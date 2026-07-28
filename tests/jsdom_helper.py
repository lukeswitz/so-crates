#!/usr/bin/env python3
"""Helper for running JavaScript tests in a JSDOM environment.

This module provides a way to execute socrates.js functions in a Node.js/JSDOM
context from Python unit tests, enabling behavioral testing instead of
brittle string-grep tests.
"""

import json
import os
import subprocess
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
HTML_PATH = os.path.join(PROJECT_ROOT, 'socrates.html')
JS_PATH = os.path.join(PROJECT_ROOT, 'static', 'socrates.js')
CSS_PATH = os.path.join(PROJECT_ROOT, 'static', 'socrates.css')
D3_PATH = os.path.join(PROJECT_ROOT, 'static', 'd3.min.js')
D3_SANKEY_PATH = os.path.join(PROJECT_ROOT, 'static', 'd3-sankey.min.js')
NODE_MODULES = os.path.join(PROJECT_ROOT, 'node_modules')


def load_files():
    """Load HTML, JS, and CSS content."""
    with open(HTML_PATH, 'r') as f:
        html = f.read()
    with open(JS_PATH, 'r') as f:
        js = f.read()
    with open(CSS_PATH, 'r') as f:
        css = f.read()
    return html, js, css


def load_d3():
    """Load d3 and d3-sankey source (UMD builds); d3 must eval before d3-sankey
    since d3-sankey extends the same global `d3` object d3.min.js creates."""
    with open(D3_PATH, 'r') as f:
        d3 = f.read()
    with open(D3_SANKEY_PATH, 'r') as f:
        d3_sankey = f.read()
    return d3, d3_sankey


def run_jsdom_test(js_test_code, setup_code='', with_d3=False):
    """Execute JS test code in a JSDOM environment with socrates loaded.

    Args:
        js_test_code: The JS code to evaluate. Must assign its result to window.__jsdom_result.
        setup_code: Optional JS code to run before the test.
        with_d3: If True, also load d3.min.js and d3-sankey.min.js before
            socrates.js (needed only for tests exercising renderSankeySVG).

    Returns:
        The parsed JSON result from the JS execution.

    Raises:
        RuntimeError: If the JS execution fails or returns invalid JSON.
    """
    html, js, css = load_files()
    d3_load_snippet = ''
    if with_d3:
        d3, d3_sankey = load_d3()
        d3_load_snippet = f'''
window.eval({json.dumps(d3)});
window.eval({json.dumps(d3_sankey)});
'''

    # Build the Node.js script
    node_script = f'''
const {{ JSDOM }} = require('jsdom');

const htmlContent = {json.dumps(html)};
const jsContent = {json.dumps(js)};
const cssContent = {json.dumps(css)};

const dom = new JSDOM(htmlContent, {{
    runScripts: 'dangerously',
    url: 'http://localhost:8000',
    pretendToBeVisual: true,
    resources: 'usable'
}});

const window = dom.window;
const document = window.document;

// Mock fetch before loading JS (prevents init() from failing)
window.fetch = function() {{ return Promise.resolve({{ json: () => Promise.resolve([]) }}); }};

// Inject CSS into the DOM
const styleEl = document.createElement('style');
styleEl.textContent = cssContent;
document.head.appendChild(styleEl);

// Make globals available
window.document = document;

// Optionally load d3 / d3-sankey (order matters: d3 first) before socrates.js
{d3_load_snippet}

// Run the main JS file via window.eval
window.eval(jsContent);

// Run setup code in window context if provided
{setup_code}

// Run the test code in window context and capture result. The test code is
// wrapped in an async IIFE so it may itself use `await` (many socrates.js
// functions are async - e.g. buildSection, applyFilters), and the outer
// script awaits that IIFE before reading the result, so assignments to
// window.__jsdom_result made after an awaited call are not missed.
// The test code must still assign its result to window.__jsdom_result.
(async () => {{
    try {{
        await window.eval({json.dumps('(async () => {' + js_test_code + '})()')});
    }} catch(e) {{
        window.__jsdom_result = {{__jsdom_error: e.message, __jsdom_stack: e.stack}};
    }}
    const __jsdom_result = window.__jsdom_result;
    delete window.__jsdom_result;

    // Handle undefined and other non-JSON values
    if (__jsdom_result === undefined) {{
        console.log(JSON.stringify({{__jsdom_undefined: true}}));
    }} else {{
        console.log(JSON.stringify(__jsdom_result));
    }}
}})();
'''

    env = os.environ.copy()
    env['NODE_PATH'] = NODE_MODULES

    # Write script to temp file (avoids "Argument list too long" error)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, dir=PROJECT_ROOT) as f:
        f.write(node_script)
        script_path = f.name

    try:
        result = subprocess.run(
            ['node', script_path],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env=env
        )
    finally:
        try:
            os.unlink(script_path)
        except Exception:
            pass

    if result.returncode != 0:
        raise RuntimeError(f'JSDOM test failed: {result.stderr}')

    output = result.stdout.strip()
    if not output:
        raise RuntimeError('JSDOM test returned empty output')

    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as e:
        raise RuntimeError(f'JSDOM test returned invalid JSON: {output[:200]}... Error: {e}')

    if isinstance(parsed, dict):
        if '__jsdom_error' in parsed:
            raise RuntimeError(f'JSDOM JS error: {parsed["__jsdom_error"]}')
        if '__jsdom_undefined' in parsed:
            return None

    return parsed


def js_expression(expr, setup_code='', with_d3=False):
    """Evaluate a JS expression and return the result.

    Args:
        expr: A single JS expression (no statements) that evaluates to a JSON-serializable value.
        setup_code: Optional setup JS code.
        with_d3: If True, also load d3/d3-sankey before socrates.js.

    Returns:
        The parsed JSON result.
    """
    js_code = f'window.__jsdom_result = {expr};'
    return run_jsdom_test(js_code, setup_code, with_d3=with_d3)


def js_statements(code, setup_code='', with_d3=False):
    """Execute JS statements and return the value assigned to window.__jsdom_result.

    Args:
        code: JS statements. Must assign the result to window.__jsdom_result.
        setup_code: Optional setup JS code.
        with_d3: If True, also load d3/d3-sankey before socrates.js.

    Returns:
        The parsed JSON result.
    """
    return run_jsdom_test(code, setup_code, with_d3=with_d3)
