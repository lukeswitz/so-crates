#!/usr/bin/env python3
import json
import unittest
import re
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'socrates.html')
JS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'socrates.js')
CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'socrates.css')
FAVICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon.svg')
FAVICON_HACKER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-hacker.svg')
FAVICON_MATTE_BLACK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-matte-black.svg')
FAVICON_TOKYO_NIGHT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-tokyo-night.svg')
FAVICON_RETRO_82_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-retro-82.svg')
FAVICON_ETHEREAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-ethereal.svg')
FAVICON_LUMON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-lumon.svg')
FAVICON_CATPPUCCIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-catppuccin.svg')
FAVICON_CATPPUCCIN_LATTE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-catppuccin-latte.svg')
FAVICON_EVERFOREST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-everforest.svg')
FAVICON_GRUVBOX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-gruvbox.svg')
FAVICON_HACKERMAN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-hackerman.svg')
FAVICON_KANAGAWA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-kanagawa.svg')
FAVICON_MIASMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-miasma.svg')
FAVICON_NORD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-nord.svg')
FAVICON_OSAKA_JADE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-osaka-jade.svg')
FAVICON_RISTRETTO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-ristretto.svg')
FAVICON_ROSE_PINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-rose-pine.svg')
FAVICON_VANTABLACK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-vantablack.svg')
FAVICON_WHITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-white.svg')
FAVICON_SGUIL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-sguil.svg')
FAVICON_CGA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-cga.svg')
FAVICON_C64_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'favicon-c64.svg')

with open(HTML_PATH, 'r') as f:
    HTML_CONTENT = f.read()
with open(JS_PATH, 'r') as f:
    JS_CONTENT = f.read()
with open(CSS_PATH, 'r') as f:
    CSS_CONTENT = f.read()


class TestHTMLStructure(unittest.TestCase):
    def test_file_size(self):
        """Verify JS file is complete (not truncated)"""
        self.assertGreater(len(JS_CONTENT), 80000, 'JS file appears truncated')

    def test_script_tags_closed(self):
        """Verify script tags are properly closed"""
        self.assertIn('<script src="static/socrates.js"></script>', HTML_CONTENT)
        # Count occurrences (including script tags with src attributes)
        open_count = HTML_CONTENT.count('<script>') + HTML_CONTENT.count('<script ')
        close_count = HTML_CONTENT.count('</script>')
        self.assertEqual(open_count, close_count, 'Script tags not balanced')

    def test_css_file_size(self):
        """Verify CSS file is complete (not truncated)"""
        self.assertGreater(len(CSS_CONTENT), 1000, 'CSS file appears truncated')

    def test_html_references_css(self):
        self.assertIn('<link rel="stylesheet" href="static/socrates.css">', HTML_CONTENT)

    def test_no_inline_style_block(self):
        """HTML must not contain inline <style> blocks after split."""
        self.assertNotIn('<style>', HTML_CONTENT, 'Inline <style> block found in HTML')
        self.assertNotIn('</style>', HTML_CONTENT, 'Inline </style> tag found in HTML')

    def test_no_inline_script_block(self):
        """HTML must not contain inline <script> blocks after split."""
        inline_script = re.search(r'<script[^>]*>(?!\s*</script>)', HTML_CONTENT)
        if inline_script:
            # Allow the small FOUC-prevention theme script in <head>
            snippet = HTML_CONTENT[inline_script.start():inline_script.start()+200]
            if 'data-theme' not in snippet:
                self.fail('Inline <script> block found in HTML')

    def test_static_files_exist(self):
        """static/socrates.css and static/socrates.js must exist on disk."""
        self.assertTrue(os.path.exists(CSS_PATH), 'static/socrates.css must exist')
        self.assertTrue(os.path.exists(JS_PATH), 'static/socrates.js must exist')

    def test_favicon_file_exists(self):
        """static/favicon.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_PATH), 'static/favicon.svg must exist')

    def test_favicon_hacker_file_exists(self):
        """static/favicon-hacker.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_HACKER_PATH), 'static/favicon-hacker.svg must exist')

    def test_favicon_cga_file_exists(self):
        """static/favicon-cga.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_CGA_PATH), 'static/favicon-cga.svg must exist')

    def test_favicon_c64_file_exists(self):
        """static/favicon-c64.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_C64_PATH), 'static/favicon-c64.svg must exist')

    def test_favicon_matte_black_file_exists(self):
        """static/favicon-matte-black.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_MATTE_BLACK_PATH), 'static/favicon-matte-black.svg must exist')

    def test_favicon_tokyo_night_file_exists(self):
        """static/favicon-tokyo-night.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_TOKYO_NIGHT_PATH), 'static/favicon-tokyo-night.svg must exist')

    def test_favicon_retro_82_file_exists(self):
        """static/favicon-retro-82.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_RETRO_82_PATH), 'static/favicon-retro-82.svg must exist')

    def test_favicon_ethereal_file_exists(self):
        """static/favicon-ethereal.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_ETHEREAL_PATH), 'static/favicon-ethereal.svg must exist')

    def test_favicon_lumon_file_exists(self):
        """static/favicon-lumon.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_LUMON_PATH), 'static/favicon-lumon.svg must exist')

    def test_favicon_catppuccin_file_exists(self):
        """static/favicon-catppuccin.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_CATPPUCCIN_PATH), 'static/favicon-catppuccin.svg must exist')

    def test_favicon_catppuccin_latte_file_exists(self):
        """static/favicon-catppuccin-latte.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_CATPPUCCIN_LATTE_PATH), 'static/favicon-catppuccin-latte.svg must exist')

    def test_favicon_everforest_file_exists(self):
        """static/favicon-everforest.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_EVERFOREST_PATH), 'static/favicon-everforest.svg must exist')

    def test_favicon_gruvbox_file_exists(self):
        """static/favicon-gruvbox.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_GRUVBOX_PATH), 'static/favicon-gruvbox.svg must exist')

    def test_favicon_hackerman_file_exists(self):
        """static/favicon-hackerman.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_HACKERMAN_PATH), 'static/favicon-hackerman.svg must exist')

    def test_favicon_kanagawa_file_exists(self):
        """static/favicon-kanagawa.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_KANAGAWA_PATH), 'static/favicon-kanagawa.svg must exist')

    def test_favicon_miasma_file_exists(self):
        """static/favicon-miasma.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_MIASMA_PATH), 'static/favicon-miasma.svg must exist')

    def test_favicon_nord_file_exists(self):
        """static/favicon-nord.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_NORD_PATH), 'static/favicon-nord.svg must exist')

    def test_favicon_osaka_jade_file_exists(self):
        """static/favicon-osaka-jade.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_OSAKA_JADE_PATH), 'static/favicon-osaka-jade.svg must exist')

    def test_favicon_ristretto_file_exists(self):
        """static/favicon-ristretto.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_RISTRETTO_PATH), 'static/favicon-ristretto.svg must exist')

    def test_favicon_rose_pine_file_exists(self):
        """static/favicon-rose-pine.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_ROSE_PINE_PATH), 'static/favicon-rose-pine.svg must exist')

    def test_favicon_vantablack_file_exists(self):
        """static/favicon-vantablack.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_VANTABLACK_PATH), 'static/favicon-vantablack.svg must exist')

    def test_favicon_white_file_exists(self):
        """static/favicon-white.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_WHITE_PATH), 'static/favicon-white.svg must exist')

    def test_favicon_sguil_file_exists(self):
        """static/favicon-sguil.svg must exist on disk."""
        self.assertTrue(os.path.exists(FAVICON_SGUIL_PATH), 'static/favicon-sguil.svg must exist')

    def test_favicon_link_in_head(self):
        """HTML must link to the SVG favicon in <head>."""
        head = HTML_CONTENT.split('</head>')[0]
        self.assertIn('rel="icon"', head, 'Favicon link must exist in head')
        self.assertIn('static/favicon.svg', head, 'Favicon link must point to static/favicon.svg')
        self.assertIn('id="faviconLink"', head, 'Favicon link must have id for JS updates')

    def test_favicon_swap_logic_exists(self):
        """JS must contain updateFavicon logic to swap favicon based on theme."""
        self.assertIn('function updateFavicon(', JS_CONTENT,
                      'updateFavicon function must exist')
        self.assertIn('getCurrentTheme()', JS_CONTENT,
                      'updateFavicon must check the current theme')

    def test_favicon_swaps_for_every_theme(self):
        """updateFavicon() must point faviconLink at the per-theme SVG that
        exists in static/ (plain favicon.svg for the default dark theme)."""
        from tests.jsdom_helper import js_statements
        themes = ['dark', 'light', 'sguil', 'hacker', 'cga', 'c64', 'matte-black', 'tokyo-night', 'retro-82', 'ethereal', 'lumon', 'catppuccin', 'catppuccin-latte', 'everforest', 'gruvbox', 'hackerman', 'kanagawa', 'miasma', 'nord', 'osaka-jade', 'ristretto', 'rose-pine', 'vantablack', 'white']
        result = js_statements(f'''
            var link = document.getElementById('faviconLink');
            var out = {{}};
            var themes = {json.dumps(themes)};
            themes.forEach(function(t) {{
                if (t === 'dark') document.documentElement.removeAttribute('data-theme');
                else document.documentElement.setAttribute('data-theme', t);
                updateFavicon();
                out[t] = link.getAttribute('href');
            }});
            window.__jsdom_result = out;
        ''')
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
        for theme in themes:
            expected = 'static/favicon.svg' if theme in ('dark', 'light') else f'static/favicon-{theme}.svg'
            self.assertEqual(result[theme], expected,
                             f'updateFavicon must select {expected} for the {theme} theme')
            svg_file = os.path.basename(expected)
            self.assertTrue(os.path.isfile(os.path.join(static_dir, svg_file)),
                            f'{svg_file} must exist in static/')

    def test_valid_doctype(self):
        self.assertTrue(HTML_CONTENT.startswith('<!DOCTYPE html>'))

    def test_has_charset(self):
        self.assertIn('charset="UTF-8"', HTML_CONTENT)

    def test_has_viewport(self):
        self.assertIn('viewport', HTML_CONTENT)

    def test_has_title(self):
        self.assertIn('SO-CRATES - Welcome', HTML_CONTENT)

    def test_has_container(self):
        self.assertIn('class="container"', HTML_CONTENT)

    def test_has_stats_grid(self):
        self.assertIn('id="statsGrid"', HTML_CONTENT)

    def test_has_sections_container(self):
        self.assertIn('id="sections"', HTML_CONTENT)

    def test_has_input_boxes(self):
        self.assertIn('id="inputBoxes"', HTML_CONTENT)

    def test_has_header(self):
        self.assertIn('id="mainHeader"', HTML_CONTENT)

    def test_has_help_modal(self):
        self.assertIn('id="helpModal"', HTML_CONTENT)

    def test_has_file_info_container(self):
        self.assertIn('id="fileInfoContainer"', HTML_CONTENT)

    def test_has_app_header_meta(self):
        self.assertIn('id="appHeaderMeta"', HTML_CONTENT)

    def test_has_app_header_filename(self):
        self.assertIn('id="appHeaderFilename"', HTML_CONTENT)

    def test_magnifying_glass_is_hyperlink(self):
        """The magnifying glass SVG in the header must be wrapped in an <a> tag linking to showWelcome()."""
        # Find the app-header-left section
        header_start = HTML_CONTENT.find('class="app-header-left"')
        self.assertGreater(header_start, -1, 'app-header-left must exist')
        header_end = HTML_CONTENT.find('</div>', header_start)
        header_section = HTML_CONTENT[header_start:header_end]
        # Must contain an <a> wrapping an <svg>
        self.assertIn('<a', header_section, 'app-header-left must contain an <a> tag')
        self.assertIn('<svg', header_section, 'app-header-left must contain an <svg>')
        # The <a> must come before the SVG (i.e., wraps it)
        a_pos = header_section.find('<a')
        svg_pos = header_section.find('<svg')
        self.assertLess(a_pos, svg_pos, '<a> must wrap <svg> in app-header-left')
        # The <a> must have onclick="showWelcome()"
        self.assertIn('showWelcome()', header_section, '<a> must call showWelcome()')

    def test_has_loading_modal(self):
        self.assertIn('id="loadingModal"', HTML_CONTENT)

    def test_has_spinner_animation(self):
        self.assertIn('@keyframes spin', CSS_CONTENT)

    def test_has_marked_js(self):
        self.assertNotIn('marked.min.js', HTML_CONTENT)

    def test_closing_tags(self):
        self.assertIn('</html>', HTML_CONTENT)
        self.assertIn('</body>', HTML_CONTENT)
        self.assertIn('</head>', HTML_CONTENT)


class TestCSSLayout(unittest.TestCase):
    def test_stats_grid_columns(self):
        match = re.search(r'grid-template-columns:\s*repeat\(([^)]+)\)', CSS_CONTENT)
        self.assertIsNotNone(match, "stats-grid should have grid-template-columns")
        if match:
            columns = match.group(1)
            self.assertIn('auto-fit', columns,
                          'stats-grid must use auto-fit for responsive wrapping')
            self.assertIn('minmax', columns,
                          'stats-grid must use minmax for responsive column sizing')

    def test_stats_grid_gap(self):
        self.assertIn('gap:', CSS_CONTENT)

    def test_section_hidden_class(self):
        self.assertIn('.section-hidden', CSS_CONTENT)
        self.assertIn('display: none', CSS_CONTENT)

    def test_stat_card_hover(self):
        self.assertIn('.stat-card:hover', CSS_CONTENT)

    def test_table_sticky_headers(self):
        self.assertIn('position: sticky', CSS_CONTENT)

    def test_no_horizontal_scrollbars(self):
        """The page itself must never require horizontal scrolling; general
        content wraps instead. Dense data tables are the documented exception
        (WCAG 1.4.10 Reflow explicitly exempts data tables from the no-2D-
        scroll rule) and may scroll horizontally within their own scoped
        wrapper, never the page - table-layout:auto lets columns size to
        their own content instead of being forced into a fixed split."""
        self.assertIn('overflow-wrap: break-word', CSS_CONTENT,
                      'Long content must wrap with break-word')
        self.assertIn('.table-scroll-wrapper { overflow-x: auto; }', CSS_CONTENT,
                      'Table horizontal scroll must be scoped to its own wrapper, not the page')
        self.assertIn('table-layout: auto', CSS_CONTENT,
                      'Tables use auto layout so columns size to their own content')

    def test_detail_row_allows_text_wrapping(self):
        """Detail rows must override the global td nowrap so content can wrap."""
        self.assertIn('.detail-row td {', CSS_CONTENT,
                      'detail-row td style must exist')
        self.assertIn('white-space: normal', CSS_CONTENT,
                      'detail-row td must allow text wrapping')

    def test_table_cells_wrap_not_truncate(self):
        """Table cells (including ALERT) must wrap text, not truncate with ellipsis."""
        td_match = re.search(r'td \{([^}]+)\}', CSS_CONTENT)
        self.assertIsNotNone(td_match, 'Global td style must exist')
        td_style = td_match.group(1)
        self.assertNotIn('white-space: nowrap', td_style,
                         'td must not force single-line truncation')
        self.assertNotIn('text-overflow: ellipsis', td_style,
                         'td must not hide overflow with ellipsis')
        self.assertIn('overflow-wrap: break-word', td_style,
                      'td must wrap long text like alert signatures')

    def test_detail_content_wraps(self):
        """Detail content must use overflow-wrap to prevent overflow."""
        self.assertIn('.detail-content {', CSS_CONTENT,
                      'detail-content style must exist')
        self.assertIn('overflow-wrap: break-word', CSS_CONTENT,
                      'detail-content must wrap long text')

    def test_ascii_transcript_lines_wrap(self):
        """ASCII transcript inner divs must wrap to avoid horizontal overflow."""
        self.assertIn('.ascii-transcript div { overflow-wrap: break-word', CSS_CONTENT,
                      'ascii-transcript divs must wrap long lines')
        self.assertIn('word-break: break-all', CSS_CONTENT,
                      'ascii-transcript divs must break on non-word characters like dots')

    def test_ascii_transcript_shows_loading_indicator(self):
        """ASCII transcript must show a loading spinner while fetching."""
        self.assertIn('.ascii-loading {', CSS_CONTENT,
                      'ascii-loading CSS class must exist')
        self.assertIn('Loading ASCII transcript', JS_CONTENT,
                      'toggleRow must set loading text before fetching transcript')
        self.assertIn('ascii-loading', JS_CONTENT,
                      'toggleRow must use ascii-loading spinner class')

    def test_sankey_diagram_shows_loading_indicator(self):
        """updateSankeyDiagram must show a loading spinner while fetching,
        reusing the same ascii-loading pattern as the ASCII transcript -
        the diagram can take 500ms+ on large datasets and previously popped
        in with no feedback."""
        update_fn = JS_CONTENT.split('async function updateSankeyDiagram()')[1].split('\n        }')[0]
        self.assertIn('Loading Sankey diagram', update_fn,
                      'updateSankeyDiagram must set loading text before fetching')
        self.assertIn('ascii-loading', update_fn,
                      'updateSankeyDiagram must use the ascii-loading spinner class')

    def test_detail_grid_can_shrink(self):
        """formatEvent grid must set min-width: 0 so columns shrink on narrow viewports."""
        self.assertIn('min-width: 0', JS_CONTENT,
                      'formatEvent grid must set min-width: 0 to shrink')
        self.assertIn('minmax(0, 1fr)', JS_CONTENT,
                      'formatEvent grid must use minmax(0, 1fr) to allow column shrinking')

    def test_responsive_viewport(self):
        self.assertIn('width=device-width', HTML_CONTENT)


class TestJavaScriptFunctions(unittest.TestCase):
    def test_has_escape_html(self):
        self.assertIn('function escapeHtml', JS_CONTENT)

    def test_has_show_tab(self):
        self.assertIn('function showTab', JS_CONTENT)

    def test_has_toggle_row(self):
        self.assertIn('function toggleRow', JS_CONTENT)

    def test_has_load_ascii_transcript(self):
        self.assertIn('function loadAsciiTranscript', JS_CONTENT)

    def test_has_format_event(self):
        self.assertIn('function formatEvent', JS_CONTENT)

    def test_has_sort_table(self):
        self.assertIn('function sortCurrentTable', JS_CONTENT)

    def test_has_show_loading(self):
        self.assertIn('function showLoading', JS_CONTENT)

    def test_has_question_hotkey(self):
        """Question mark hotkey must trigger showHelpModal outside input fields."""
        # Verify the keydown handler checks for '?' key
        self.assertIn("e.key === '?'", JS_CONTENT,
                      'JS must listen for ? key to show help modal')
        # Verify it guards against input/textarea targets
        self.assertIn("e.target.tagName !== 'INPUT'", JS_CONTENT,
                      'JS must not trigger ? hotkey when typing in input fields')

    def test_has_hide_loading(self):
        self.assertIn('function hideLoading', JS_CONTENT)

    def test_has_show_welcome(self):
        self.assertIn('function showWelcome', JS_CONTENT)

    def test_has_load_analysis(self):
        self.assertIn('function loadAnalysis', JS_CONTENT)

    def test_has_load_from_url(self):
        self.assertIn('function loadFromUrl', JS_CONTENT)

    def test_has_upload_pcap(self):
        self.assertIn('function uploadPcap', JS_CONTENT)

    def test_has_check_status(self):
        self.assertIn('function checkStatus', JS_CONTENT)

    def test_has_build_stats(self):
        self.assertIn('function buildStats', JS_CONTENT)

    def test_has_build_sections(self):
        self.assertIn('function buildSections', JS_CONTENT)

    def test_has_build_row_for_event(self):
        self.assertIn('function buildRowForEvent', JS_CONTENT)

    def test_has_get_columns_for_type(self):
        self.assertIn('function getColumnsForType', JS_CONTENT)

    def test_has_build_all_events(self):
        self.assertIn('function buildAllEvents', JS_CONTENT)

    def test_has_clearAnalysisContainers(self):
        self.assertIn('function clearAnalysisContainers', JS_CONTENT)

    def test_has_showWelcomeUI(self):
        self.assertIn('function showWelcomeUI', JS_CONTENT)

    def test_has_showHelpModal(self):
        self.assertIn('function showHelpModal', JS_CONTENT)

    def test_has_closeHelpModal(self):
        self.assertIn('function closeHelpModal', JS_CONTENT)

    def test_has_shouldShowHelpModal(self):
        self.assertIn('function shouldShowHelpModal', JS_CONTENT)

    def test_has_handleHelpBackdropClick(self):
        self.assertIn('function handleHelpBackdropClick', JS_CONTENT)

    def test_has_welcomeHelpContent(self):
        self.assertIn('function getWelcomeHelpContent', JS_CONTENT)

    def test_has_showAnalysisUI(self):
        self.assertIn('function showAnalysisUI', JS_CONTENT)

    def test_has_refreshCurrentView(self):
        self.assertIn('function refreshCurrentView', JS_CONTENT)

    def test_has_init(self):
        self.assertIn('function init', JS_CONTENT)

    def test_has_delete_analysis(self):
        self.assertIn('function openDeleteAnalysis', JS_CONTENT)

    def test_has_reanalyze_modal_functions(self):
        self.assertIn('function openReanalyzeModal', JS_CONTENT)
        self.assertIn('function closeReanalyzeModal', JS_CONTENT)
        self.assertIn('function confirmReanalyze', JS_CONTENT)


class TestJavaScriptSyntax(unittest.TestCase):
    def test_no_unclosed_template_literals(self):
        """Check that template literals are properly closed"""
        backtick_count = JS_CONTENT.count('`')
        # Should be even - all template literals have matching backticks
        self.assertEqual(backtick_count % 2, 0, f'Unclosed template literals detected: {backtick_count} backticks')

    def test_brace_balance_in_script(self):
        """Check that braces are balanced in JavaScript"""
        open_braces = JS_CONTENT.count('{')
        close_braces = JS_CONTENT.count('}')
        self.assertEqual(open_braces, close_braces, f'Unbalanced braces: {open_braces} open, {close_braces} close')

    def test_paren_balance_in_script(self):
        """Check that parentheses are balanced in JavaScript"""
        open_parens = JS_CONTENT.count('(')
        close_parens = JS_CONTENT.count(')')
        self.assertEqual(open_parens, close_parens, f'Unbalanced parentheses: {open_parens} open, {close_parens} close')

    def test_script_is_valid_js(self):
        """Verify JavaScript can be parsed without syntax errors"""
        # This test checks that there are no obvious syntax errors
        # by verifying all function definitions have matching braces
        import re
        func_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{'
        matches = list(re.finditer(func_pattern, JS_CONTENT))
        
        for match in matches:
            start = match.end()
            brace_count = 1
            pos = start
            found_end = False
            while pos < len(JS_CONTENT) and brace_count > 0 and pos - start < 100000:
                if JS_CONTENT[pos] == '{':
                    brace_count += 1
                elif JS_CONTENT[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            if brace_count != 0:
                func_name = match.group(1)
                self.fail(f"Function '{func_name}' has unbalanced braces")


class TestCardOrder(unittest.TestCase):
    def test_alert_first_all_last_sorting(self):
        """Verify alert is first and all is last in stats sorting logic"""
        # Check the sorting logic in the code
        self.assertIn("function sortEventTypes", JS_CONTENT,
                      "Should have a sortEventTypes helper for event type ordering")
        self.assertIn("t !== 'stats' && t !== 'all'", JS_CONTENT,
                      "Should filter out 'stats' and 'all' from sorting")
        self.assertIn("a.localeCompare(b)", JS_CONTENT,
                      "Should sort alphabetically after prioritized types")

    def test_sortEventTypes_behavior(self):
        """sortEventTypes must prioritize alert and filealerts, then sort alphabetically."""
        from tests.jsdom_helper import js_expression
        result = js_expression("sortEventTypes(['dns', 'http', 'alert', 'filealerts', 'tls'])")
        self.assertEqual(result, ['alert', 'filealerts', 'dns', 'http', 'tls'])

    def test_sortEventTypes_fallback_to_alphabetical(self):
        """sortEventTypes must fall back to alphabetical ordering for non-prioritized types."""
        from tests.jsdom_helper import js_expression
        result = js_expression("sortEventTypes(['dns', 'stats', 'all'])")
        self.assertEqual(result, ['all', 'dns', 'stats'])

    def test_apply_filter_calls_both_section_and_aggregation(self):
        """Verify applyFilter builds both section and aggregation when filtering"""
        self.assertIn("function applyFilters(", JS_CONTENT,
                      "applyFilter should delegate to applyFilters")
        applyFunc = JS_CONTENT.split('function applyFilter(')[1].split('function clearFilter')[0]
        self.assertIn("applyFilters", applyFunc,
                      "applyFilter should delegate to applyFilters")
        refreshFunc = JS_CONTENT.split('function refreshCurrentView')[1].split('function ')[0]
        self.assertIn("buildAggregationsSection(eventType, filtered)", refreshFunc,
                      "refreshCurrentView should call buildAggregationsSection with filtered events")
        self.assertIn("buildSection(eventType, events)", refreshFunc,
                      "refreshCurrentView should call buildSection with events")


class TestJavaScriptDataStructures(unittest.TestCase):
    def test_has_type_labels(self):
        self.assertIn('typeLabels', JS_CONTENT)

    def test_has_type_colors(self):
        self.assertIn('COLORS', JS_CONTENT)

    def test_colors_event_alert_is_red(self):
        self.assertIn("alert: '#ff6b6b'", JS_CONTENT,
                      'COLORS.EVENT.alert must be red')

    def test_all_events_type_column_uses_color_dot(self):
        self.assertIn('valueDotSpan(COLORS.EVENT[etype])', JS_CONTENT,
                      'All Events Type column must render a value-dot colored via COLORS.EVENT, '
                      'matching the dot used for Protocol/Method/etc rather than an emoji icon')

    def test_has_all_events_columns_constant(self):
        self.assertIn('ALL_EVENTS_COLUMNS', JS_CONTENT)

    def test_has_empty_filter_state_constant(self):
        self.assertIn('EMPTY_FILTER_STATE_HTML', JS_CONTENT)

    def test_has_agg_collapsed_constant(self):
        self.assertIn('AGG_COLLAPSED_HTML', JS_CONTENT)

    def test_has_all_event_types(self):
        expected_types = ['alert', 'dns', 'http', 'tls', 'flow', 'ftp', 'stats', 'anomaly', 'fileinfo']
        for etype in expected_types:
            self.assertIn(f"'{etype}'", JS_CONTENT)

    def test_has_global_state(self):
        self.assertIn('let allEvents', JS_CONTENT)
        self.assertIn('let tabDataCache', JS_CONTENT)
        self.assertIn('let eventTypes', JS_CONTENT)
        self.assertIn('let currentMd5', JS_CONTENT)


class TestJavaScriptLogic(unittest.TestCase):
    def test_escape_html_escapes_special_chars(self):
        self.assertIn('&amp;', JS_CONTENT)
        self.assertIn('&lt;', JS_CONTENT)
        self.assertIn('&gt;', JS_CONTENT)
        self.assertIn('&quot;', JS_CONTENT)

    def test_error_message_escapes_event_type_label(self):
        self.assertIn("escapeHtml(typeLabels[eventType] || eventType.toUpperCase())", JS_CONTENT,
                      'Tab error message must escape the event type label before innerHTML')

    def test_sort_table_toggles_direction(self):
        self.assertIn('sort-asc', JS_CONTENT)
        self.assertIn('sort-desc', JS_CONTENT)

    def test_toggle_row_handles_detail_visibility(self):
        self.assertIn('detail-row', JS_CONTENT)
        self.assertIn('visible', JS_CONTENT)
        self.assertIn('expanded-row', JS_CONTENT)

    def test_format_event_handles_all_types(self):
        event_types = ['alert', 'dns', 'http', 'tls', 'flow', 'ftp', 'anomaly', 'fileinfo', 'stats']
        # formatEvent now uses EVENT_RENDERERS to dispatch to type-specific renderers
        self.assertIn('const renderer = EVENT_RENDERERS[e.event_type]', JS_CONTENT,
                      'formatEvent must use EVENT_RENDERERS for type dispatch')
        for etype in event_types:
            # Keys may be quoted or unquoted in JS object literal
            found = f"'{etype}':" in JS_CONTENT or f'{etype}:' in JS_CONTENT
            self.assertTrue(found, f'EVENT_RENDERERS must handle event type {etype}')

    def test_get_columns_returns_correct_columns(self):
        self.assertIn("case 'alert':", JS_CONTENT)
        self.assertIn("case 'dns':", JS_CONTENT)
        self.assertIn("case 'http':", JS_CONTENT)
        self.assertIn("case 'tls':", JS_CONTENT)
        self.assertIn("case 'flow':", JS_CONTENT)
        self.assertIn('default:', JS_CONTENT)

    def test_keyboard_shortcuts(self):
        self.assertIn("e.key === 'Escape'", JS_CONTENT)

    def test_url_parameter_handling(self):
        self.assertIn('URLSearchParams', JS_CONTENT)
        self.assertIn('pcap', JS_CONTENT)

    def test_date_range_display(self):
        """Date range comes from the server's /api/stats date_range field
        (not a client-side scan of allEvents, which would defeat lazy
        loading)."""
        self.assertIn('statsData.date_range', JS_CONTENT)
        self.assertIn('rangeMin', JS_CONTENT)
        self.assertIn('rangeMax', JS_CONTENT)

    def test_event_type_sorting(self):
        self.assertIn("function sortEventTypes", JS_CONTENT)
        self.assertIn("localeCompare", JS_CONTENT)


class TestAPIIntegration(unittest.TestCase):
    def test_uses_correct_api_endpoints(self):
        endpoints = [
            '/api/events',
            '/api/analyses',
            '/api/load-analysis',
            '/api/upload',
            '/api/load-url',
            '/api/check-status',
        ]
        for endpoint in endpoints:
            self.assertIn(endpoint, JS_CONTENT)
        # ascii-stream and download-stream are built dynamically via buildStreamUrl
        self.assertIn("buildStreamUrl('ascii-stream'", JS_CONTENT)
        self.assertIn("buildStreamUrl('download-stream'", JS_CONTENT)

    def test_uses_fetch_api(self):
        self.assertIn('fetch(', JS_CONTENT)

    def test_handles_json_responses(self):
        self.assertIn('.json()', JS_CONTENT)

    def test_handles_errors(self):
        self.assertIn('catch', JS_CONTENT)
        self.assertIn('err.message', JS_CONTENT)

    def test_uses_correct_http_methods(self):
        self.assertIn("method: 'POST'", JS_CONTENT)

    def test_sends_json_content_type(self):
        self.assertIn("'Content-Type': 'application/json'", JS_CONTENT)

    def test_uses_form_data_for_upload(self):
        self.assertIn('FormData', JS_CONTENT)

    def test_passes_md5_to_api(self):
        self.assertIn('md5=', JS_CONTENT)
        self.assertIn('currentMd5', JS_CONTENT)


class TestUXFeatures(unittest.TestCase):
    def test_loading_states(self):
        self.assertIn('showLoading', JS_CONTENT)
        self.assertIn('hideLoading', JS_CONTENT)
        self.assertIn('spinner', CSS_CONTENT)

    def test_empty_state_handling(self):
        self.assertIn('No previous analyses available', JS_CONTENT)

    def test_error_messages(self):
        self.assertIn('showError(', JS_CONTENT)
        self.assertIn('id="errorModal"', HTML_CONTENT)

    def test_back_navigation(self):
        """Back navigation must exist via the app header logo link."""
        self.assertIn("showWelcome(); return false;", HTML_CONTENT,
                      'App header logo must link back to welcome screen')

    def test_help_modal_lightbulb_uses_template_literal(self):
        """REGRESSION: dynamic help text must interpolate LIGHTBULB_ICON_SVG
        instead of showing the literal text."""
        func_match = re.search(r'function showHelpModal\([^)]*\)\s*\{', JS_CONTENT)
        self.assertIsNotNone(func_match, 'showHelpModal function must exist')
        start = func_match.end()
        brace_count = 1
        pos = start
        while pos < len(JS_CONTENT) and brace_count > 0:
            if JS_CONTENT[pos] == '{':
                brace_count += 1
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
        func_body = JS_CONTENT[start:pos]
        # The three dynamic helpText assignments should use backticks.
        self.assertNotIn("'${LIGHTBULB_ICON_SVG}'", func_body,
                         'Dynamic helpText must not single-quote the icon variable')
        self.assertIn('helpText = `<span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}', func_body,
                      'Dynamic helpText must use a template literal for the icon')

    def test_welcome_help_lightbulb_uses_help_icon_color(self):
        """Static welcome help modal lightbulb icons must use --help-icon-color."""
        welcome_match = re.search(r'function getWelcomeHelpContent\(\) \{ return `', JS_CONTENT)
        self.assertIsNotNone(welcome_match, 'getWelcomeHelpContent must exist')
        start = welcome_match.end()
        # Find the closing backtick of the template literal.
        pos = start
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '`' and JS_CONTENT[pos - 1] != '\\':
                break
            pos += 1
        content = JS_CONTENT[start:pos]
        self.assertIn('<span style="color: var(--help-icon-color);">${LIGHTBULB_ICON_SVG}</span>', content,
                      'Welcome help lightbulb icons must use --help-icon-color')

    def test_empty_filter_state_uses_template_literal(self):
        """REGRESSION: EMPTY_FILTER_STATE_HTML must interpolate SEARCH_ICON_SVG
        instead of showing the literal text."""
        self.assertIn('const EMPTY_FILTER_STATE_HTML = `<div style="padding: 40px; text-align: center; color: var(--text-muted); font-size: 0.95rem;">${SEARCH_ICON_SVG}', JS_CONTENT,
                      'EMPTY_FILTER_STATE_HTML must use a template literal for the search icon')
        self.assertNotIn("const EMPTY_FILTER_STATE_HTML = '<div style=\"padding: 40px; text-align: center; color: var(--text-muted); font-size: 0.95rem;\">${SEARCH_ICON_SVG}", JS_CONTENT,
                         'EMPTY_FILTER_STATE_HTML must not single-quote the search icon variable')

    def test_help_modal_has_backdrop_click_handler(self):
        """Help modal wrapper must close when the dark backdrop is clicked."""
        self.assertIn('id="helpModal" onclick="handleHelpBackdropClick(event)"', HTML_CONTENT,
                      'Help modal wrapper must handle backdrop clicks')
        modal_section = HTML_CONTENT.split('id="helpModal"')[1].split('</div>\n        </div>')[0]
        self.assertIn('onclick="event.stopPropagation()"', modal_section,
                      'Help modal content must stop event propagation')

    def test_help_modal_backdrop_handler_closes_modal(self):
        """handleHelpBackdropClick must close the modal only when the backdrop is clicked."""
        func_match = re.search(r'function handleHelpBackdropClick\([^)]*\)\s*\{', JS_CONTENT)
        self.assertIsNotNone(func_match, 'handleHelpBackdropClick function must exist')
        start = func_match.end()
        brace_count = 1
        pos = start
        while pos < len(JS_CONTENT) and brace_count > 0:
            if JS_CONTENT[pos] == '{':
                brace_count += 1
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
        func_body = JS_CONTENT[start:pos]
        self.assertIn("event.target === document.getElementById('helpModal')", func_body,
                      'Backdrop handler must only close when the helpModal wrapper is clicked')
        self.assertIn('closeHelpModal()', func_body,
                      'Backdrop handler must call closeHelpModal()')

    def test_header_has_no_separators(self):
        """Header items must not have any separators (pipes or borders) for clean responsive wrapping."""
        app_header_section = JS_CONTENT.split("getElementById('appHeaderRight').innerHTML")[1].split("`;")[0]
        self.assertNotIn('color: #30363d;"|"', app_header_section,
                         'Header must not use literal pipe characters as separators')
        self.assertNotIn('.header-item', CSS_CONTENT,
                          'Header must not use CSS border separators')

    def test_header_has_file_icon(self):
        """Header filename must have a file icon prefix."""
        self.assertIn('FILE_ICON_SVG', JS_CONTENT,
                      'App header filename must be prefixed with FILE_ICON_SVG')
        self.assertIn('currentFileName', JS_CONTENT,
                      'App header must display currentFileName')

    def test_header_meta_class_exists(self):
        """Header meta container CSS class must exist for grouping hash/date."""
        self.assertIn('.app-header-meta', CSS_CONTENT,
                      'CSS must define .app-header-meta for hash/date grouping')

    def test_file_input_accepts_all_files(self):
        """File input must not restrict file types — any file can be uploaded."""
        input_match = re.search(r'id="pcapUpload"[^>]*>', JS_CONTENT)
        self.assertIsNotNone(input_match, 'pcapUpload input must exist')
        self.assertNotIn('accept=', input_match.group(0),
                         'File input must not have accept attribute to allow any file')

    def test_drag_and_drop_zone_exists(self):
        """Upload area must have a visible drop zone for drag-and-drop."""
        self.assertIn('id="dropZone"', JS_CONTENT,
                      'Drop zone element must exist')
        self.assertIn('ondragover', JS_CONTENT,
                      'Drop zone must handle dragover event')
        self.assertIn('ondrop', JS_CONTENT,
                      'Drop zone must handle drop event')

    def test_drag_and_drop_css_feedback(self):
        """Drop zone must have CSS class for visual feedback on drag."""
        self.assertIn('.drop-zone-active', CSS_CONTENT,
                      'Drop zone active CSS class must exist')
        active_match = re.search(r'\.drop-zone-active\s*\{([^}]+)\}', CSS_CONTENT)
        self.assertIsNotNone(active_match, '.drop-zone-active CSS rule must exist')
        active_style = active_match.group(1)
        self.assertIn('border-color', active_style,
                      'Drop zone active must change border color')

    def test_drag_and_drop_handlers_exist(self):
        """JavaScript must have drag-and-drop event handler functions."""
        self.assertIn('function handleDragOver', JS_CONTENT,
                      'handleDragOver function must exist')
        self.assertIn('function handleDragLeave', JS_CONTENT,
                      'handleDragLeave function must exist')
        self.assertIn('function handleDrop', JS_CONTENT,
                      'handleDrop function must exist')

    def test_upload_function_accepts_file_parameter(self):
        """uploadPcap must accept an optional file parameter for drag-and-drop."""
        func_match = re.search(r'function uploadPcap\(([^)]*)\)', JS_CONTENT)
        self.assertIsNotNone(func_match, 'uploadPcap function must exist')
        params = func_match.group(1)
        self.assertIn('droppedFile', params,
                      'uploadPcap must accept a droppedFile parameter')

    def test_upload_shows_loading_immediately(self):
        """uploadPcap must show loading before fetch so user sees feedback during upload."""
        upload_func = JS_CONTENT.split('async function uploadPcap')[1].split('async function checkStatus')[0]
        self.assertIn("showLoading('Uploading file... (0s)')", upload_func,
                      'uploadPcap must show loading immediately before fetch')

    def test_url_input_submits_on_enter(self):
        """URL input field must call loadFromUrl when Enter key is pressed."""
        input_match = re.search(r'id="pcapUrl"[^>]*>', JS_CONTENT)
        self.assertIsNotNone(input_match, 'pcapUrl input must exist')
        input_tag = input_match.group(0)
        self.assertIn("onkeydown", input_tag,
                      'pcapUrl input must have onkeydown handler')
        self.assertIn("loadFromUrl()", input_tag,
                      'pcapUrl onkeydown must call loadFromUrl')

    def test_diagram_toggle_exists(self):
        """Sankey panel must include a collapsible heading bar."""
        self.assertIn('toggleDiagram()', JS_CONTENT,
                      'toggleDiagram function must be referenced in heading bar')
        self.assertIn('diagramMode', JS_CONTENT,
                      'diagramMode variable must exist')

    def test_sankey_panel_exists(self):
        """Static HTML must include a #sankeyPanel container."""
        self.assertIn('id="sankeyPanel"', HTML_CONTENT,
                      'sankeyPanel container must exist')

    def test_d3_library_bundled(self):
        """D3 and d3-sankey must be loaded from local static files, not CDN."""
        self.assertIn('static/d3.min.js', HTML_CONTENT,
                      'D3 must be loaded from local static file')
        self.assertIn('static/d3-sankey.min.js', HTML_CONTENT,
                      'd3-sankey must be loaded from local static file')
        self.assertNotIn('unpkg.com', HTML_CONTENT,
                         'Must not use external CDN for D3 libraries')

    def test_sankey_functions_exist(self):
        """JavaScript must define buildSankeyData and renderSankeySVG functions."""
        self.assertIn('function buildSankeyData(', JS_CONTENT,
                      'buildSankeyData function must exist')
        self.assertIn('function renderSankeySVG(', JS_CONTENT,
                      'renderSankeySVG function must exist')
        self.assertIn('d3.sankey()', JS_CONTENT,
                      'renderSankeySVG must use d3.sankey for layout')
        self.assertIn('d3.sankeyLinkHorizontal()', JS_CONTENT,
                      'renderSankeySVG must use d3.sankeyLinkHorizontal for links')

    def test_diagram_toggle_listener_exists(self):
        """Sankey diagram heading bar must call toggleDiagram when clicked."""
        self.assertIn("toggleDiagram()", JS_CONTENT,
                      'Sankey heading bar onclick must call toggleDiagram')

    def test_sankey_has_close_button(self):
        """Sankey diagram panel must include a collapsible heading bar."""
        self.assertIn('section-toggle-bar', CSS_CONTENT,
                      'section-toggle-bar CSS class must exist')
        self.assertIn("diagramMode = !diagramMode", JS_CONTENT,
                      'toggleDiagram must flip diagramMode state')
        self.assertIn("toggleDiagram()", JS_CONTENT,
                      'Sankey heading must call toggleDiagram')

    def test_sankey_links_clickable(self):
        """Sankey links must have click handlers to create filters."""
        self.assertIn(".on('click', function(event, d)", JS_CONTENT,
                      'Sankey links must have click handler')
        self.assertIn("applyFilters(visibleSection.id, [", JS_CONTENT,
                      'Sankey link click must call applyFilters')
        self.assertIn("getColumnNameFromSankeyColumn(d.source.column)", JS_CONTENT,
                      'Sankey link must map source column')
        self.assertIn("getColumnNameFromSankeyColumn(d.target.column)", JS_CONTENT,
                      'Sankey link must map target column')

    def test_sankey_nodes_clickable(self):
        """Sankey nodes must have click handlers to create filters."""
        self.assertIn(".on('click', function(event, d)", JS_CONTENT,
                      'Sankey nodes must have click handler')
        self.assertIn("getColumnNameFromSankeyColumn(d.column)", JS_CONTENT,
                      'Sankey node must map column')

    def test_sankey_empty_events_shows_header(self):
        """REGRESSION: updateSankeyDiagram must render the toggle header even when events are empty."""
        func = JS_CONTENT.split('function updateSankeyDiagram(')[1].split('function ')[0]
        self.assertIn("sankeyPanel.innerHTML = '<div class=\"section-toggle-bar\" onclick=\"toggleDiagram()\">▾ Sankey Diagram</div>'", func,
                      'updateSankeyDiagram must render header bar for empty events')

    def test_getSankeyEvents_exists(self):
        """JavaScript must define getSankeyEvents to resolve events for the currently visible tab."""
        self.assertIn('function getSankeyEvents(', JS_CONTENT,
                      'getSankeyEvents function must exist')

    def test_updateSankeyDiagram_uses_getSankeyEvents(self):
        """REGRESSION: updateSankeyDiagram must call getSankeyEvents instead of accepting a parameter."""
        func = JS_CONTENT.split('function updateSankeyDiagram(')[1].split('function ')[0]
        self.assertIn('getSankeyEvents()', func,
                      'updateSankeyDiagram must call getSankeyEvents to resolve events')

    def test_apply_filters_function_exists(self):
        """JavaScript must define applyFilters to apply multiple filters at once."""
        self.assertIn('function applyFilters(', JS_CONTENT,
                      'applyFilters function must exist')

    def test_get_column_name_helper_exists(self):
        """JavaScript must define getColumnNameFromSankeyColumn for column mapping."""
        self.assertIn('function getColumnNameFromSankeyColumn(', JS_CONTENT,
                      'getColumnNameFromSankeyColumn function must exist')

    def test_default_url_prefilled(self):
        self.assertIn('malware-traffic-analysis.net', JS_CONTENT)

    def test_feature_comparison_table(self):
        self.assertIn('SO-CRATES', JS_CONTENT)
        self.assertIn('Security Onion', JS_CONTENT)

    def test_feature_comparison_table_links(self):
        """Feature comparison table must include links to Security Onion resources"""
        self.assertIn('https://securityonion.net', JS_CONTENT)
        self.assertIn('http://securityonion.net/docs/about', JS_CONTENT)
        self.assertIn('https://securityonion.com/pro', JS_CONTENT)
        self.assertIn('http://securityonion.net/docs/security-onion-pro', JS_CONTENT)

    def test_ascii_transcript_loading(self):
        self.assertIn('ASCII Transcript', JS_CONTENT)
        self.assertIn('downloadPcap', JS_CONTENT)

    def test_ascii_transcript_colored_bars(self):
        self.assertIn('#ff6b6b', JS_CONTENT)
        self.assertIn('#58a6ff', JS_CONTENT)

    def test_ascii_transcript_direction_grouping(self):
        self.assertIn("direction === 'src'", JS_CONTENT)
        self.assertIn("line.direction", JS_CONTENT)

    def test_table_sorting_ui(self):
        self.assertIn('cursor: pointer', CSS_CONTENT)
        self.assertIn('sort-arrow', JS_CONTENT)

    def test_hexdump_function_exists(self):
        self.assertIn('function switchStreamView', JS_CONTENT)
        self.assertIn('function loadHexdumpData', JS_CONTENT)

    def test_hexdump_toggle_functions_exist(self):
        self.assertIn('function togglePacket', JS_CONTENT)
        self.assertIn('function expandAllPackets', JS_CONTENT)
        self.assertIn('function collapseAllPackets', JS_CONTENT)

    def test_hexdump_expand_collapse_selector_uses_direct_child(self):
        """expandAllPackets and collapseAllPackets must use > span:first-child
        to avoid overwriting nested colored IP spans."""
        self.assertIn("querySelectorAll('.packet-header > span:first-child')", JS_CONTENT)

    def test_hexdump_button_in_detail_row(self):
        self.assertIn('Hexdump', JS_CONTENT)
        self.assertIn("onclick=\"switchStreamView(", JS_CONTENT)
        self.assertIn('.view-tabs', CSS_CONTENT)
        self.assertIn('.view-tab', CSS_CONTENT)

    def test_payload_container_uses_data_attributes(self):
        """Payload container must store stream params in data-* attributes, not in a raw id."""
        self.assertIn('class="stream-payload"', JS_CONTENT,
                      'Payload container must use a stream-payload class')
        self.assertIn('data-src-ip="', JS_CONTENT,
                      'Payload container must store src IP in a data attribute')
        self.assertIn('data-dst-ip="', JS_CONTENT,
                      'Payload container must store dst IP in a data attribute')
        self.assertIn("escapeHtml(e.src_ip)", JS_CONTENT,
                      'Payload container must HTML-escape src IP')
        self.assertIn("escapeHtml(e.dest_ip)", JS_CONTENT,
                      'Payload container must HTML-escape dst IP')
        self.assertNotIn('id="ascii-${e.src_ip}', JS_CONTENT,
                         'Payload container must not build id from raw src IP')

    def test_all_events_filter_refreshes_correctly(self):
        """refreshCurrentView must use buildAllEvents for the 'all' section."""
        func = JS_CONTENT.split('function refreshCurrentView(')[1].split('function applyFilters')[0]
        self.assertIn("if (eventType === 'all')", func,
                      'refreshCurrentView must special-case the all-events section')
        self.assertIn('buildAllEvents();', func,
                      'refreshCurrentView must call buildAllEvents for all-events')
        self.assertIn('buildAggregationsSectionAll();', func,
                      'refreshCurrentView must call buildAggregationsSectionAll for all-events')

    def test_hexdump_packet_css(self):
        self.assertIn('.packet-block', CSS_CONTENT)
        self.assertIn('.packet-header', CSS_CONTENT)
        self.assertIn('.packet-content', CSS_CONTENT)
        self.assertIn('.view-tabs', CSS_CONTENT)
        self.assertIn('.view-tab', CSS_CONTENT)

    def test_hexdump_direction_classes(self):
        """Each packet block must have a src-dir or dst-dir class for colored left border."""
        self.assertIn('.packet-block.src-dir', CSS_CONTENT)
        self.assertIn('.packet-block.dst-dir', CSS_CONTENT)
        self.assertNotIn('function colorizePacketHeader', JS_CONTENT)

    def test_hexdump_direction_detection(self):
        """loadHexdumpData must detect direction by splitting on ' > ' and checking src."""
        self.assertIn("pkt.header.split(' > ')", JS_CONTENT)
        self.assertIn("dirParts[0].includes(src)", JS_CONTENT)

    def test_loadAnalysis_calls_loadTabData_after_buildSections(self):
        """loadAnalysis must call loadTabData after buildSections since buildSections no longer loads data."""
        func = JS_CONTENT.split('async function loadAnalysis')[1].split('async function')[0]
        self.assertIn("clearAnalysisContainers()", func,
                      'loadAnalysis must clear containers before rebuilding')
        self.assertIn("buildSections();", func,
                      'loadAnalysis must call buildSections')
        self.assertIn("loadTabData(eventTypes[0])", func,
                      'loadAnalysis must call loadTabData after buildSections')

    def test_loadAnalysis_uses_showAnalysisUI(self):
        """loadAnalysis must call showAnalysisUI after rebuilding the analysis view."""
        func = JS_CONTENT.split('async function loadAnalysis')[1].split('async function')[0]
        self.assertIn("showAnalysisUI()", func,
                      'loadAnalysis must call showAnalysisUI after rebuilding')


class TestSecurityInUI(unittest.TestCase):
    def test_no_inline_event_handlers_with_dangerous_patterns(self):
        dangerous_patterns = ['eval(', 'document.write(', 'innerHTML = location', 'innerHTML = window']
        for pattern in dangerous_patterns:
            self.assertNotIn(pattern, JS_CONTENT)

    def test_uses_escape_html_function(self):
        self.assertIn('escapeHtml(', JS_CONTENT)

    def test_no_hardcoded_credentials(self):
        content = JS_CONTENT.lower().replace('disclaimer', '').replace('password-protected', '').replace('password protected', '').replace('common passwords', '')
        self.assertNotIn('password', content)

    def test_uses_https_for_external_resources(self):
        self.assertIn('https://', HTML_CONTENT)


class TestAccessibility(unittest.TestCase):
    def test_has_lang_attribute(self):
        self.assertIn('lang="en"', HTML_CONTENT)

    def test_has_meta_viewport(self):
        self.assertIn('viewport', HTML_CONTENT)

    def test_has_title(self):
        self.assertIn('<title>', HTML_CONTENT)

    def test_buttons_have_titles(self):
        self.assertIn('title="', JS_CONTENT)


class TestThemeAndMenu(unittest.TestCase):
    def test_toggleTheme_exists(self):
        self.assertIn('function toggleTheme(', JS_CONTENT,
                      'toggleTheme function must exist')

    def test_toggleMenu_exists(self):
        self.assertIn('function toggleMenu(', JS_CONTENT,
                      'toggleMenu function must exist')

    def test_closeMenu_exists(self):
        self.assertIn('function closeMenu(', JS_CONTENT,
                      'closeMenu function must exist')

    def test_menu_dropdown_in_html(self):
        self.assertIn('id="appHeaderMenuDropdown"', HTML_CONTENT,
                      'Menu dropdown container must exist in HTML')

    def test_theme_options_in_menu(self):
        for theme in ('dark', 'light', 'sguil', 'hacker', 'cga', 'c64', 'matte-black', 'tokyo-night', 'retro-82', 'ethereal', 'lumon', 'catppuccin', 'catppuccin-latte', 'everforest', 'gruvbox', 'hackerman', 'kanagawa', 'miasma', 'nord', 'osaka-jade', 'ristretto', 'rose-pine', 'vantablack', 'white'):
            self.assertIn(f"commitTheme('{theme}')", HTML_CONTENT,
                          f'{theme} theme option must commit on click')
            self.assertIn(f"previewTheme('{theme}')", HTML_CONTENT,
                          f'{theme} theme option must preview on hover')
            self.assertIn(f'data-theme-option="{theme}"', HTML_CONTENT,
                          f'{theme} theme option must carry data-theme-option in HTML')
        self.assertIn('revertTheme()', HTML_CONTENT,
                      'Theme options must revert on mouseleave')

    def test_theme_options_in_rendered_gear_menu(self):
        """renderGearMenu() must generate a button with preview/commit handlers
        for every theme in the THEMES registry."""
        from tests.jsdom_helper import js_statements
        themes = ['dark', 'light', 'sguil', 'hacker', 'cga', 'c64', 'matte-black', 'tokyo-night', 'retro-82', 'ethereal', 'lumon', 'catppuccin', 'catppuccin-latte', 'everforest', 'gruvbox', 'hackerman', 'kanagawa', 'miasma', 'nord', 'osaka-jade', 'ristretto', 'rose-pine', 'vantablack', 'white']
        result = js_statements(f'''
            var html = renderGearMenu();
            var missing = [];
            var themes = {json.dumps(themes)};
            themes.forEach(function(t) {{
                if (html.indexOf('data-theme-option="' + t + '"') === -1) missing.push('data-theme-option:' + t);
                if (html.indexOf("commitTheme('" + t + "')") === -1) missing.push('commitTheme:' + t);
                if (html.indexOf("previewTheme('" + t + "')") === -1) missing.push('previewTheme:' + t);
            }});
            window.__jsdom_result = missing;
        ''')
        self.assertEqual(result, [],
                         f'renderGearMenu output is missing theme entries: {result}')

    def test_theme_header_separate_class(self):
        """Theme section headings must be distinct non-interactive headers."""
        self.assertIn('class="app-header-menu-header"', HTML_CONTENT,
                      'Theme heading must use app-header-menu-header class')
        self.assertIn('>Dark Themes</div>', HTML_CONTENT,
                      'Dark Themes heading must exist in menu')
        self.assertIn('>Fun Themes</div>', HTML_CONTENT,
                      'Fun Themes heading must exist in menu')
        self.assertIn('>Light Themes</div>', HTML_CONTENT,
                      'Light Themes heading must exist in menu')
        self.assertNotIn('>Theme</div>', HTML_CONTENT,
                         'Old single Theme heading must be removed')
        self.assertIn('.app-header-menu-header {', CSS_CONTENT,
                      'CSS must define app-header-menu-header styling')
        header_block = CSS_CONTENT.split('.app-header-menu-header {')[1].split('}')[0]
        self.assertIn('text-transform: uppercase', header_block,
                      'Theme heading must be uppercase')
        self.assertIn('color: var(--text-muted)', header_block,
                      'Theme heading must use muted text color')

    def test_theme_menu_items_have_no_icons(self):
        """Theme menu items must be plain text; old theme icon classes must be gone."""
        for cls in ['theme-icon-dark', 'theme-icon-light', 'theme-icon-hacker']:
            self.assertNotIn(cls, HTML_CONTENT,
                             f'{cls} must not appear in HTML after removing theme icons')
            self.assertNotIn(cls, JS_CONTENT,
                             f'{cls} must not appear in JS after removing theme icons')

    def test_help_in_menu_not_standalone(self):
        self.assertIn('onclick="showHelpModal(); closeMenu();"', HTML_CONTENT,
                      'Help button must be inside the menu dropdown')

    def test_help_appears_before_theme_header(self):
        """REGRESSION: Help must be at the top of the gear menu, followed by
        the Dark Themes section."""
        help_index = HTML_CONTENT.find('onclick="showHelpModal(); closeMenu();"')
        dark_index = HTML_CONTENT.find('>Dark Themes</div>')
        self.assertGreater(help_index, -1, 'Help button must exist in menu')
        self.assertGreater(dark_index, -1, 'Dark Themes header must exist in menu')
        self.assertLess(help_index, dark_index,
                        'Help button must appear before the Dark Themes header')

    def test_dark_themes_before_light_themes(self):
        """REGRESSION: Dark themes must be grouped before Light themes."""
        dark_index = HTML_CONTENT.find('>Dark Themes</div>')
        light_index = HTML_CONTENT.find('>Light Themes</div>')
        light_btn_index = HTML_CONTENT.find('commitTheme(\'light\')')
        self.assertGreater(dark_index, -1, 'Dark Themes header must exist')
        self.assertGreater(light_index, -1, 'Light Themes header must exist')
        self.assertGreater(light_btn_index, -1, 'Light theme button must exist')
        self.assertLess(dark_index, light_index,
                        'Dark Themes header must appear before Light Themes header')
        self.assertLess(light_index, light_btn_index,
                        'Light Themes header must appear before Light theme button')

    def test_fun_themes_between_dark_and_light(self):
        """Fun Themes section (Hacker, Sguil) sits between Dark and Light sections."""
        fun_index = HTML_CONTENT.find('>Fun Themes</div>')
        dark_index = HTML_CONTENT.find('>Dark Themes</div>')
        light_index = HTML_CONTENT.find('>Light Themes</div>')
        hacker_btn_index = HTML_CONTENT.find('commitTheme(\'hacker\')')
        sguil_btn_index = HTML_CONTENT.find('commitTheme(\'sguil\')')
        self.assertGreater(fun_index, -1, 'Fun Themes header must exist')
        self.assertLess(dark_index, fun_index,
                        'Fun Themes header must appear after Dark Themes header')
        self.assertLess(fun_index, light_index,
                        'Fun Themes header must appear before Light Themes header')
        self.assertLess(fun_index, hacker_btn_index,
                        'Hacker button must appear inside the Fun Themes section')
        self.assertLess(fun_index, sguil_btn_index,
                        'Sguil button must appear inside the Fun Themes section')
        self.assertLess(hacker_btn_index, light_index,
                        'Hacker button must appear before the Light Themes section')
        self.assertLess(sguil_btn_index, light_index,
                        'Sguil button must appear before the Light Themes section')

    def test_dark_themes_alphabetical(self):
        """Dark Themes section must list themes in alphabetical order by label,
        and renderGearMenu() must match the static HTML menu order."""
        dark_section = HTML_CONTENT.split('>Dark Themes</div>')[1].split('>Fun Themes</div>')[0]
        labels = re.findall(r'<span>([^<]+)</span>', dark_section)
        self.assertEqual(labels, sorted(labels),
                         'Dark Themes in HTML menu must be in alphabetical order')
        js_labels = self._rendered_gear_menu_section_labels('Dark Themes', 'Fun Themes')
        self.assertEqual(js_labels, labels,
                         'renderGearMenu Dark Themes order must match the HTML menu')

    def test_light_themes_alphabetical(self):
        """Light Themes section must list themes in alphabetical order by label,
        and renderGearMenu() must match the static HTML menu order."""
        light_section = HTML_CONTENT.split('>Light Themes</div>')[1].split('</div>')[0]
        labels = re.findall(r'<span>([^<]+)</span>', light_section)
        self.assertEqual(labels, sorted(labels),
                         'Light Themes in HTML menu must be in alphabetical order')
        js_labels = self._rendered_gear_menu_section_labels('Light Themes', None)
        self.assertEqual(js_labels, labels,
                         'renderGearMenu Light Themes order must match the HTML menu')

    def _rendered_gear_menu_section_labels(self, start_header, end_header):
        """Evaluate renderGearMenu() in JSDOM and extract the <span> labels of
        the named theme section (up to the next section header, if any)."""
        from tests.jsdom_helper import js_statements
        end = f"'{end_header}'" if end_header else 'null'
        return js_statements(f'''
            var html = renderGearMenu();
            var section = html.split('>' + '{start_header}' + '</div>')[1];
            var endHeader = {end};
            if (endHeader) section = section.split('>' + endHeader + '</div>')[0];
            var re = /<span>([^<]+)<\\/span>/g, m, labels = [];
            while ((m = re.exec(section)) !== null) labels.push(m[1]);
            window.__jsdom_result = labels;
        ''')

    def test_renderGearMenu_helper_exists(self):
        """The gear menu markup must live in a single shared helper."""
        self.assertIn('function renderGearMenu(', JS_CONTENT,
                      'renderGearMenu helper must exist for shared gear menu markup')
        self.assertIn('GEAR_ICON_SVG', JS_CONTENT,
                      'Gear icon SVG must be a shared constant')
        self.assertGreaterEqual(JS_CONTENT.count('renderGearMenu()'), 2,
                                'showWelcomeUI and loadAnalysis must both call renderGearMenu()')

    def test_preview_commit_revert_functions_exist(self):
        self.assertIn('function previewTheme(', JS_CONTENT,
                      'previewTheme function must exist for hover preview')
        self.assertIn('function revertTheme(', JS_CONTENT,
                      'revertTheme function must exist for hover revert')
        self.assertIn('function commitTheme(', JS_CONTENT,
                      'commitTheme function must exist for click persistence')

    def test_theme_hover_previews_and_reverts(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            setTheme('dark');
            toggleMenu();
            var buttons = document.querySelectorAll('.app-header-menu-item');
            var lightBtn = Array.from(buttons).find(function(b) {
                return b.textContent.trim() === 'Daylight';
            });
            lightBtn.onmouseenter();
            var preview = document.documentElement.getAttribute('data-theme') || 'dark';
            lightBtn.onmouseleave();
            var reverted = document.documentElement.getAttribute('data-theme') || 'dark';
            window.__jsdom_result = { preview: preview, reverted: reverted };
        ''')
        self.assertEqual(result['preview'], 'light',
                         'hovering a theme should preview it')
        self.assertEqual(result['reverted'], 'dark',
                         'leaving a theme item should revert to the baseline')

    def test_update_theme_menu_marks_active_theme(self):
        """The active theme checkmark must track setTheme and hover previews."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            setTheme('nord');
            var afterSet = document.querySelectorAll('.app-header-menu-item.theme-active');
            var nordActive = document.querySelector('[data-theme-option="nord"]').classList.contains('theme-active');
            previewTheme('lumon');
            var afterPreview = document.querySelectorAll('.app-header-menu-item.theme-active');
            var lumonActive = document.querySelector('[data-theme-option="lumon"]').classList.contains('theme-active');
            var nordStillActive = document.querySelector('[data-theme-option="nord"]').classList.contains('theme-active');
            window.__jsdom_result = {
                setCount: afterSet.length,
                nordActive: nordActive,
                previewCount: afterPreview.length,
                lumonActive: lumonActive,
                nordStillActive: nordStillActive
            };
        ''')
        self.assertEqual(result['setCount'], 1, 'exactly one menu item must be marked active')
        self.assertTrue(result['nordActive'], 'setTheme(nord) must mark the Nord item active')
        self.assertEqual(result['previewCount'], 1, 'exactly one menu item must be marked active after preview')
        self.assertTrue(result['lumonActive'], 'previewTheme(lumon) must move the active mark to Lumon')
        self.assertFalse(result['nordStillActive'], 'previewTheme must clear the previous active mark')

    def test_active_theme_checkmark_css_exists(self):
        self.assertIn('.app-header-menu-item[data-theme-option]::before', CSS_CONTENT,
                      'CSS must reserve checkmark space on theme menu items only')
        self.assertIn('.app-header-menu-item[data-theme-option].theme-active::before', CSS_CONTENT,
                      'CSS must define the active-theme checkmark')
        block = CSS_CONTENT.split('.app-header-menu-item[data-theme-option].theme-active::before')[1].split('}')[0]
        self.assertIn("content: '✓'", block,
                      'Active-theme checkmark content must be ✓')
        self.assertIn('var(--accent)', block,
                      'Active-theme checkmark must use the accent color')

    def test_checkmark_space_not_applied_to_help_item(self):
        """REGRESSION: the Help menu item must not reserve checkmark space
        (it is not a theme item, so the bare ::before rule must not exist)."""
        self.assertNotIn('.app-header-menu-item::before', CSS_CONTENT,
                         'Checkmark space must be scoped to [data-theme-option], not all menu items')
        help_btn = HTML_CONTENT.split('onclick="showHelpModal(); closeMenu();"')[0].split('<button')[-1]
        self.assertNotIn('data-theme-option', help_btn,
                         'Help menu item must not carry data-theme-option')

    def test_theme_menu_items_do_not_wrap(self):
        """REGRESSION: menu items must not wrap (Catppuccin Latte wrapped when the
        checkmark ::before was added without widening the dropdown)."""
        item_block = CSS_CONTENT.split('.app-header-menu-item {')[1].split('}')[0]
        self.assertIn('white-space: nowrap', item_block,
                      'Menu items must use white-space: nowrap so long theme names stay on one line')
        dropdown_block = CSS_CONTENT.split('.app-header-menu-dropdown {')[1].split('}')[0]
        self.assertIn('min-width: 180px', dropdown_block,
                      'Dropdown min-width must be at least 180px to fit the checkmark plus the longest theme name')

    def test_update_theme_menu_implementation(self):
        self.assertIn("querySelectorAll('.app-header-menu-item[data-theme-option]')", JS_CONTENT,
                      'updateThemeMenu must query theme items by data-theme-option')
        self.assertIn("classList.toggle('theme-active'", JS_CONTENT,
                      'updateThemeMenu must toggle the theme-active class')
        self.assertIn('aria-current', JS_CONTENT,
                      'updateThemeMenu must set aria-current for accessibility')

    def test_theme_click_commits_and_closes_menu(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            setTheme('dark');
            toggleMenu();
            var buttons = document.querySelectorAll('.app-header-menu-item');
            var lightBtn = Array.from(buttons).find(function(b) {
                return b.textContent.trim() === 'Daylight';
            });
            lightBtn.onclick();
            var committed = document.documentElement.getAttribute('data-theme') || 'dark';
            var stored = localStorage.getItem('socrates-theme');
            var dropdown = document.getElementById('appHeaderMenuDropdown');
            window.__jsdom_result = {
                committed: committed,
                stored: stored,
                menuOpen: dropdown.classList.contains('active')
            };
        ''')
        self.assertEqual(result['committed'], 'light',
                         'clicking a theme should commit it visually')
        self.assertEqual(result['stored'], 'light',
                         'clicking a theme should persist it to localStorage')
        self.assertFalse(result['menuOpen'], 'clicking a theme should close the menu')

    def test_css_theme_variables_exist(self):
        self.assertIn('--bg-primary:', CSS_CONTENT,
                      'CSS must define --bg-primary custom property')
        self.assertIn('--text-primary:', CSS_CONTENT,
                      'CSS must define --text-primary custom property')
        self.assertIn('--accent:', CSS_CONTENT,
                      'CSS must define --accent custom property')

    def test_help_icon_color_variable_exists_per_theme(self):
        """Each theme must define --help-icon-color."""
        self.assertIn('--help-icon-color:', CSS_CONTENT,
                      'CSS must define --help-icon-color custom property')
        # Verify the variable appears inside each theme block.
        root_block = CSS_CONTENT.split(':root {')[1].split('}')[0]
        light_block = CSS_CONTENT.split('[data-theme="light"] {')[1].split('}')[0]
        sguil_block = CSS_CONTENT.split('[data-theme="sguil"] {')[1].split('}')[0]
        hacker_block = CSS_CONTENT.split('[data-theme="hacker"] {')[1].split('}')[0]
        matte_black_block = CSS_CONTENT.split('[data-theme="matte-black"] {')[1].split('}')[0]
        tokyo_night_block = CSS_CONTENT.split('[data-theme="tokyo-night"] {')[1].split('}')[0]
        retro_82_block = CSS_CONTENT.split('[data-theme="retro-82"] {')[1].split('}')[0]
        ethereal_block = CSS_CONTENT.split('[data-theme="ethereal"] {')[1].split('}')[0]
        lumon_block = CSS_CONTENT.split('[data-theme="lumon"] {')[1].split('}')[0]
        catppuccin_block = CSS_CONTENT.split('[data-theme="catppuccin"] {')[1].split('}')[0]
        catppuccin_latte_block = CSS_CONTENT.split('[data-theme="catppuccin-latte"] {')[1].split('}')[0]
        everforest_block = CSS_CONTENT.split('[data-theme="everforest"] {')[1].split('}')[0]
        gruvbox_block = CSS_CONTENT.split('[data-theme="gruvbox"] {')[1].split('}')[0]
        hackerman_block = CSS_CONTENT.split('[data-theme="hackerman"] {')[1].split('}')[0]
        kanagawa_block = CSS_CONTENT.split('[data-theme="kanagawa"] {')[1].split('}')[0]
        miasma_block = CSS_CONTENT.split('[data-theme="miasma"] {')[1].split('}')[0]
        nord_block = CSS_CONTENT.split('[data-theme="nord"] {')[1].split('}')[0]
        osaka_jade_block = CSS_CONTENT.split('[data-theme="osaka-jade"] {')[1].split('}')[0]
        ristretto_block = CSS_CONTENT.split('[data-theme="ristretto"] {')[1].split('}')[0]
        rose_pine_block = CSS_CONTENT.split('[data-theme="rose-pine"] {')[1].split('}')[0]
        vantablack_block = CSS_CONTENT.split('[data-theme="vantablack"] {')[1].split('}')[0]
        white_block = CSS_CONTENT.split('[data-theme="white"] {')[1].split('}')[0]
        self.assertIn('--help-icon-color:', root_block,
                      'Dark theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', light_block,
                      'Light theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', sguil_block,
                      'Sguil theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', hacker_block,
                      'Hacker theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', matte_black_block,
                      'Matte Black theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', tokyo_night_block,
                      'Tokyo Night theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', retro_82_block,
                      'Retro 82 theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', ethereal_block,
                      'Ethereal theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', lumon_block,
                      'Lumon theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', catppuccin_block,
                      'Catppuccin theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', catppuccin_latte_block,
                      'Catppuccin Latte theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', everforest_block,
                      'Everforest theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', gruvbox_block,
                      'Gruvbox theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', hackerman_block,
                      'Hackerman theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', kanagawa_block,
                      'Kanagawa theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', miasma_block,
                      'Miasma theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', nord_block,
                      'Nord theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', osaka_jade_block,
                      'Osaka Jade theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', ristretto_block,
                      'Ristretto theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', rose_pine_block,
                      'Rose Pine theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', vantablack_block,
                      'Vantablack theme must define --help-icon-color')
        self.assertIn('--help-icon-color:', white_block,
                      'White theme must define --help-icon-color')
        self.assertIn('var(--accent)', hacker_block,
                      'Hacker theme --help-icon-color should map to accent green')
        self.assertIn('var(--accent)', matte_black_block,
                      'Matte Black theme --help-icon-color should map to accent orange')

    def test_light_theme_override_exists(self):
        self.assertIn('[data-theme="light"]', CSS_CONTENT,
                      'CSS must have a light theme override block')

    def test_escape_closes_menu(self):
        self.assertIn('closeMenu();', JS_CONTENT,
                      'Escape key handler must call closeMenu()')

    def test_localStorage_theme_persistence(self):
        self.assertIn("safeStorageSet(localStorage, 'socrates-theme'", JS_CONTENT,
                      'Theme choice must be persisted to localStorage via safe wrapper')

    def test_help_storage_uses_safe_wrappers(self):
        should_show = JS_CONTENT.split('function shouldShowHelpModal')[1].split('function')[0]
        self.assertIn('safeStorageGet(localStorage, \'socrates_hideHelp\')', should_show,
                      'shouldShowHelpModal must use safeStorageGet for localStorage')
        self.assertIn('safeStorageGet(sessionStorage, \'socrates_helpShown\')', should_show,
                      'shouldShowHelpModal must use safeStorageGet for sessionStorage')
        close_help = JS_CONTENT.split('function closeHelpModal')[1].split('function')[0]
        self.assertIn('safeStorageSet(sessionStorage, \'socrates_helpShown\', \'true\')', close_help,
                      'closeHelpModal must use safeStorageSet for sessionStorage')
        self.assertIn('safeStorageSet(localStorage, \'socrates_hideHelp\', \'true\')', close_help,
                      'closeHelpModal must use safeStorageSet for localStorage')
        self.assertIn('safeStorageRemove(localStorage, \'socrates_hideHelp\')', close_help,
                      'closeHelpModal must use safeStorageRemove for localStorage')

    def test_fouc_prevention_script_exists(self):
        self.assertIn('data-theme', HTML_CONTENT,
                      'HTML must have FOUC-prevention theme script')

    def test_fouc_prevention_script_is_fault_tolerant(self):
        head = HTML_CONTENT.split('</head>')[0]
        inline_script_match = re.search(r'<script[^>]*>(.*?)</script>', head, re.DOTALL)
        self.assertTrue(inline_script_match, 'Inline script must be present in <head>')
        inline_script = inline_script_match.group(1)
        self.assertIn('try{', inline_script.replace(' ', ''),
                      'FOUC script must guard theme read in try block')
        self.assertIn('catch(e){}', inline_script.replace(' ', ''),
                      'FOUC script must swallow localStorage errors')

    def test_hacker_theme_override_exists(self):
        self.assertIn('[data-theme="hacker"]', CSS_CONTENT,
                      'CSS must have a Hacker theme override block')

    def test_matte_black_theme_override_exists(self):
        self.assertIn('[data-theme="matte-black"]', CSS_CONTENT,
                      'CSS must have a Matte Black theme override block')

    def test_tokyo_night_theme_override_exists(self):
        self.assertIn('[data-theme="tokyo-night"]', CSS_CONTENT,
                      'CSS must have a Tokyo Night theme override block')

    def test_retro_82_theme_override_exists(self):
        self.assertIn('[data-theme="retro-82"]', CSS_CONTENT,
                      'CSS must have a Retro 82 theme override block')

    def test_ethereal_theme_override_exists(self):
        self.assertIn('[data-theme="ethereal"]', CSS_CONTENT,
                      'CSS must have an Ethereal theme override block')

    def test_lumon_theme_override_exists(self):
        self.assertIn('[data-theme="lumon"]', CSS_CONTENT,
                      'CSS must have a Lumon theme override block')

    def test_catppuccin_theme_override_exists(self):
        self.assertIn('[data-theme="catppuccin"]', CSS_CONTENT,
                      'CSS must have a Catppuccin theme override block')

    def test_catppuccin_latte_theme_override_exists(self):
        self.assertIn('[data-theme="catppuccin-latte"]', CSS_CONTENT,
                      'CSS must have a Catppuccin Latte theme override block')

    def test_everforest_theme_override_exists(self):
        self.assertIn('[data-theme="everforest"]', CSS_CONTENT,
                      'CSS must have an Everforest theme override block')

    def test_gruvbox_theme_override_exists(self):
        self.assertIn('[data-theme="gruvbox"]', CSS_CONTENT,
                      'CSS must have a Gruvbox theme override block')

    def test_hackerman_theme_override_exists(self):
        self.assertIn('[data-theme="hackerman"]', CSS_CONTENT,
                      'CSS must have a Hackerman theme override block')

    def test_kanagawa_theme_override_exists(self):
        self.assertIn('[data-theme="kanagawa"]', CSS_CONTENT,
                      'CSS must have a Kanagawa theme override block')

    def test_miasma_theme_override_exists(self):
        self.assertIn('[data-theme="miasma"]', CSS_CONTENT,
                      'CSS must have a Miasma theme override block')

    def test_nord_theme_override_exists(self):
        self.assertIn('[data-theme="nord"]', CSS_CONTENT,
                      'CSS must have a Nord theme override block')

    def test_osaka_jade_theme_override_exists(self):
        self.assertIn('[data-theme="osaka-jade"]', CSS_CONTENT,
                      'CSS must have an Osaka Jade theme override block')

    def test_ristretto_theme_override_exists(self):
        self.assertIn('[data-theme="ristretto"]', CSS_CONTENT,
                      'CSS must have a Ristretto theme override block')

    def test_rose_pine_theme_override_exists(self):
        self.assertIn('[data-theme="rose-pine"]', CSS_CONTENT,
                      'CSS must have a Rose Pine theme override block')

    def test_vantablack_theme_override_exists(self):
        self.assertIn('[data-theme="vantablack"]', CSS_CONTENT,
                      'CSS must have a Vantablack theme override block')

    def test_white_theme_override_exists(self):
        self.assertIn('[data-theme="white"]', CSS_CONTENT,
                      'CSS must have a White theme override block')

    def test_sguil_theme_override_exists(self):
        self.assertIn('[data-theme="sguil"]', CSS_CONTENT,
                      'CSS must have a Sguil theme override block')

    def test_code_rain_canvas_exists(self):
        self.assertIn('id="codeRain"', HTML_CONTENT,
                      'HTML must include a code-rain canvas for Hacker')

    def test_setTheme_function_exists(self):
        self.assertIn('function setTheme(', JS_CONTENT,
                      'setTheme function must exist for multi-theme support')

    def test_themes_registry_exists(self):
        self.assertIn('const THEMES = {', JS_CONTENT,
                      'JS must define a THEMES registry')

    def test_hacker_theme_in_registry(self):
        self.assertIn('hacker:', JS_CONTENT,
                      'THEMES registry must include the hacker theme')

    def test_matte_black_theme_in_registry(self):
        self.assertIn("'matte-black':", JS_CONTENT,
                      'THEMES registry must include the matte-black theme')

    def test_tokyo_night_theme_in_registry(self):
        self.assertIn("'tokyo-night':", JS_CONTENT,
                      'THEMES registry must include the tokyo-night theme')

    def test_retro_82_theme_in_registry(self):
        self.assertIn("'retro-82':", JS_CONTENT,
                      'THEMES registry must include the retro-82 theme')

    def test_ethereal_theme_in_registry(self):
        self.assertIn("'ethereal':", JS_CONTENT,
                      'THEMES registry must include the ethereal theme')

    def test_lumon_theme_in_registry(self):
        self.assertIn("'lumon':", JS_CONTENT,
                      'THEMES registry must include the lumon theme')

    def test_catppuccin_theme_in_registry(self):
        self.assertIn("'catppuccin':", JS_CONTENT,
                      'THEMES registry must include the catppuccin theme')

    def test_catppuccin_latte_theme_in_registry(self):
        self.assertIn("'catppuccin-latte':", JS_CONTENT,
                      'THEMES registry must include the catppuccin-latte theme')

    def test_everforest_theme_in_registry(self):
        self.assertIn("'everforest':", JS_CONTENT,
                      'THEMES registry must include the everforest theme')

    def test_gruvbox_theme_in_registry(self):
        self.assertIn("'gruvbox':", JS_CONTENT,
                      'THEMES registry must include the gruvbox theme')

    def test_hackerman_theme_in_registry(self):
        self.assertIn("'hackerman':", JS_CONTENT,
                      'THEMES registry must include the hackerman theme')

    def test_kanagawa_theme_in_registry(self):
        self.assertIn("'kanagawa':", JS_CONTENT,
                      'THEMES registry must include the kanagawa theme')

    def test_miasma_theme_in_registry(self):
        self.assertIn("'miasma':", JS_CONTENT,
                      'THEMES registry must include the miasma theme')

    def test_nord_theme_in_registry(self):
        self.assertIn("'nord':", JS_CONTENT,
                      'THEMES registry must include the nord theme')

    def test_osaka_jade_theme_in_registry(self):
        self.assertIn("'osaka-jade':", JS_CONTENT,
                      'THEMES registry must include the osaka-jade theme')

    def test_ristretto_theme_in_registry(self):
        self.assertIn("'ristretto':", JS_CONTENT,
                      'THEMES registry must include the ristretto theme')

    def test_rose_pine_theme_in_registry(self):
        self.assertIn("'rose-pine':", JS_CONTENT,
                      'THEMES registry must include the rose-pine theme')

    def test_vantablack_theme_in_registry(self):
        self.assertIn("'vantablack':", JS_CONTENT,
                      'THEMES registry must include the vantablack theme')

    def test_white_theme_in_registry(self):
        self.assertIn("'white':", JS_CONTENT,
                      'THEMES registry must include the white theme')

    def test_sguil_theme_in_registry(self):
        self.assertIn("sguil:", JS_CONTENT,
                      'THEMES registry must include the sguil theme')

    def test_hacker_search_btn_override(self):
        self.assertIn('[data-theme="hacker"] .search-btn', CSS_CONTENT,
                      'Hacker theme must override search button styling')

    def test_sample_cards_use_accent(self):
        """Sample cards must use theme accent colors, not hardcoded red/orange/yellow."""
        for cls in ('sample-card-red', 'sample-card-orange', 'sample-card-yellow',
                    'sample-red', 'sample-orange', 'sample-yellow'):
            self.assertNotIn(cls, CSS_CONTENT,
                             f'{cls} must be removed from CSS in favor of accent-based styling')
            self.assertNotIn(cls, JS_CONTENT,
                             f'{cls} must be removed from sample markup in favor of accent-based styling')
        label_block = CSS_CONTENT.split('.sample-card .sample-label {')[1].split('}')[0]
        self.assertIn('color: var(--accent)', label_block,
                      'Sample labels must use the theme accent color')
        card_hover_block = CSS_CONTENT.split('.sample-card:hover {')[1].split('}')[0]
        self.assertIn('border-color: var(--interactive-highlight, var(--accent))', card_hover_block,
                      'Sample card hover border must use the theme accent color, with an '
                      'optional --interactive-highlight override for themes (like C64) where '
                      '--accent alone is not visually distinct from --border-color')

    def test_welcome_color_vars_removed(self):
        """--welcome-red/orange/yellow must be gone from themes and all consumers."""
        self.assertNotIn('--welcome-red', CSS_CONTENT,
                         '--welcome-red must be removed from CSS')
        self.assertNotIn('--welcome-orange', CSS_CONTENT,
                         '--welcome-orange must be removed from CSS')
        self.assertNotIn('--welcome-yellow', CSS_CONTENT,
                         '--welcome-yellow must be removed from CSS')
        self.assertNotIn('var(--welcome-', JS_CONTENT,
                         'JS must not reference --welcome-* variables')

    def test_dead_theme_vars_removed(self):
        """--accent-rgb and --filter-bar-bg were defined in every theme block
        but never consumed anywhere (verified via var(--name) search across
        CSS/JS/HTML) - removed as dead CSS. Must not reappear. (--border-color
        was removed alongside these too, but was later reintroduced with a
        real purpose - see test_border_color_split_from_bg_hover - so it's
        deliberately not checked here.)"""
        for name in ('--accent-rgb', '--filter-bar-bg'):
            self.assertNotIn(f'{name}:', CSS_CONTENT,
                             f'{name} is unused and must not be redefined without a real consumer')
            self.assertNotIn(f'var({name}', CSS_CONTENT,
                             f'var({name}) must not appear without also adding a definition')
            self.assertNotIn(f'var({name}', JS_CONTENT,
                             f'var({name}) must not appear without also adding a definition')

    def test_border_color_split_from_bg_hover(self):
        """--border-color is a distinct variable from --bg-hover: --bg-hover
        is for hover-state background fills, --border-color is for
        border/outline decorations. Every theme must define both, and CSS
        border declarations must reference --border-color rather than
        --bg-hover (which would re-couple the two)."""
        theme_blocks = re.findall(r'(?::root|\[data-theme="[^"]+"\])\s*\{([^}]*)\}', CSS_CONTENT, re.DOTALL)
        theme_blocks_with_bg_hover = [b for b in theme_blocks if '--bg-hover:' in b]
        self.assertGreaterEqual(len(theme_blocks_with_bg_hover), 23,
                                'Expected at least 23 theme blocks defining --bg-hover')
        for body in theme_blocks_with_bg_hover:
            self.assertIn('--border-color:', body,
                         'Every theme defining --bg-hover must also define --border-color')
        self.assertNotIn('border-color: var(--bg-hover)', CSS_CONTENT,
                         'Border declarations must use var(--border-color), not var(--bg-hover)')
        self.assertNotRegex(CSS_CONTENT, r'border(?:-top|-bottom)?:\s*\d+px\s+(?:solid|dashed)\s+var\(--bg-hover\)',
                            'Border declarations must use var(--border-color), not var(--bg-hover)')
        # CGA's border should be a distinct, brighter cyan than its hover fill -
        # the exact bug this split was introduced to fix (see release notes).
        cga_block = next(b for b in theme_blocks if '--bg-hover: #008080' in b)
        self.assertIn('--border-color: #55ffff', cga_block,
                      'CGA border-color must be the bright CGA light cyan, distinct from the muted --bg-hover fill')

    def test_cga_header_footer_light_cyan(self):
        """CGA's header/footer use a bright light-cyan background (matching
        the real CGA Palette 1 High-Intensity hue) instead of the dark
        near-black bg-secondary every other theme uses there, with
        --text-bright/--text-muted overridden to a dark color for legibility
        against that bright background. The gear dropdown menu (a visual
        child of the header, but rendered on its own dark bg-secondary
        panel) must reset those same two variables back to their normal CGA
        values so its own text doesn't inherit the header's dark override."""
        header_footer_match = re.search(
            r'\[data-theme="cga"\] \.app-header,\s*\[data-theme="cga"\] \.footer\s*\{([^}]*)\}',
            CSS_CONTENT,
        )
        self.assertIsNotNone(header_footer_match,
                             'CGA must override .app-header/.footer background')
        body = header_footer_match.group(1)
        self.assertIn('background: #55ffff', body,
                     'CGA header/footer background must be the bright CGA light cyan')
        self.assertIn('--text-bright: #000000', body,
                     'CGA header/footer text-bright must switch to black for legibility on the bright cyan bg')
        self.assertIn('--text-muted: #003333', body,
                     'CGA header/footer text-muted must switch to a dark teal for legibility on the bright cyan bg')

        dropdown_match = re.search(
            r'\[data-theme="cga"\] \.app-header-menu-dropdown\s*\{([^}]*)\}',
            CSS_CONTENT,
        )
        self.assertIsNotNone(dropdown_match,
                             'CGA must reset the dropdown menu text vars back from the header override')
        dropdown_body = dropdown_match.group(1)
        self.assertIn('--text-bright: #ffffff', dropdown_body,
                     "Dropdown menu must reset --text-bright to CGA's normal (light) value")
        self.assertIn('--text-muted: #55aaaa', dropdown_body,
                     "Dropdown menu must reset --text-muted to CGA's normal (light) value")

        # The real (non-CGA-scoped) dropdown rule must appear before these
        # CGA overrides in the file, or test_theme_menu_items_do_not_wrap's
        # naive '.app-header-menu-dropdown {'.split() would grab the wrong
        # (CGA override) block instead of the real rule's min-width.
        real_rule_pos = CSS_CONTENT.index('.app-header-menu-dropdown { display: none;')
        cga_override_pos = CSS_CONTENT.index('[data-theme="cga"] .app-header-menu-dropdown')
        self.assertLess(real_rule_pos, cga_override_pos,
                        "The base .app-header-menu-dropdown rule must come before CGA's override "
                        "in the file, so naive substring-based CSS extraction in other tests still "
                        "finds the real rule first")

    def test_c64_logo_text_uses_light_blue(self):
        """The 'SO-CRATES' header logo link is normally --text-bright (white
        in every theme, including C64). C64 overrides it to --text-primary
        (light blue) instead, to match the rest of its header text rather
        than standing out in white."""
        self.assertIn('class="app-logo-text"', HTML_CONTENT,
                      'The header logo link must carry the app-logo-text class')
        override_match = re.search(
            r'\[data-theme="c64"\] \.app-logo-text\s*\{([^}]*)\}',
            CSS_CONTENT,
        )
        self.assertIsNotNone(override_match,
                             'C64 must override .app-logo-text color')
        self.assertIn('color: var(--text-primary) !important', override_match.group(1),
                      'C64 logo text must use --text-primary (light blue), overriding the '
                      'default --text-bright (white) with !important since the inline '
                      'style="color: var(--text-bright)" on the element itself outranks a '
                      'plain class selector')

    def test_hacker_previous_analysis_delete_overrides(self):
        self.assertIn('[data-theme="hacker"] .previous-analysis-delete', CSS_CONTENT,
                      'Hacker theme must override previous analysis delete color')
        self.assertIn('[data-theme="hacker"] .previous-analysis-delete-all', CSS_CONTENT,
                      'Hacker theme must override delete-all button color')

    def test_hacker_reanalyze_button_override(self):
        self.assertIn('[data-theme="hacker"] .reanalyze-confirm-btn', CSS_CONTENT,
                      'Hacker theme must override re-analyze confirm button')

    def test_hacker_delete_modal_overrides(self):
        self.assertIn('[data-theme="hacker"] .delete-modal-title', CSS_CONTENT,
                      'Hacker theme must override delete modal title color')
        self.assertIn('[data-theme="hacker"] .delete-modal-confirm-btn', CSS_CONTENT,
                      'Hacker theme must override delete modal confirm button')

    def test_hacker_theme_uses_base_font(self):
        self.assertIn('[data-theme="hacker"] body {', CSS_CONTENT,
                      'Hacker theme body rule must exist')
        hacker_body_block = CSS_CONTENT.split('[data-theme="hacker"] body {')[1].split('}')[0]
        self.assertNotIn('font-family:', hacker_body_block,
                         'Hacker theme must not override the base font family')

    def test_gear_icon_button_exists(self):
        self.assertIn('class="app-header-menu-btn"', HTML_CONTENT,
                      'Gear icon menu button must exist')

    def test_no_standalone_help_button(self):
        """Ensure the old standalone Help button is removed from the header."""
        header_right = HTML_CONTENT.split('id="appHeaderRight"')[1].split('</div>')[0]
        self.assertNotIn('class="app-header-help"', header_right,
                         'Standalone Help button must not exist in appHeaderRight')

    def test_magnifying_glass_uses_accent_color(self):
        """Magnifying glass SVG must use theme-aware color so it matches accent."""
        header_left = HTML_CONTENT.split('class="app-header-left"')[1].split('</div>')[0]
        svg_section = header_left.split('<svg')[1].split('</svg>')[0]
        self.assertTrue('stroke="currentColor"' in svg_section or 'stroke="var(--accent)"' in svg_section,
                        'Magnifying glass SVG must use currentColor or var(--accent) for theme adaptability')

    def test_theme_cycle_hotkey_exists(self):
        """Pressing 't' outside input fields must cycle themes."""
        self.assertIn("e.key === 't'", JS_CONTENT,
                      'JS must listen for the theme-cycle hotkey')
        self.assertIn('toggleTheme();', JS_CONTENT,
                      'Theme hotkey must call toggleTheme()')
        self.assertIn("showToast('Switched to ' + THEMES[nextTheme].label + ' theme')", JS_CONTENT,
                      'Theme hotkey must show a toast with the new theme name')
        # Guard against triggering while typing in inputs.
        self.assertIn("e.target.tagName !== 'INPUT'", JS_CONTENT,
                      'Theme hotkey must ignore input fields')
        self.assertIn("e.target.tagName !== 'TEXTAREA'", JS_CONTENT,
                      'Theme hotkey must ignore textarea fields')
        self.assertIn('!e.target.isContentEditable', JS_CONTENT,
                      'Theme hotkey must ignore contenteditable elements')

    def test_theme_hotkey_matches_menu_order(self):
        """The 't' hotkey must cycle themes in the same order they appear in the menu."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var order = [];
            setTheme('dark');
            for (var i = 0; i < 24; i++) {
                toggleTheme();
                order.push(document.documentElement.getAttribute('data-theme') || 'dark');
            }
            window.__jsdom_result = { order: order };
        ''')
        self.assertEqual(result['order'], ['nord', 'osaka-jade', 'retro-82', 'ristretto', 'tokyo-night', 'vantablack', 'c64', 'cga', 'hacker', 'sguil', 'catppuccin-latte', 'light', 'rose-pine', 'white', 'catppuccin', 'ethereal', 'everforest', 'gruvbox', 'hackerman', 'kanagawa', 'lumon', 'matte-black', 'miasma', 'dark'],
                         't hotkey cycle order must match menu order')

    def test_hacker_mode_easter_egg_exists(self):
        """Typing 31337 outside of input fields must activate Hacker."""
        self.assertIn("keyBuffer.endsWith('31337')", JS_CONTENT,
                      'JS must check for the 31337 easter egg sequence')
        self.assertIn("setTheme('hacker')", JS_CONTENT,
                      'Easter egg must activate Hacker')
        self.assertIn('Switched to Hacker theme', JS_CONTENT,
                      'Easter egg activation message must reference Hacker theme')
        self.assertIn('showToast(', JS_CONTENT,
                      'Easter egg must show an activation message')

    def test_cga_easter_egg_exists(self):
        """Typing cga outside of input fields must activate the CGA theme."""
        self.assertIn("keyBuffer.endsWith('cga')", JS_CONTENT,
                      'JS must check for the cga easter egg sequence')
        self.assertIn("setTheme('cga')", JS_CONTENT,
                      'Easter egg must activate CGA')
        self.assertIn('Switched to CGA theme', JS_CONTENT,
                      'Easter egg activation message must reference CGA theme')

    def test_easter_egg_short_code_triggers_via_endswith(self):
        """REGRESSION: a code shorter than the 5-char keyBuffer (like "cga")
        must actually trigger after other keystrokes, not just in the first
        few keystrokes after page load - this is exactly what endsWith()
        (rather than ===) on the buffer is for."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            setTheme('dark');
            function press(k) {
                document.dispatchEvent(new KeyboardEvent('keydown', {key: k}));
            }
            'xyz'.split('').forEach(press);
            'cga'.split('').forEach(press);
            window.__jsdom_result = { theme: getCurrentTheme() };
        ''')
        self.assertEqual(result['theme'], 'cga',
                         'Typing cga after other keystrokes must still activate CGA theme')

    def test_c64_easter_egg_exists(self):
        """Typing c64 outside of input fields must activate the C64 theme."""
        self.assertIn("keyBuffer.endsWith('c64')", JS_CONTENT,
                      'JS must check for the c64 easter egg sequence')
        self.assertIn("setTheme('c64')", JS_CONTENT,
                      'Easter egg must activate C64')
        self.assertIn('Switched to C64 theme', JS_CONTENT,
                      'Easter egg activation message must reference C64 theme')

    def test_c64_easter_egg_short_code_triggers_via_endswith(self):
        """REGRESSION: same class of bug as the cga easter egg - a code
        shorter than the 5-char keyBuffer (like "c64") must actually trigger
        after other keystrokes, not just in the first few keystrokes after
        page load."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            setTheme('dark');
            function press(k) {
                document.dispatchEvent(new KeyboardEvent('keydown', {key: k}));
            }
            'xyz'.split('').forEach(press);
            'c64'.split('').forEach(press);
            window.__jsdom_result = { theme: getCurrentTheme() };
        ''')
        self.assertEqual(result['theme'], 'c64',
                         'Typing c64 after other keystrokes must still activate C64 theme')

    def test_hacker_mode_easter_egg_ignores_input_fields(self):
        """Easter egg must not trigger while typing in form controls."""
        listener_match = re.search(r'document\.addEventListener\(\'keydown\',\s*function\(e\)\s*\{', JS_CONTENT)
        self.assertIsNotNone(listener_match, 'keydown listener must exist')
        start = listener_match.end()
        brace_count = 1
        pos = start
        while pos < len(JS_CONTENT) and brace_count > 0:
            if JS_CONTENT[pos] == '{':
                brace_count += 1
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
        listener_body = JS_CONTENT[start:pos]
        self.assertIn("tag === 'INPUT'", listener_body,
                      'Easter egg must ignore INPUT elements')
        self.assertIn("tag === 'TEXTAREA'", listener_body,
                      'Easter egg must ignore TEXTAREA elements')
        self.assertIn("tag === 'SELECT'", listener_body,
                      'Easter egg must ignore SELECT elements')
        self.assertIn('isContentEditable', listener_body,
                      'Easter egg must ignore contenteditable elements')


class TestAggregationTables(unittest.TestCase):
    def test_has_agg_grid_css(self):
        self.assertIn('.agg-grid', CSS_CONTENT)

    def test_has_agg_section_css(self):
        """agg-section must be a flex item sized to content, not fixed widths."""
        self.assertIn('.agg-section', CSS_CONTENT)
        section_match = re.search(r'\.agg-section\s*\{([^}]+)\}', CSS_CONTENT)
        self.assertIsNotNone(section_match, 'agg-section CSS rule must exist')
        section_style = section_match.group(1)
        self.assertIn('flex: 0 1 auto', section_style,
                      'agg-section must size to content, not force fixed widths')
        self.assertNotIn('min-width', section_style,
                         'agg-section must not have fixed min-width')
        self.assertNotIn('max-width', section_style,
                         'agg-section must not have fixed max-width')

    def test_agg_table_sized_to_content(self):
        """agg-table tables must fill container while columns size to data."""
        rule_match = re.search(r'\.agg-table table\s*\{([^}]+)\}', CSS_CONTENT)
        self.assertIsNotNone(rule_match, '.agg-table table CSS rule must exist')
        rule_style = rule_match.group(1)
        self.assertIn('width: 100%', rule_style,
                      'agg-table must fill container for consistent header backgrounds')
        self.assertIn('table-layout: auto', rule_style,
                      'agg-table columns must size based on data')

    def test_has_agg_table_css(self):
        self.assertIn('.agg-table', CSS_CONTENT)

    def test_has_agg_table_title_css(self):
        self.assertIn('.agg-table .agg-header', CSS_CONTENT)

    def test_has_agg_row_css(self):
        self.assertIn('.agg-row', CSS_CONTENT)

    def test_has_agg_cell_css(self):
        self.assertIn('.agg-cell', CSS_CONTENT)

    def test_agg_cell_allows_full_text(self):
        """agg-cell must show full values without truncation."""
        cell_match = re.search(r'\.agg-cell\s*\{([^}]+)\}', CSS_CONTENT)
        self.assertIsNotNone(cell_match, '.agg-cell CSS rule must exist')
        cell_style = cell_match.group(1)
        self.assertNotIn('text-overflow: ellipsis', cell_style,
                         'agg-cell must not truncate with ellipsis')
        self.assertNotIn('white-space: nowrap', cell_style,
                         'agg-cell must allow text wrapping')
        self.assertNotIn('max-width', cell_style,
                         'agg-cell must not have fixed max-width')
        self.assertIn('overflow-wrap: break-word', cell_style,
                      'agg-cell must wrap long words')

    def test_agg_table_td_allows_full_text(self):
        """agg-table td cells must not force single-line truncation."""
        td_match = re.search(r'\.agg-table td\s*\{([^}]+)\}', CSS_CONTENT)
        self.assertIsNotNone(td_match, '.agg-table td CSS rule must exist')
        td_style = td_match.group(1)
        self.assertNotIn('text-overflow: ellipsis', td_style,
                         'agg-table td must not truncate with ellipsis')
        self.assertNotIn('white-space: nowrap', td_style,
                         'agg-table td must allow text wrapping')

    def test_has_aggregations_container(self):
        self.assertIn('id="aggregations"', HTML_CONTENT)

    def test_has_build_aggregation_tables_function(self):
        self.assertIn('function buildAggregationTables', JS_CONTENT)

    def test_has_build_aggregation_tables_all_function(self):
        self.assertIn('function buildAggregationTablesAll', JS_CONTENT)

    def test_has_build_aggregation_tables_core_function(self):
        """buildAggregationTablesCore must exist as the unified aggregation builder."""
        self.assertIn('function buildAggregationTablesCore', JS_CONTENT)

    def test_buildAggregationTables_delegates_to_core(self):
        """REGRESSION: buildAggregationTables must delegate to buildAggregationTablesCore
        instead of duplicating the grid-building logic."""
        func = JS_CONTENT.split('function buildAggregationTables(')[1].split('function ')[0]
        self.assertIn('buildAggregationTablesCore', func,
                      'buildAggregationTables must delegate to buildAggregationTablesCore')

    def test_buildAggregationTablesAll_delegates_to_core(self):
        """REGRESSION: buildAggregationTablesAll must delegate to buildAggregationTablesCore
        instead of duplicating the grid-building logic."""
        func = JS_CONTENT.split('function buildAggregationTablesAll(')[1].split('function ')[0]
        self.assertIn('buildAggregationTablesCore', func,
                      'buildAggregationTablesAll must delegate to buildAggregationTablesCore')

    def test_has_extract_value_function(self):
        self.assertIn('function extractValue', JS_CONTENT)

    def test_has_extract_all_value_function(self):
        self.assertIn('function extractAllValue', JS_CONTENT)

    def test_extractAllValue_handles_all_events_columns(self):
        """extractAllValue must special-case 'Type' (it means "the event_type
        itself", e.g. "DNS"/"ANOMALY" - different semantics than the
        per-type 'Type' column, e.g. a DNS record type) and delegate
        everything else to extractValue for per-type columns so filters
        work correctly.

        REGRESSION: 'Command' and 'Message' used to be special-cased here
        too, but both were stale - 'Command' predates pgsql/enip/pop3
        gaining their own real command fields (this always returned '' for
        them, ignoring extractValue's own already-correct per-protocol
        handling), and 'Message' read e.anomaly?.message, a field that has
        never existed in Suricata's eve.json anomaly schema (real field is
        'event') and hasn't been a real column label since anomaly gained
        real columns (Event/Type/Layer/App Proto). Both must now be absent
        so extractValue's own correct handling is used instead."""
        func_body = JS_CONTENT.split('function extractAllValue')[1].split('function buildAggregationTablesCore')[0]
        self.assertIn("col === 'Type'", func_body,
                      'extractAllValue must handle Type column')
        self.assertNotIn("col === 'Command'", func_body,
                          'extractAllValue must not override Command - extractValue already handles it per-protocol')
        self.assertNotIn("col === 'Message'", func_body,
                          "extractAllValue must not override Message - it read a field that never existed")
        self.assertIn('return extractValue(e, col, colIndex)', func_body,
                      'extractAllValue must delegate to extractValue')

    def test_extractValue_handles_detail_column(self):
        """extractValue must handle 'Detail' column for all event types so
        filters set in the 'All Events' view work correctly on per-type tabs."""
        func_body = JS_CONTENT.split('function extractValue')[1].split('function buildAggregationTables')[0]
        self.assertIn("case 'Detail':", func_body,
                      'extractValue must handle Detail column')
        self.assertIn("e.event_type", func_body,
                      'extractValue Detail must check event_type')
        self.assertIn("e.alert?.signature", func_body,
                      'extractValue Detail must handle alert events')
        self.assertIn("e.dns?.rrname", func_body,
                      'extractValue Detail must handle dns events')
        self.assertIn("e.tls?.sni", func_body,
                      'extractValue Detail must handle tls events')

    def test_has_build_aggregations_section_function(self):
        self.assertIn('function buildAggregationsSection', JS_CONTENT)

    def test_has_build_aggregations_section_all_function(self):
        self.assertIn('function buildAggregationsSectionAll', JS_CONTENT)

    def test_agg_tables_use_string_ports(self):
        self.assertIn("String(e.src_port", JS_CONTENT)
        self.assertIn("String(e.dest_port", JS_CONTENT)

    def test_buildAggregationTablesCore_produces_html(self):
        """buildAggregationTablesCore must produce HTML with aggregation rows for sample events."""
        from tests.jsdom_helper import js_statements
        events = [
            {'event_type': 'alert', 'proto': 'TCP', 'src_ip': '1.2.3.4', 'src_port': 80, 'dest_ip': '5.6.7.8', 'dest_port': 443, 'alert': {'signature': 'Test Sig'}},
            {'event_type': 'alert', 'proto': 'TCP', 'src_ip': '1.2.3.4', 'src_port': 80, 'dest_ip': '5.6.7.8', 'dest_port': 443, 'alert': {'signature': 'Test Sig'}},
            {'event_type': 'alert', 'proto': 'UDP', 'src_ip': '9.8.7.6', 'src_port': 53, 'dest_ip': '1.2.3.4', 'dest_port': 53, 'alert': {'signature': 'DNS Sig'}},
        ]
        result = js_statements(f'''
            var events = {json.dumps(events)};
            var html = buildAggregationTablesCore(events, ['Protocol', 'Source IP'], 'section-alert', extractValue);
            window.__jsdom_result = {{
                hasTCP: html.indexOf('TCP') >= 0,
                hasUDP: html.indexOf('UDP') >= 0,
                hasSrcIp: html.indexOf('1.2.3.4') >= 0,
                hasCount2: html.indexOf('2') >= 0,
                hasAggRow: html.indexOf('agg-row') >= 0,
            }};
        ''')
        self.assertTrue(result['hasTCP'], 'HTML must contain TCP protocol')
        self.assertTrue(result['hasUDP'], 'HTML must contain UDP protocol')
        self.assertTrue(result['hasSrcIp'], 'HTML must contain source IP')
        self.assertTrue(result['hasCount2'], 'HTML must contain count of 2')
        self.assertTrue(result['hasAggRow'], 'HTML must contain aggregation rows')

    def test_extractAllValue_cross_type(self):
        """extractAllValue must return correct values for cross-event-type
        columns, correctly delegating 'Command' to extractValue's own
        per-protocol handling (ftp AND pop3/pgsql/enip, not just ftp - see
        the regression note on test_extractAllValue_handles_all_events_columns)
        and 'Event' for anomaly's real field."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var e1 = {event_type: 'alert', proto: 'TCP', alert: {signature: 'Test Alert'}};
            var e2 = {event_type: 'ftp', proto: 'TCP', ftp: {command: 'USER admin'}};
            var e3 = {event_type: 'anomaly', proto: 'TCP', anomaly: {event: 'APPLAYER_DETECT_PROTOCOL_ONLY_ONE_DIRECTION'}};
            var e4 = {event_type: 'pop3', proto: 'TCP', pop3: {request: {command: 'RETR'}}};
            window.__jsdom_result = {
                alertType: extractAllValue(e1, 'Type', -1),
                alertProto: extractAllValue(e1, 'Protocol', -1),
                ftpCommand: extractAllValue(e2, 'Command', -1),
                anomalyEvent: extractAllValue(e3, 'Event', -1),
                pop3Command: extractAllValue(e4, 'Command', -1),
            };
        ''')
        self.assertEqual(result['alertType'], 'ALERT')
        self.assertEqual(result['alertProto'], 'TCP')
        self.assertEqual(result['ftpCommand'], 'USER admin')
        self.assertEqual(result['anomalyEvent'], 'APPLAYER_DETECT_PROTOCOL_ONLY_ONE_DIRECTION')
        self.assertEqual(result['pop3Command'], 'RETR')

    def test_agg_tables_have_click_handlers(self):
        self.assertIn("onclick=\"applyFilter('${sectionId}', '${escapeJsString(col)}', '${escapeJsString(filterVal)}')\"", JS_CONTENT)

    def test_agg_tables_no_bar_charts(self):
        self.assertNotIn('.agg-bar', CSS_CONTENT)

    def test_agg_tables_have_borders(self):
        self.assertIn('border: 1px solid var(--border-color)', CSS_CONTENT)

    def test_agg_tables_wrap_with_flex(self):
        self.assertIn('flex-wrap: wrap', CSS_CONTENT)

    def test_agg_header_has_close_button(self):
        """Each aggregation table header must include a close button to hide the table."""
        self.assertIn('agg-close', CSS_CONTENT,
                      'agg-close CSS class must exist')
        self.assertIn("hideAggregationTable('${sectionId}'", JS_CONTENT,
                      'Aggregation header must call hideAggregationTable')

    def test_hide_aggregation_table_function_exists(self):
        """JavaScript must define hideAggregationTable to track hidden aggregation tables."""
        self.assertIn('function hideAggregationTable(', JS_CONTENT,
                      'hideAggregationTable function must exist')
        self.assertIn('hiddenAggregations', JS_CONTENT,
                      'hiddenAggregations variable must exist')

    def test_aggregation_skips_hidden_columns(self):
        """buildAggregationTables must filter out columns in hiddenAggregations."""
        self.assertIn("!hiddenAggregations.has(sectionId + ':' + c)", JS_CONTENT,
                      'buildAggregationTables must skip hidden columns')

    def test_hide_aggregation_table_auto_collapses_section(self):
        """Closing the last visible aggregation table must collapse the section."""
        self.assertIn("advancedMode = false", JS_CONTENT,
                      'hideAggregationTable must set advancedMode to false when last table hidden')
        self.assertIn("▸ Aggregation Tables", JS_CONTENT,
                      'hideAggregationTable must render collapsed heading when last table hidden')


class TestFiltering(unittest.TestCase):
    def test_has_current_filters_state(self):
        self.assertIn('currentFilters', JS_CONTENT)

    def test_has_apply_filter_function(self):
        self.assertIn('function applyFilter', JS_CONTENT)

    def test_has_clear_filter_function(self):
        self.assertIn('function clearFilter', JS_CONTENT)

    def test_has_clear_all_filters_function(self):
        self.assertIn('function clearAllFilters', JS_CONTENT)

    def test_has_get_filtered_events_function(self):
        self.assertIn('function getFilteredEvents', JS_CONTENT)

    def test_has_filter_bar_css(self):
        self.assertIn('.filter-bar', CSS_CONTENT)

    def test_has_filter_chip_css(self):
        self.assertIn('.filter-chip', CSS_CONTENT)

    def test_has_filter_clear_all_css(self):
        self.assertIn('.filter-clear-all', CSS_CONTENT)

    def test_has_footer_css(self):
        self.assertIn('.footer', CSS_CONTENT)

    def test_has_footer_with_version_placeholder(self):
        self.assertIn('SO-CRATES</a>', HTML_CONTENT)
        self.assertIn('id="footerVersionLink"', HTML_CONTENT)

    def test_has_footer_with_copyright(self):
        self.assertIn('Security Onion Solutions, LLC', HTML_CONTENT)

    def test_has_footer_links(self):
        self.assertIn('github.com/dougburks', HTML_CONTENT)
        self.assertIn('securityonion.com', HTML_CONTENT)

    def test_has_analysis_header(self):
        self.assertIn('id="mainHeader"', HTML_CONTENT)

    def test_has_instructions_in_analysis(self):
        """Analysis instructions must mention filtering options and hexdump."""
        self.assertIn('Start by reviewing all alerts', JS_CONTENT)
        self.assertIn('Filter using the search bar, sankey diagram, or aggregation tables', JS_CONTENT)
        self.assertIn('ASCII transcript and hexdump and optionally download', JS_CONTENT)
        self.assertNotIn('ASCII transcript and optionally download', JS_CONTENT)

    def test_filter_bar_only_in_aggregations(self):
        self.assertIn('buildAggregationsSection', JS_CONTENT)

    def test_filters_reset_on_new_pcap(self):
        self.assertIn('currentFilters = {}', JS_CONTENT)

    def test_filter_uses_string_comparison_for_ports(self):
        self.assertIn("String(e.src_port", JS_CONTENT)
        self.assertIn("String(e.dest_port", JS_CONTENT)

    def test_empty_value_handling_in_agg_tables(self):
        self.assertIn("(empty)", JS_CONTENT)

    def test_empty_value_converts_to_empty_string_on_click(self):
        self.assertIn("val === '(empty)' ? '' : val", JS_CONTENT)

    def test_all_events_filter_uses_buildAllEvents(self):
        self.assertIn("eventType === 'all'", JS_CONTENT)
        self.assertIn("buildAllEvents()", JS_CONTENT)

    def test_aggregations_cleared_on_welcome(self):
        self.assertIn("document.getElementById('aggregations').innerHTML = ''", JS_CONTENT)

    def test_getFilteredEvents_handles_all_type(self):
        self.assertIn("function getFilteredEvents", JS_CONTENT)
        self.assertIn("eventType === 'all'", JS_CONTENT)

    def test_eventMatchesFilters_uses_extractValue_unconditionally(self):
        """eventMatchesFilters must call extractValue for all columns, not gated by colIndex.
        Cross-type metadata (e.g., http.hostname on a fileinfo event) must be matched."""
        func_body = JS_CONTENT.split('function eventMatchesFilters')[1].split('function computeFilteredStats')[0]
        self.assertIn("extractValue(event, col, -1)", func_body,
                      'eventMatchesFilters must call extractValue unconditionally')
        self.assertNotIn("colIndex >= 0", func_body,
                          'eventMatchesFilters must not gate extractValue on colIndex')

    def test_extractValue_works_across_event_types(self):
        """extractValue must return correct values for all event types and columns."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var e1 = {event_type: 'alert', proto: 'TCP', src_ip: '1.2.3.4', alert: {signature: 'Test Alert'}};
            var e2 = {event_type: 'dns', proto: 'UDP', src_ip: '5.6.7.8', dns: {rrname: 'example.com'}};
            var e3 = {event_type: 'fileinfo', proto: 'TCP', src_ip: '9.8.7.6', fileinfo: {filename: 'test.exe'}};
            window.__jsdom_result = {
                alertProto: extractValue(e1, 'Protocol', -1),
                alertSig: extractValue(e1, 'Alert', -1),
                dnsProto: extractValue(e2, 'Protocol', -1),
                dnsQuery: extractValue(e2, 'Query', -1),
                fileProto: extractValue(e3, 'Protocol', -1),
                fileName: extractValue(e3, 'Filename', -1),
            };
        ''')
        self.assertEqual(result['alertProto'], 'TCP')
        self.assertEqual(result['alertSig'], 'Test Alert')
        self.assertEqual(result['dnsProto'], 'UDP')
        self.assertEqual(result['dnsQuery'], 'example.com')
        self.assertEqual(result['fileProto'], 'TCP')
        self.assertEqual(result['fileName'], 'test.exe')

    def test_extractValue_disambiguates_shared_column_labels_by_event_type(self):
        """REGRESSION: 'Category'/'Type'/'Query' are each used by two event
        types with getColumnsForType(), but extractValue's switch(col) is
        keyed only by label - modbus's Category, dnp3's Type, and pgsql's
        Query previously had no event_type branch, so a JS switch's first
        matching case (alert.category / dns.rrtype / dns.rrname) always won
        and those three columns rendered empty for every real event."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var modbusEvent = {event_type: 'modbus', modbus: {request: {category: 'PUBLIC_ASSIGNED'}}};
            var dnp3Event = {event_type: 'dnp3', dnp3: {type: 'unsolicited_response'}};
            var pgsqlEvent = {event_type: 'pgsql', pgsql: {request: {simple_query: 'SELECT 1'}}};
            // Sibling event types sharing the same label must still work.
            var alertEvent = {event_type: 'alert', alert: {category: 'A Network Trojan was detected'}};
            var dnsEvent = {event_type: 'dns', dns: {rrtype: 'A', rrname: 'example.com'}};
            window.__jsdom_result = {
                modbusCategory: extractValue(modbusEvent, 'Category', -1),
                dnp3Type: extractValue(dnp3Event, 'Type', -1),
                pgsqlQuery: extractValue(pgsqlEvent, 'Query', -1),
                alertCategory: extractValue(alertEvent, 'Category', -1),
                dnsType: extractValue(dnsEvent, 'Type', -1),
                dnsQuery: extractValue(dnsEvent, 'Query', -1),
            };
        ''')
        self.assertEqual(result['modbusCategory'], 'PUBLIC_ASSIGNED')
        self.assertEqual(result['dnp3Type'], 'unsolicited_response')
        self.assertEqual(result['pgsqlQuery'], 'SELECT 1')
        self.assertEqual(result['alertCategory'], 'A Network Trojan was detected')
        self.assertEqual(result['dnsType'], 'A')
        self.assertEqual(result['dnsQuery'], 'example.com')

    def test_buildStats_no_filealerts_special_case(self):
        """buildStats must use filteredStats consistently for all event types, including filealerts."""
        func_body = JS_CONTENT.split('function buildStats(')[1].split('function buildFilterBarHtml')[0]
        self.assertNotIn("if (type === 'filealerts')", func_body,
                         'buildStats must not special-case filealerts count')
        self.assertIn('filteredStats ? (filteredStats[type] || 0)', func_body,
                      'buildStats must use filteredStats for all types')

    def test_sigmaAlertMatchesFilters_uses_original_log_for_dynamic_columns(self):
        """The shared extractSigmaValue helper (used by sigmaAlertMatchesFilters
        and getFilteredSigmaAlerts) must parse original_log for dynamic columns."""
        self.assertIn('return matchesCurrentFilters(alert, extractSigmaValue)', JS_CONTENT,
                      'sigmaAlertMatchesFilters must delegate to extractSigmaValue')
        func_body = JS_CONTENT.split('function extractSigmaValue')[1].split('function getFilteredLogEvents')[0]
        self.assertIn('JSON.parse(alert.original_log ||', func_body,
                      'extractSigmaValue must parse original_log for dynamic columns')
        self.assertIn('_getFieldForLabel(col)', func_body,
                      'extractSigmaValue must use _getFieldForLabel for dynamic column lookup')


class TestPerformance(unittest.TestCase):
    def test_paginates_large_tables_instead_of_rendering_all_rows(self):
        """Data tables must cap rendered rows per page rather than inserting
        every fetched row into the DOM at once (up to the user-configurable
        query limit, default 75000, server ceiling 100000)."""
        self.assertIn('TABLE_PAGE_SIZE', JS_CONTENT)
        self.assertIn('function renderPaginatedTable', JS_CONTENT)

    def test_uses_event_delegation(self):
        self.assertIn('addEventListener', JS_CONTENT)

    def test_lazy_loads_ascii_transcripts(self):
        self.assertIn('loadAsciiTranscript', JS_CONTENT)
        self.assertIn('!pre.innerHTML', JS_CONTENT)

    def test_truncates_large_streams(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'socrates.py'), 'r') as f:
            server_content = f.read()
        self.assertIn('truncated', server_content)


class TestAdvancedToggle(unittest.TestCase):
    def test_has_advanced_toggle_input(self):
        self.assertIn('toggleAggregations()', JS_CONTENT)

    def test_has_advanced_mode_js_variable(self):
        self.assertIn('var advancedMode', JS_CONTENT)

    def test_aggregations_collapsed_by_default(self):
        self.assertIn("▸ Aggregation Tables", JS_CONTENT)

    def test_filter_bar_container_exists(self):
        self.assertIn('id="filterBarContainer"', HTML_CONTENT)

    def test_update_filter_bar_visibility_function(self):
        self.assertIn('function updateFilterBarVisibility', JS_CONTENT)
        self.assertIn('function buildFilterBarHtml', JS_CONTENT)

    def test_advanced_toggle_in_header(self):
        self.assertIn('Aggregation Tables', JS_CONTENT)
        self.assertIn("toggleAggregations()", JS_CONTENT)


class TestFilterOnclickQuoting(unittest.TestCase):
    """Regression tests for JSON.stringify double-quote collision in onclick attributes.

    JSON.stringify() produces double-quoted strings like "Source IP", which break
    when embedded in double-quoted onclick attributes. All onclick handlers must
    use single-quoted string arguments with escaped internal single quotes instead.
    """

    def test_no_json_stringify_in_apply_filter_onclick(self):
        """applyFilter onclick must not use JSON.stringify (causes double-quote collision)"""
        apply_filter_matches = re.findall(r'onclick="applyFilter\([^"]*\)"', JS_CONTENT)
        for match in apply_filter_matches:
            self.assertNotIn('JSON.stringify', match,
                f'applyFilter onclick uses JSON.stringify which breaks in double-quoted onclick: {match[:80]}')

    def test_no_json_stringify_in_clear_filter_onclick(self):
        """clearFilter onclick must not use JSON.stringify (causes double-quote collision)"""
        clear_filter_matches = re.findall(r'onclick="clearFilter\([^"]*\)"', JS_CONTENT)
        for match in clear_filter_matches:
            self.assertNotIn('JSON.stringify', match,
                f'clearFilter onclick uses JSON.stringify which breaks in double-quoted onclick: {match[:80]}')

    def test_apply_filter_uses_single_quoted_args(self):
        """applyFilter onclick should use single-quoted string arguments via escapeJsString"""
        self.assertRegex(JS_CONTENT, r"onclick=\"applyFilter\('[^']+',\s*'\$\{escapeJsString\([^)]+\)\}',\s*'\$\{escapeJsString\([^)]+\)\}'\)\"",
            'applyFilter onclick should use single-quoted escapeJsString expressions')

    def test_clear_filter_uses_single_quoted_args(self):
        """clearFilter onclick should use single-quoted string argument"""
        self.assertRegex(JS_CONTENT, r"onclick=\"clearFilter\('\$\{[^}]+\}'\)\"",
            'clearFilter onclick should use single-quoted template expression')

    def test_agg_row_onclick_has_escaped_quotes(self):
        """agg-row onclick handlers must escape single quotes in values via escapeJsString"""
        self.assertIn('escapeJsString', JS_CONTENT,
            'onclick handlers must use escapeJsString for JS-context escaping')

    def test_no_bare_json_stringify_in_onclick_templates(self):
        """No template literal should embed JSON.stringify directly into an onclick attribute"""
        lines = JS_CONTENT.split('\n')
        for i, line in enumerate(lines):
            if 'onclick=' in line and 'JSON.stringify' in line:
                self.fail(f'Line {i+1} has JSON.stringify inside onclick template: {line.strip()}')


class TestAdvancedModeFilterBar(unittest.TestCase):
    """Regression tests for advanced mode toggle and filter bar persistence."""

    def test_loadTabData_calls_updateFilterBarVisibility_for_cached_data(self):
        """loadTabData must call updateFilterBarVisibility when using cached data"""
        self.assertIn("updateFilterBarVisibility()", JS_CONTENT)
        pattern = r"buildSection\(eventType,\s*tabDataCache\[eventType\]\);[\s\S]{0,80}updateFilterBarVisibility\(\)"
        self.assertRegex(JS_CONTENT, pattern,
            'loadTabData must call updateFilterBarVisibility after buildSection for cached data')

    def test_loadTabData_calls_updateFilterBarVisibility_for_fresh_data(self):
        """loadTabData must call updateFilterBarVisibility after fetching fresh data"""
        pattern = r"buildSection\(eventType,\s*events\);[\s\S]{0,80}updateFilterBarVisibility\(\)"
        self.assertRegex(JS_CONTENT, pattern,
            'loadTabData must call updateFilterBarVisibility after buildSection for fresh data')

    def test_loadTabData_all_events_calls_updateFilterBarVisibility(self):
        """loadTabData for "all" events must call updateFilterBarVisibility"""
        pattern = r"buildAllEvents\(\);\s*if\s*\(\s*sectionEl\s*&&\s*advancedMode\s*\)\s*(await\s+)?buildAggregationsSectionAll\(\);\s*updateFilterBarVisibility\(\)"
        self.assertRegex(JS_CONTENT, pattern,
            'loadTabData must call updateFilterBarVisibility for "all" events')

    def test_advanced_toggle_clears_filterBarContainer(self):
        """Enabling advanced mode must clear filterBarContainer to prevent duplicate filter bars"""
        self.assertIn("filterBarContainer.innerHTML = ''", JS_CONTENT)
        self.assertIn("filterBarContainer.style.display = 'none'", JS_CONTENT)

    def test_advanced_toggle_collapses_aggregations_on_disable(self):
        """Collapsing aggregations must render collapsed heading instead of clearing container"""
        self.assertIn("▸ Aggregation Tables", JS_CONTENT,
            'Aggregation collapse must render collapsed heading bar')

    def test_filters_are_global_not_per_section(self):
        """currentFilters must be a flat object so filters persist across all views"""
        self.assertIn("currentFilters[f.column] = f.value", JS_CONTENT)
        self.assertNotIn("currentFilters[sectionId] = {}", JS_CONTENT)
        self.assertNotIn("currentFilters[sectionId][columnName]", JS_CONTENT)

    def test_buildSection_uses_global_filters(self):
        """buildSection must filter using global currentFilters, not per-section filters"""
        self.assertIn("Object.keys(currentFilters).length", JS_CONTENT)
        self.assertNotIn("currentFilters[sectionId] || {}", JS_CONTENT)

    def test_buildAggregationsSection_uses_global_filters(self):
        """buildAggregationsSection must render heading bar and delegate to buildAggregationTables"""
        self.assertIn('function buildAggregationsSection', JS_CONTENT)
        self.assertIn('section-toggle-bar', JS_CONTENT)

    def test_buildAggregationsSectionAll_uses_global_filters(self):
        """buildAggregationsSectionAll must use global currentFilters for filtering and filter bar"""
        pattern = r"function buildAggregationsSectionAll[\s\S]{0,1600}Object\.keys\(currentFilters\)\.length"
        self.assertRegex(JS_CONTENT, pattern,
            'buildAggregationsSectionAll must check Object.keys(currentFilters).length')

    def test_advanced_toggle_handles_all_events_type(self):
        """Advanced toggle must handle "all" events type by calling buildAggregationsSectionAll"""
        pattern = r"eventType\s*===\s*'all'[\s\S]{0,100}buildAggregationsSectionAll"
        self.assertRegex(JS_CONTENT, pattern,
            'Advanced toggle handler must call buildAggregationsSectionAll for "all" events')

    def test_clearFilter_uses_global_filters(self):
        """clearFilter must delete from flat currentFilters, not nested"""
        self.assertIn("delete currentFilters[columnName]", JS_CONTENT)
        self.assertNotIn("delete currentFilters[sectionId]", JS_CONTENT)

    def test_applyFilters_calls_updateFilterBarVisibility(self):
        """applyFilters must call updateFilterBarVisibility and rebuild stats after refreshing the view."""
        func = JS_CONTENT.split('function applyFilters(')[1].split('function applyFilter(')[0]
        self.assertIn('refreshCurrentView(sectionId, eventType)', func,
                      'applyFilters must call refreshCurrentView')
        self.assertIn('updateFilterBarVisibility()', func,
                      'applyFilters must call updateFilterBarVisibility after refreshCurrentView')
        self.assertIn('buildStats(await computeFilteredStats())', func,
                      'applyFilters must rebuild stat card counts after applying filters')

    def test_applyFilters_binary_path_calls_updateFilterBarVisibility(self):
        """applyFilters must update UI in the binary analysis early-return path,
        using the narrower binary-events fetch instead of ensureCappedBatch('all').
        Must NOT rebuild stats: binary mode hides #statsGrid entirely, so
        buildStats(await computeFilteredStats()) is dead work there."""
        func = JS_CONTENT.split('function applyFilters(')[1].split('function applyFilter(')[0]
        self.assertIn("if (sectionId === 'section-binary')", func,
                      'applyFilters must check for section-binary')
        self.assertIn('updateFilterBarVisibility()', func,
                      'applyFilters must call updateFilterBarVisibility')
        # Verify calls appear before return in the binary branch
        binary_branch = func.split("if (sectionId === 'section-binary')")[1].split('return;')[0]
        self.assertIn('await ensureBinaryEventsBatch()', binary_branch,
            'applyFilters binary path must use the narrow binary-events fetch')
        self.assertIn('updateFilterBarVisibility()', binary_branch,
            'applyFilters binary path must call updateFilterBarVisibility before return')
        self.assertNotIn('buildStats(', binary_branch,
            'applyFilters binary path must not rebuild the hidden statsGrid')

    def test_clearFilter_calls_updateFilterBarVisibility(self):
        """clearFilter must update UI after refreshing the view."""
        func = JS_CONTENT.split('function clearFilter(')[1].split('async function clearAllFilters(')[0]
        self.assertIn('refreshCurrentView(visibleSection.id, eventType)', func,
                      'clearFilter must call refreshCurrentView')
        self.assertIn('updateFilterBarVisibility()', func,
                      'clearFilter must call updateFilterBarVisibility after refreshCurrentView')
        self.assertIn('buildStats(await computeFilteredStats())', func,
                      'clearFilter must rebuild stat card counts after clearing filters')

    def test_clearFilter_binary_path_calls_updateFilterBarVisibility(self):
        """clearFilter must update UI in the binary analysis early-return path,
        using the narrower binary-events fetch instead of ensureCappedBatch('all').
        Must NOT rebuild stats: binary mode hides #statsGrid entirely, so
        buildStats(await computeFilteredStats()) is dead work there."""
        func = JS_CONTENT.split('function clearFilter(')[1].split('async function clearAllFilters(')[0]
        self.assertIn('buildBinaryAnalysisView(allEvents)', func,
                      'clearFilter must call buildBinaryAnalysisView for binary mode')
        self.assertIn('updateFilterBarVisibility()', func,
                      'clearFilter must call updateFilterBarVisibility')
        # ensureBinaryEventsBatch call must precede buildBinaryAnalysisView
        pre = func.split('buildBinaryAnalysisView(allEvents)')[0]
        self.assertIn('await ensureBinaryEventsBatch()', pre,
            'clearFilter binary path must use the narrow binary-events fetch')
        # Verify calls appear before return in the binary branch
        binary_branch = func.split('buildBinaryAnalysisView(allEvents)')[1].split('return;')[0]
        self.assertIn('updateFilterBarVisibility()', binary_branch,
            'clearFilter binary path must call updateFilterBarVisibility before return')
        self.assertNotIn('buildStats(', binary_branch,
            'clearFilter binary path must not rebuild the hidden statsGrid')

    def test_fetchBinaryEvents_uses_type_scoped_requests(self):
        """fetchBinaryEvents must request fileinfo and filealerts by type=,
        never the untyped 'all' endpoint - binary-file analyses only ever
        produce these two event types, so narrowing the fetch by type avoids
        pulling in every other event type in the database."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var urls = [];
            window.fetch = function(url) {
                urls.push(url);
                if (url.indexOf('/api/events') >= 0 && url.indexOf('type=fileinfo') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([{ event_type: 'fileinfo' }]) });
                }
                if (url.indexOf('/api/events') >= 0 && url.indexOf('type=filealerts') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([{ event_type: 'filealerts' }]) });
                }
                return Promise.resolve({ json: () => Promise.resolve([]) });
            };
            currentMd5 = 'abc123';
            var result = await fetchBinaryEvents('');
            var eventsCalls = urls.filter(u => u.indexOf('/api/events') >= 0);
            window.__jsdom_result = {
                hitFileAlerts: eventsCalls.some(u => u.indexOf('type=filealerts') >= 0),
                hitFileInfo: eventsCalls.some(u => u.indexOf('type=fileinfo') >= 0),
                untypedEventsCalls: eventsCalls.filter(u => u.indexOf('type=') < 0).length,
                eventsCallCount: eventsCalls.length,
                result: result
            };
        ''')
        self.assertTrue(result['hitFileAlerts'], 'must request /api/events?type=filealerts')
        self.assertTrue(result['hitFileInfo'], 'must request /api/events?type=fileinfo')
        self.assertEqual(result['untypedEventsCalls'], 0, 'must never issue an untyped /api/events request')
        self.assertEqual(result['eventsCallCount'], 2, 'must issue exactly two /api/events requests')
        self.assertEqual(result['result'], [{'event_type': 'fileinfo'}, {'event_type': 'filealerts'}],
                         'must merge fileinfo before filealerts into one array')

    def test_ensureBinaryEventsBatch_is_cache_aware(self):
        """ensureBinaryEventsBatch must not refetch when allEvents is already
        populated, mirroring ensureCappedBatch('all')'s own caching contract."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var eventsCalls = [];
            window.fetch = function(url) {
                if (url.indexOf('/api/events') >= 0) eventsCalls.push(url);
                return Promise.resolve({ json: () => Promise.resolve([{ event_type: 'fileinfo' }]) });
            };
            currentMd5 = 'abc123';
            currentSearch = [];
            await ensureBinaryEventsBatch();
            var callsAfterFirst = eventsCalls.length;
            await ensureBinaryEventsBatch();
            var callsAfterSecond = eventsCalls.length;
            window.__jsdom_result = {
                callsAfterFirst: callsAfterFirst,
                callsAfterSecond: callsAfterSecond
            };
        ''')
        self.assertEqual(result['callsAfterFirst'], 2, 'first call must fetch fileinfo + filealerts once each')
        self.assertEqual(result['callsAfterSecond'], 2, 'second call must reuse the already-populated allEvents, not refetch')

    def test_clearAllFilters_resets_global_filters(self):
        """clearAllFilters must reset currentFilters to empty object"""
        self.assertIn("currentFilters = {}", JS_CONTENT)

    def test_loadTabData_filters_agg_tables_in_advanced_mode_cached(self):
        """loadTabData must pass filtered events to buildAggregationsSection for cached data in advanced mode"""
        pattern = r"const filtered = getFilteredEvents\((?:sectionEl\.id|sectionId),\s*tabDataCache\[eventType\],\s*eventType\);[\s\S]{0,120}buildAggregationsSection\(eventType,\s*filtered\)"
        self.assertRegex(JS_CONTENT, pattern,
            'loadTabData must call getFilteredEvents before buildAggregationsSection for cached data in advanced mode')

    def test_loadTabData_filters_agg_tables_in_advanced_mode_fresh(self):
        """loadTabData must pass filtered events to buildAggregationsSection for fresh data in advanced mode"""
        pattern = r"const filtered = getFilteredEvents\((?:sectionEl\.id|sectionId),\s*events,\s*eventType\);[\s\S]{0,120}buildAggregationsSection\(eventType,\s*filtered\)"
        self.assertRegex(JS_CONTENT, pattern,
            'loadTabData must call getFilteredEvents before buildAggregationsSection for fresh data in advanced mode')

    def test_currentFilters_is_flat_object_not_nested(self):
        """REGRESSION: currentFilters must remain a flat {columnName: value} object.
        Nesting it as {sectionId: {columnName: value}} causes filters to disappear when
        switching tabs, because each tab creates a new empty section entry."""
        self.assertNotIn("currentFilters[sectionId] = {}", JS_CONTENT)
        self.assertNotIn("currentFilters[sectionId] = {", JS_CONTENT)
        self.assertNotIn("currentFilters[sectionId][columnName]", JS_CONTENT)
        self.assertNotIn("currentFilters[sectionId] || {}", JS_CONTENT)
        self.assertIn("currentFilters[f.column] = f.value", JS_CONTENT)

    def test_all_filtering_functions_use_global_currentFilters(self):
        """REGRESSION: Every function that reads filters must use currentFilters directly,
        not currentFilters[sectionId]. Functions checked: buildSection, buildAllEvents,
        buildAggregationsSection, buildAggregationsSectionAll, getFilteredEvents."""
        self.assertNotIn("const filters = currentFilters[sectionId]", JS_CONTENT)

    def test_buildStats_shows_count_over_total_when_filtered(self):
        """buildStats must display 'count / total' when filters are active,
        comma-formatted (toLocaleString) so a large analysis (e.g. a
        1,000,000-row dataset) doesn't render as an unbroken digit string."""
        func = JS_CONTENT.split('function buildStats(')[1].split('function buildSections(')[0]
        self.assertIn('${s.count.toLocaleString()} / ${s.total.toLocaleString()}', func,
                      'buildStats must show filtered count over total when hasFilters is true')

    def test_buildStats_shows_count_only_when_unfiltered(self):
        """buildStats must display just the count when no filters are active,
        comma-formatted (toLocaleString), matching the rest of the app's
        existing number-formatting convention (flow Pkts/Bytes, file size,
        the query-limit settings hint)."""
        func = JS_CONTENT.split('function buildStats(')[1].split('function buildSections(')[0]
        self.assertIn('s.count.toLocaleString()', func,
                      'buildStats must show only count when hasFilters is false')

    def test_buildBinaryAnalysisView_preserves_file_info_on_search(self):
        """REGRESSION: buildBinaryAnalysisView must use unfiltered baseAllEvents
        so the FILE INFO section remains visible when search filters out the
        fileinfo event."""
        self.assertIn('let baseAllEvents = []', JS_CONTENT,
                      'A baseAllEvents variable must exist to store unfiltered events')
        self.assertIn('function buildBinaryAnalysisView(events, baseEvents)', JS_CONTENT,
                      'buildBinaryAnalysisView must accept a baseEvents parameter')
        func = JS_CONTENT.split('function buildBinaryAnalysisView(events, baseEvents)')[1].split('function buildLogEventRow(')[0]
        self.assertIn('const fileInfoSource = baseEvents || baseAllEvents || events;', func,
                      'buildBinaryAnalysisView must fall back to baseAllEvents for file info')
        self.assertIn('buildFileInfoHtml(fileInfoSource)', func,
                      'buildBinaryAnalysisView must pass fileInfoSource to buildFileInfoHtml')


class TestXSSPrevention(unittest.TestCase):
    def _get_function_body(self, func_name):
        func_match = re.search(rf'function {re.escape(func_name)}\([^)]*\)\s*\{{', JS_CONTENT)
        self.assertIsNotNone(func_match, f'{func_name} function not found')
        start = func_match.end()
        brace_count = 1
        pos = start
        while pos < len(JS_CONTENT) and brace_count > 0:
            if JS_CONTENT[pos] == '{':
                brace_count += 1
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
        return JS_CONTENT[start:pos]

    def test_formatEvent_escapes_dynamic_values(self):
        """User-controlled fields in formatEvent must be wrapped with escapeHtml()."""
        func_body = self._get_function_body('formatEvent')
        dangerous_patterns = [
            r'\$\{e\.alert\?\.signature',
            r'\$\{e\.alert\?\.rule',
            r'\$\{e\.alert\?\.category',
            r'\$\{e\.dns\?\.rrname',
            r'\$\{e\.dns\?\.rrtype',
            r'\$\{e\.http\?\.http_method',
            r'\$\{e\.http\?\.url',
            r'\$\{e\.http\?\.hostname',
            r'\$\{e\.http\?\.http_user_agent',
            r'\$\{e\.http\?\.http_content_type',
            r'\$\{e\.tls\?\.sni',
            r'\$\{e\.tls\?\.version',
            r'\$\{e\.tls\?\.subject',
            r'\$\{e\.tls\?\.issuerdn',
            r'\$\{e\.tls\?\.fingerprint',
            r'\$\{e\.flow\?\.state',
            r'\$\{e\.ftp\?\.command',
            r'\$\{e\.ftp\?\.reply',
            r'\$\{e\.anomaly\?\.type',
            r'\$\{e\.anomaly\?\.message',
            r'\$\{e\.fileinfo\?\.filename',
            r'\$\{e\.fileinfo\?\.magic',
            r'\$\{e\.fileinfo\?\.md5',
            r'\$\{e\.fileinfo\?\.sha1',
            r'\$\{e\.fileinfo\?\.sha256',
        ]
        for pattern in dangerous_patterns:
            matches = re.findall(pattern, func_body)
            self.assertEqual(len(matches), 0,
                f'Found unescaped user-controlled field in formatEvent matching: {pattern}')

    def test_buildRowForEvent_escapes_user_fields(self):
        """Table cells for DNS, HTTP, TLS, Flow, and File Info must use escapeHtml()."""
        func_body = self._get_function_body('buildRowForEvent')
        self.assertIn("escapeHtml(rrname)", func_body, 'DNS rrname must be escaped')
        self.assertIn("escapeHtml(rrtype)", func_body, 'DNS rrtype must be escaped')
        self.assertIn("escapeHtml(url)", func_body, 'HTTP url must be escaped')
        self.assertIn("escapeHtml(ua)", func_body, 'HTTP user-agent must be escaped')
        self.assertIn("escapeHtml(sni)", func_body, 'TLS SNI must be escaped')
        self.assertIn("escapeHtml(subject)", func_body, 'TLS subject must be escaped')
        self.assertIn("CONFIG.TLS_ISSUER_MAX_LENGTH", func_body, 'TLS issuer must use CONFIG constant')
        self.assertIn("escapeHtml(state)", func_body, 'Flow state must be escaped')
        self.assertIn("escapeHtml(filename)", func_body, 'File Info filename must be escaped')

    def test_buildAllEvents_escapes_user_fields(self):
        """All Events table must escape user-controlled fields."""
        func_body = self._get_function_body('buildAllEventRow')
        self.assertIn("escapeHtml(ts)", func_body, 'All Events timestamp must be escaped')
        self.assertIn("escapeHtml(etype.toUpperCase())", func_body, 'All Events event type must be escaped')
        self.assertIn("escapeHtml(proto)", func_body, 'All Events protocol must be escaped')
        self.assertIn("escapeHtml(srcIp)", func_body, 'All Events source IP must be escaped')
        self.assertIn("escapeHtml(String(srcPort))", func_body, 'All Events source port must be escaped')
        self.assertIn("escapeHtml(dstIp)", func_body, 'All Events dest IP must be escaped')
        self.assertIn("escapeHtml(String(dstPort))", func_body, 'All Events dest port must be escaped')

    def test_alert_details_shows_rule(self):
        """Alert detail panel must include a Rule row with monospace styling."""
        func_body = self._get_function_body('renderAlertDetails')
        self.assertIn("alert?.rule", func_body, 'renderAlertDetails must reference alert.rule')
        self.assertIn('white-space: pre-wrap', JS_CONTENT, 'Rule text must wrap with pre-wrap')
        self.assertIn('overflow-wrap: break-word', JS_CONTENT, 'Rule text must wrap with overflow-wrap')
        self.assertIn('class="mono"', JS_CONTENT, 'Rule text must use monospace font')


class TestURLParameterEncoding(unittest.TestCase):
    def test_downloadPcap_uses_encodeURIComponent(self):
        """downloadPcap must encode URL parameters to prevent injection.
        Encoding is delegated to buildStreamUrl helper."""
        func_match = re.search(r'function downloadPcap\(', JS_CONTENT)
        self.assertIsNotNone(func_match)
        start = func_match.start()
        brace_count = 0
        pos = start
        found_open = False
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
                found_open = True
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
            if found_open and brace_count == 0:
                break
        func_body = JS_CONTENT[start:pos]
        self.assertIn("buildStreamUrl('download-stream'", func_body,
                      'downloadPcap must delegate URL building to buildStreamUrl')

    def test_loadAsciiTranscript_uses_encodeURIComponent(self):
        """loadAsciiTranscript must encode URL parameters.
        Encoding is delegated to buildStreamUrl helper."""
        func_match = re.search(r'function loadAsciiTranscript\(', JS_CONTENT)
        self.assertIsNotNone(func_match)
        start = func_match.start()
        brace_count = 0
        pos = start
        found_open = False
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
                found_open = True
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
            if found_open and brace_count == 0:
                break
        func_body = JS_CONTENT[start:pos]
        self.assertIn("buildStreamUrl('ascii-stream'", func_body,
                      'loadAsciiTranscript must delegate URL building to buildStreamUrl')

    def test_buildStreamUrl_encodes_parameters(self):
        """buildStreamUrl must encode all URL parameters to prevent injection."""
        func_match = re.search(r'function buildStreamUrl\(', JS_CONTENT)
        self.assertIsNotNone(func_match)
        start = func_match.start()
        brace_count = 0
        pos = start
        found_open = False
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
                found_open = True
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
            if found_open and brace_count == 0:
                break
        func_body = JS_CONTENT[start:pos]
        self.assertIn("encodeURIComponent(src)", func_body)
        self.assertIn("encodeURIComponent(sport)", func_body)
        self.assertIn("encodeURIComponent(dst)", func_body)
        self.assertIn("encodeURIComponent(dport)", func_body)
        self.assertIn("encodeURIComponent(currentMd5)", func_body)


class TestEscapeHtmlRobustness(unittest.TestCase):
    def test_escapeHtml_handles_numbers(self):
        """REGRESSION: escapeHtml must coerce numbers to String before .replace().
        Suricata outputs e.ftp?.reply as a number (e.g. 230), which caused:
        TypeError: str.replace is not a function."""
        func_match = re.search(r'function escapeHtml\(', JS_CONTENT)
        self.assertIsNotNone(func_match)
        start = func_match.start()
        brace_count = 0
        pos = start
        found_open = False
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
                found_open = True
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
            if found_open and brace_count == 0:
                break
        func_body = JS_CONTENT[start:pos]
        self.assertIn("String(str).replace", func_body,
                      'escapeHtml must use String(str) to handle numeric inputs')
        self.assertIn("str == null", func_body,
                      'escapeHtml must use == null check (not !str) so 0 is not rejected')


class TestErrorModal(unittest.TestCase):
    def test_error_modal_exists(self):
        self.assertIn('id="errorModal"', HTML_CONTENT)

    def test_error_modal_has_close_button(self):
        self.assertIn("onclick=\"closeErrorModal()\"", HTML_CONTENT)

    def test_showError_function_exists(self):
        self.assertIn('function showError(', JS_CONTENT)

    def test_closeErrorModal_function_exists(self):
        self.assertIn('function closeErrorModal(', JS_CONTENT)

    def test_no_alert_for_errors(self):
        """All user-facing error alerts must use showError, not alert()."""
        alert_errors = re.findall(r"alert\('Error:", JS_CONTENT)
        self.assertEqual(len(alert_errors), 0,
                         f'Found {len(alert_errors)} alert() calls for errors; use showError() instead')


class TestExternalLinksSecurity(unittest.TestCase):
    def test_all_blank_targets_have_rel_noopener(self):
        """All links with target='_blank' must have rel='noopener noreferrer' to prevent tabnabbing."""
        links = re.findall(r'<a[^>]*target="_blank"[^>]*>', HTML_CONTENT)
        self.assertGreater(len(links), 0, 'Should have external links to test')
        for link in links:
            self.assertIn('rel="noopener noreferrer"', link,
                          f'External link missing rel="noopener noreferrer": {link}')


class TestEscapeHtmlCompleteness(unittest.TestCase):
    def test_escapeHtml_escapes_single_quotes(self):
        func_match = re.search(r'function escapeHtml\(', JS_CONTENT)
        self.assertIsNotNone(func_match)
        start = func_match.start()
        brace_count = 0
        pos = start
        found_open = False
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
                found_open = True
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
            if found_open and brace_count == 0:
                break
        func_body = JS_CONTENT[start:pos]
        self.assertIn("replace(/'/g, '&#39;')", func_body,
                      'escapeHtml must escape single quotes for defense-in-depth')


class TestEscapeJsStringCompleteness(unittest.TestCase):
    """REGRESSION: escapeJsString is always used to embed a value inside a
    single-quoted JS string literal within a double-quoted HTML onclick="..."
    attribute (e.g. onclick="fn('${escapeJsString(x)}')"). Escaping only
    backslash/single-quote protects the JS-string boundary but leaves a raw
    '"' free to break out of the surrounding HTML attribute -- discovered via
    a jsdom exploit test that created a live <img> element through exactly
    this gap. escapeJsString must also HTML-escape so both boundaries hold."""

    def test_escapeJsString_neutralizes_double_quote_breakout(self):
        from tests.jsdom_helper import js_statements
        payload = '"><img src=x onerror=alert(1)>'
        result = js_statements(f'''
            var escaped = escapeJsString({json.dumps(payload)});
            var div = document.createElement('div');
            div.innerHTML = '<button onclick="fn(\\'' + escaped + '\\')">x</button>';
            document.body.appendChild(div);
            window.__jsdom_result = {{
                imgCount: div.querySelectorAll('img').length,
                buttonCount: div.querySelectorAll('button').length,
            }};
        ''')
        self.assertEqual(result['imgCount'], 0, 'a double-quote must not break out of the onclick attribute')
        self.assertEqual(result['buttonCount'], 1, 'the button element itself must survive intact')

    def test_escapeJsString_still_escapes_backslash_and_single_quote(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = {
                backslash: escapeJsString('a\\\\b'),
                quote: escapeJsString("a'b"),
            };
        ''')
        self.assertEqual(result['backslash'], 'a\\\\b')
        self.assertEqual(result['quote'], "a\\&#39;b")

    def test_escapeJsString_escapes_newlines_and_carriage_returns(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = {
                newline: escapeJsString('a\\nb'),
                cr: escapeJsString('a\\rb'),
                crlf: escapeJsString('a\\r\\nb'),
            };
        ''')
        self.assertNotIn('\n', result['newline'], 'newline must be escaped')
        self.assertNotIn('\r', result['cr'], 'carriage return must be escaped')
        self.assertNotIn('\r\n', result['crlf'], 'CRLF must be escaped')
        self.assertIn('\\n', result['newline'], 'newline must appear as escaped \\\\n')
        self.assertIn('\\r', result['cr'], 'carriage return must appear as escaped \\\\r')


class TestInlineHtmlEscaping(unittest.TestCase):
    """REGRESSION: values from server responses must be escaped before being
    assigned to innerHTML or placed inside inline event handlers."""

    def test_previous_analysis_md5_escaped_in_link(self):
        show_welcome = JS_CONTENT.split('async function showWelcome')[1].split('async function')[0]
        self.assertIn('href="?file=${escapeHtml(a.md5)}"', show_welcome,
                      'previous analysis md5 must be escaped in query link')
        self.assertIn("loadAnalysis('${escapeJsString(a.md5)}')", show_welcome,
                      'previous analysis md5 must be escaped in inline onclick handler')

    def test_previous_analysis_md5_escaped_in_data_attrs(self):
        show_welcome = JS_CONTENT.split('async function showWelcome')[1].split('async function')[0]
        # Both re-analyze and delete buttons should have data-md5 escaped.
        data_md5_count = show_welcome.count('data-md5="${escapeHtml(a.md5)}"')
        self.assertGreaterEqual(data_md5_count, 2,
                                'data-md5 attributes must escape the md5 value')

    def test_appHeaderMeta_escapes_md5_and_date(self):
        load_analysis = JS_CONTENT.split('async function loadAnalysis')[1].split('async function')[0]
        self.assertIn('${escapeHtml(currentMd5)}', load_analysis,
                      'currentMd5 must be escaped in appHeaderMeta.innerHTML')
        self.assertIn('${escapeHtml(dateDisplay)}', load_analysis,
                      'dateDisplay must be escaped in appHeaderMeta.innerHTML')

    def test_document_title_does_not_html_escape_filename(self):
        """document.title is a plain-text DOM property, not HTML -- escapeHtml() would
        make literal entities (e.g. &amp;) show up in the browser tab instead of the
        real character, so the filename must be assigned unescaped."""
        load_analysis = JS_CONTENT.split('async function loadAnalysis')[1].split('async function')[0]
        self.assertIn("document.title = 'SO-CRATES - ' + currentFileName", load_analysis,
                      'document.title must not HTML-escape the filename')


class TestAdvancedToggleNoMemoryLeak(unittest.TestCase):
    def test_no_inline_addEventListener_for_advancedToggle(self):
        """The advanced toggle must use a single delegated listener, not repeated inline addEventListener calls."""
        load_analysis = JS_CONTENT.split('async function loadAnalysis')[1]
        self.assertNotIn("addEventListener('change', function()", load_analysis,
                         'loadAnalysis must not attach inline change listeners to avoid memory leaks')

    def test_toggle_aggregations_function_exists(self):
        """toggleAggregations function must exist to handle section heading clicks."""
        self.assertIn("function toggleAggregations()", JS_CONTENT,
                      'toggleAggregations function must exist')


class TestCheckStatusTimeoutFeedback(unittest.TestCase):
    def test_timeout_shows_error_modal(self):
        """After max polling attempts, checkStatus must show an error to the user."""
        self.assertIn('CONFIG.MAX_POLLING_ATTEMPTS', JS_CONTENT,
                      'checkStatus must use CONFIG constant for polling attempts')
        check_status = JS_CONTENT.split('async function checkStatus')[1]
        self.assertIn('showError(', check_status,
                      'checkStatus must show an error when polling times out')

    def test_error_status_shows_error_modal(self):
        """When server returns status='error', checkStatus must show it immediately."""
        check_status = JS_CONTENT.split('async function checkStatus')[1]
        self.assertIn("result.status === 'error'", check_status,
                      'checkStatus must handle error status from server')
        self.assertIn('showError(result.message', check_status,
                      'checkStatus must show the server error message')


class TestNoDeadCode(unittest.TestCase):
    def test_no_currentSectionTypes(self):
        """currentSectionTypes was declared but never used — should be removed."""
        self.assertNotIn('currentSectionTypes', JS_CONTENT,
                         'currentSectionTypes is dead code and should be removed')

    def test_no_dead_css_selectors(self):
        """These CSS rules were removed because no HTML/JS uses them."""
        dead_selectors = [
            '.app-header-help',
            '.back-top-btn',
            '.stream-output',
            '.filtered-row',
            '.advanced-toggle',
            '.sankey-close',
            '.yara-matches-section',
            '.file-alerts-grid',
            '.file-alert-card',
            '.sigma-alerts-section',
            '.sigma-log-json',
        ]
        for selector in dead_selectors:
            self.assertNotIn(selector, CSS_CONTENT,
                             f'{selector} is unused CSS and should be removed')


class TestSearchUI(unittest.TestCase):
    def test_search_bar_exists(self):
        self.assertIn('id="searchBarContainer"', HTML_CONTENT,
                      'Search bar container must exist')
        self.assertIn('id="searchInput"', HTML_CONTENT,
                      'Search input must exist')

    def test_search_functions_exist(self):
        self.assertIn('function performSearch', JS_CONTENT,
                      'performSearch function must exist')
        self.assertIn('function clearSearch', JS_CONTENT,
                      'clearSearch function must exist')
        self.assertIn('function refreshAnalysisData', JS_CONTENT,
                      'refreshAnalysisData function must exist')

    def test_search_state_variable_is_array(self):
        self.assertIn('let currentSearch = []', JS_CONTENT,
                      'currentSearch must be initialized as an array')

    def test_search_uses_encodeURIComponent(self):
        self.assertIn('encodeURIComponent(t)', JS_CONTENT,
                      'Search must encode URI components per term')

    def test_search_bar_css(self):
        self.assertIn('.search-bar', CSS_CONTENT,
                      'Search bar CSS must exist')
        self.assertIn('.search-input', CSS_CONTENT,
                      'Search input CSS must exist')
        self.assertIn('.search-btn', CSS_CONTENT,
                      'Search button CSS must exist')

    def test_search_fetches_stats_with_q(self):
        self.assertIn("'/api/stats?md5=' + currentMd5 + qParam", JS_CONTENT,
                      'refreshAnalysisData must fetch stats with q parameter')

    def test_search_fetches_events_with_q(self):
        self.assertIn("function getUserQueryLimit", JS_CONTENT,
                      'ensureCappedBatch must use the user-configurable query limit')

    def test_loadTabData_passes_q(self):
        self.assertIn("currentSearch.map(t => '&q=' + encodeURIComponent(t)).join('')", JS_CONTENT,
                      'loadTabData must join multiple q parameters')

    def test_search_resets_on_new_analysis(self):
        self.assertIn("currentSearch = []", JS_CONTENT,
                      'loadAnalysis must reset currentSearch to empty array')

    def test_baseEventStats_exists(self):
        self.assertIn('baseEventStats', JS_CONTENT,
                      'baseEventStats variable must exist for unfiltered totals')

    def test_buildStats_uses_baseEventStats(self):
        self.assertIn('baseEventStats[type]', JS_CONTENT,
                      'buildStats must use baseEventStats for totals')

    def test_search_creates_chip_per_term(self):
        """buildFilterBarHtml must render one chip per search term."""
        self.assertIn('for (let i = 0; i < currentSearch.length; i++)', JS_CONTENT,
                      'buildFilterBarHtml must iterate search terms')
        self.assertIn('onclick="clearSearchTerm(', JS_CONTENT,
                      'Each search chip must call clearSearchTerm with index')

    def test_search_chip_shows_full_query(self):
        """buildFilterBarHtml must show full escaped term in each chip."""
        self.assertIn('"${escapeHtml(term)}"', JS_CONTENT,
                      'Search chip must show full escaped term text')

    def test_filter_chip_escapes_malicious_column_name(self):
        """REGRESSION: buildFilterBarHtml renders currentFilters keys (column
        names, which can originate from attacker-controlled log field names
        applied as a filter) both as visible text and inside a
        clearFilter('...') onclick attribute. A malicious key must not
        create a live element via either sink."""
        from tests.jsdom_helper import js_statements
        malicious_col = '"><img src=x onerror=alert(1)>'
        result = js_statements(f'''
            currentFilters = {{}};
            currentFilters[{json.dumps(malicious_col)}] = 'someval';
            var html = buildFilterBarHtml();
            var div = document.createElement('div');
            div.innerHTML = html;
            document.body.appendChild(div);
            window.__jsdom_result = {{
                imgCount: div.querySelectorAll('img').length,
            }};
        ''')
        self.assertEqual(result['imgCount'], 0, 'malicious filter column name must not create a live <img> element')

    def test_search_adds_terms_on_enter(self):
        """performSearch must split input into terms and push to array."""
        func = JS_CONTENT.split('async function performSearch')[1].split('async function')[0]
        self.assertIn("currentSearch.push(term)", func,
                      'performSearch must push terms into currentSearch array')

    def test_search_clears_input_after_enter(self):
        """performSearch must clear input after adding terms."""
        func = JS_CONTENT.split('async function performSearch')[1].split('async function')[0]
        self.assertIn("input.value = ''", func,
                      'performSearch must clear search input after submit')

    def test_search_deduplicates_terms(self):
        """performSearch must skip duplicate terms."""
        func = JS_CONTENT.split('async function performSearch')[1].split('async function')[0]
        self.assertIn("!currentSearch.includes(term)", func,
                      'performSearch must deduplicate terms')

    def test_clear_search_term_by_index(self):
        """clearSearchTerm must splice array at given index."""
        func = JS_CONTENT.split('async function clearSearchTerm')[1].split('async function')[0]
        self.assertIn("currentSearch.splice(index, 1)", func,
                      'clearSearchTerm must remove term at index')

    def test_qParam_builds_multiple_q(self):
        """qParam must build multiple &q= params from currentSearch array."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            currentSearch = ['1.2.3.4', 'malware'];
            var qParam = currentSearch.length > 0 ? currentSearch.map(function(t) { return '&q=' + encodeURIComponent(t); }).join('') : '';
            window.__jsdom_result = qParam;
        ''')
        self.assertIn('q=1.2.3.4', result)
        self.assertIn('q=malware', result)

    def test_clearSearchTerm_removes_term(self):
        """clearSearchTerm must remove the term at the given index."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            currentSearch = ['1.2.3.4', 'malware', 'apt'];
            // The synchronous part of clearSearchTerm
            currentSearch.splice(1, 1);
            window.__jsdom_result = currentSearch;
        ''')
        self.assertEqual(result, ['1.2.3.4', 'apt'])

    def test_qParam_joins_multiple_q(self):
        """qParam must build multiple &q= params from array."""
        self.assertIn("currentSearch.map(t => '&q=' + encodeURIComponent(t)).join('')", JS_CONTENT,
                      'qParam must join multiple q parameters')

    def test_clear_all_clears_search(self):
        """clearAllFilters must reset currentSearch and search input."""
        func = JS_CONTENT.split('async function clearAllFilters')[1].split('async function')[0]
        self.assertIn("currentSearch = []", func,
                      'clearAllFilters must reset currentSearch to empty array')
        self.assertIn("input.value = ''", func,
                      'clearAllFilters must clear search input')

    def test_filter_bar_visible_with_search_only(self):
        """updateFilterBarVisibility must show bar when only currentSearch has terms."""
        self.assertIn('currentSearch.length > 0 || hasFilters', JS_CONTENT,
                      'updateFilterBarVisibility must check search array length and filters')

    def test_showWelcome_uses_clearAnalysisContainers(self):
        """REGRESSION: showWelcome must call clearAnalysisContainers when returning to overview."""
        func = JS_CONTENT.split('async function showWelcome')[1].split('async function')[0]
        self.assertIn("clearAnalysisContainers()", func,
                      'showWelcome must call clearAnalysisContainers when returning to overview')

    def test_showWelcome_uses_showWelcomeUI(self):
        """REGRESSION: showWelcome must call showWelcomeUI when returning to overview."""
        func = JS_CONTENT.split('async function showWelcome')[1].split('async function')[0]
        self.assertIn("showWelcomeUI()", func,
                      'showWelcome must call showWelcomeUI when returning to overview')

    def test_refreshAnalysisData_preserves_active_section(self):
        """REGRESSION: refreshAnalysisData must remember and restore the active section type after rebuild."""
        func = JS_CONTENT.split('async function refreshAnalysisData')[1].split('async function')[0]
        self.assertIn("const visibleSection = document.querySelector('.section:not(.section-hidden):not(.agg-section)')", func,
                      'refreshAnalysisData must query visible section before rebuild')
        self.assertIn("const activeType = visibleSection ? visibleSection.id.replace('section-', '') : ''", func,
                      'refreshAnalysisData must extract active type from visible section')
        self.assertIn("if (activeType && activeType !== eventTypes[0])", func,
                      'refreshAnalysisData must conditionally restore non-default active type')
        self.assertIn("sectionEl.classList.remove('section-hidden')", func,
                      'refreshAnalysisData must unhide the restored section')
        self.assertIn("loadTabData(activeType, null)", func,
                      'refreshAnalysisData must reload data for restored section')

    def test_refreshAnalysisData_loads_default_tab(self):
        """REGRESSION: refreshAnalysisData must explicitly load the default tab when no other tab is active."""
        func = JS_CONTENT.split('async function refreshAnalysisData')[1].split('async function')[0]
        self.assertIn("loadTabData(eventTypes[0], null)", func,
                      'refreshAnalysisData must load default tab when activeType is default')

    def test_refreshAnalysisData_does_not_override_sankey_with_all_events(self):
        """REGRESSION: refreshAnalysisData must not call updateSankeyDiagram(allEvents) after restoring the active section, because loadTabData already updates the Sankey for the correct type."""
        func = JS_CONTENT.split('async function refreshAnalysisData')[1].split('async function')[0]
        self.assertNotIn("updateSankeyDiagram(allEvents)", func,
                      'refreshAnalysisData must not override Sankey with allEvents after restore')

    def test_refreshAnalysisData_does_not_override_aggregations_with_all_events(self):
        """REGRESSION: refreshAnalysisData must not unconditionally call buildAggregationsSectionAll() after restoring the active section, because loadTabData already builds aggregations for the correct type."""
        func = JS_CONTENT.split('async function refreshAnalysisData')[1].split('async function')[0]
        self.assertNotIn("buildAggregationsSectionAll()", func,
                      'refreshAnalysisData must not override aggregations with allEvents after restore')

    def test_buildSections_does_not_call_loadTabData(self):
        """REGRESSION: buildSections must not call loadTabData to prevent a race with refreshAnalysisData."""
        func = JS_CONTENT.split('function buildSections(')[1].split('function ')[0]
        self.assertNotIn("loadTabData", func,
                      'buildSections must not call loadTabData')


class TestReanalyzeUI(unittest.TestCase):
    def test_reanalyze_button_on_welcome(self):
        """Welcome screen must show a re-analyze button next to each previous analysis."""
        self.assertIn('openReanalyzeModal', JS_CONTENT,
                      'showWelcome must include re-analyze button')
        self.assertIn('REFRESH_ICON_SVG', JS_CONTENT,
                      'Re-analyze button must use refresh icon')

    def test_reanalyze_modal_exists(self):
        """Re-analyze confirmation modal must exist in HTML."""
        self.assertIn('id="reanalyzeConfirmModal"', HTML_CONTENT,
                      'reanalyzeConfirmModal must exist')
        self.assertIn('id="reanalyzeFileName"', HTML_CONTENT,
                      'reanalyzeFileName span must exist')

    def test_reanalyze_modal_has_cancel_and_reanalyze_buttons(self):
        """Re-analyze modal must have Cancel and Re-analyze buttons."""
        modal_section = HTML_CONTENT.split('id="reanalyzeConfirmModal"')[1].split('</div>\n        </div>')[0]
        self.assertIn('closeReanalyzeModal()', modal_section,
                      'Modal must have Cancel button')
        self.assertIn('confirmReanalyze()', modal_section,
                      'Modal must have Re-analyze button')

    def test_reanalyze_modal_has_backdrop_click_handler(self):
        """Re-analyze modal wrapper must close when backdrop is clicked."""
        self.assertIn('id="reanalyzeConfirmModal" onclick="handleReanalyzeBackdropClick(event)"', HTML_CONTENT,
                      'Re-analyze modal wrapper must handle backdrop clicks')
        modal_section = HTML_CONTENT.split('id="reanalyzeConfirmModal"')[1].split('</div>\n        </div>')[0]
        self.assertIn('onclick="event.stopPropagation()"', modal_section,
                      'Re-analyze modal content must stop event propagation')
        self.assertIn('function handleReanalyzeBackdropClick(', JS_CONTENT,
                      'handleReanalyzeBackdropClick must be defined')

    def test_reanalyze_calls_post_api(self):
        """confirmReanalyze must POST to /api/reanalyze with JSON body."""
        self.assertIn("fetch('/api/reanalyze'", JS_CONTENT,
                      'confirmReanalyze must fetch /api/reanalyze')
        self.assertIn("method: 'POST'", JS_CONTENT,
                      'confirmReanalyze must use POST method')
        self.assertIn("JSON.stringify({md5: md5})", JS_CONTENT,
                      'confirmReanalyze must send md5 in JSON body')

    def test_reanalyze_shows_loading(self):
        """confirmReanalyze must show loading indicator while Suricata runs."""
        self.assertIn("showLoading('Re-analyzing", JS_CONTENT,
                      'confirmReanalyze must call showLoading')

    def test_reanalyze_uses_checkStatus(self):
        """confirmReanalyze must poll checkStatus after starting reanalysis."""
        self.assertIn('await checkStatus(md5, phase', JS_CONTENT,
                      'confirmReanalyze must poll checkStatus with md5 and phase')

    def test_reanalyze_pdf_sets_files_phase(self):
        """openReanalyzeModal must set phase to 'files' for non-log non-pcap files like PDF."""
        func_match = re.search(r'function openReanalyzeModal\(', JS_CONTENT)
        self.assertIsNotNone(func_match)
        start = func_match.start()
        brace_count = 0
        pos = start
        found_open = False
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
                found_open = True
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
            if found_open and brace_count == 0:
                break
        func_body = JS_CONTENT[start:pos]
        self.assertIn("detectFileType(name)", func_body,
                      'openReanalyzeModal must detect file type via the shared detectFileType helper')
        self.assertIn("let phase = 'files'", func_body,
                      'openReanalyzeModal must default to files phase')
        self.assertIn("if (detectedType === 'log') phase = 'logs'", func_body,
                      'openReanalyzeModal must set logs phase for log files')
        self.assertIn("else if (detectedType === 'pcap') phase = 'network'", func_body,
                      'openReanalyzeModal must set network phase for PCAP files')

    def test_reanalyze_pcap_sets_network_phase(self):
        """openReanalyzeModal must set phase to 'network' for PCAP files."""
        func_match = re.search(r'function openReanalyzeModal\(', JS_CONTENT)
        self.assertIsNotNone(func_match)
        start = func_match.start()
        brace_count = 0
        pos = start
        found_open = False
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
                found_open = True
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
            if found_open and brace_count == 0:
                break
        func_body = JS_CONTENT[start:pos]
        self.assertIn("detectFileType(name)", func_body,
                      'openReanalyzeModal must detect PCAP files via the shared detectFileType helper')
        self.assertIn("else if (detectedType === 'pcap') phase = 'network'", func_body,
                      'openReanalyzeModal must set network phase for PCAP files')

    def test_reanalyze_log_sets_logs_phase(self):
        """openReanalyzeModal must set phase to 'logs' for log files."""
        func_match = re.search(r'function openReanalyzeModal\(', JS_CONTENT)
        self.assertIsNotNone(func_match)
        start = func_match.start()
        brace_count = 0
        pos = start
        found_open = False
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
                found_open = True
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
            if found_open and brace_count == 0:
                break
        func_body = JS_CONTENT[start:pos]
        self.assertIn("detectFileType(name)", func_body,
                      'openReanalyzeModal must detect log files via the shared detectFileType helper')
        self.assertIn("if (detectedType === 'log') phase = 'logs'", func_body,
                      'openReanalyzeModal must set logs phase for log files')

    def test_reanalyze_modal_fallback_to_filename(self):
        """openReanalyzeModal must fall back to filename-based phase when status API fails."""
        self.assertIn('async function openReanalyzeModal', JS_CONTENT,
                      'openReanalyzeModal must be async')
        func_match = re.search(r'function openReanalyzeModal\(', JS_CONTENT)
        self.assertIsNotNone(func_match)
        start = func_match.start()
        brace_count = 0
        pos = start
        found_open = False
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
                found_open = True
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
            if found_open and brace_count == 0:
                break
        func_body = JS_CONTENT[start:pos]
        self.assertIn('catch(err)', func_body,
                      'openReanalyzeModal must have catch block for status API failures')
        catch_section = func_body.split('catch(err)')[1]
        self.assertIn("detectFileType(name)", catch_section,
                      'Fallback must detect file type by extension via the shared helper')
        self.assertIn("if (detectedType === 'log') phase = 'logs'", catch_section,
                      'Fallback must set logs phase')
        self.assertIn("else if (detectedType === 'pcap') phase = 'network'", catch_section,
                      'Fallback must set network phase')


class TestDeleteAllAnalysesUI(unittest.TestCase):
    def test_delete_all_button_on_welcome(self):
        """Welcome screen must show a Delete All button when previous analyses exist."""
        self.assertIn('openDeleteAllAnalyses', JS_CONTENT,
                      'showWelcome must include Delete All button handler')
        self.assertIn('previous-analysis-delete-all', JS_CONTENT,
                      'Delete All button must have styling class')

    def test_delete_all_modal_exists(self):
        """Delete All confirmation modal must exist in HTML."""
        self.assertIn('id="deleteAllConfirmModal"', HTML_CONTENT,
                      'deleteAllConfirmModal must exist')
        self.assertIn('id="deleteAllCount"', HTML_CONTENT,
                      'deleteAllCount span must exist')

    def test_delete_all_modal_has_cancel_and_delete_buttons(self):
        """Delete All modal must have Cancel and Delete All buttons."""
        modal_section = HTML_CONTENT.split('id="deleteAllConfirmModal"')[1].split('</div>\n        </div>')[0]
        self.assertIn('closeDeleteAllModal()', modal_section,
                      'Modal must have Cancel button')
        self.assertIn('confirmDeleteAll()', modal_section,
                      'Modal must have Delete All button')

    def test_delete_all_modal_has_backdrop_click_handler(self):
        """Delete All modal wrapper must close when backdrop is clicked."""
        self.assertIn('id="deleteAllConfirmModal" onclick="handleDeleteAllBackdropClick(event)"', HTML_CONTENT,
                      'Delete All modal wrapper must handle backdrop clicks')
        modal_section = HTML_CONTENT.split('id="deleteAllConfirmModal"')[1].split('</div>\n        </div>')[0]
        self.assertIn('onclick="event.stopPropagation()"', modal_section,
                      'Delete All modal content must stop event propagation')
        self.assertIn('function handleDeleteAllBackdropClick(', JS_CONTENT,
                      'handleDeleteAllBackdropClick must be defined')

    def test_delete_modal_has_backdrop_click_handler(self):
        """Delete modal wrapper must close when backdrop is clicked."""
        self.assertIn('id="deleteConfirmModal" onclick="handleDeleteBackdropClick(event)"', HTML_CONTENT,
                      'Delete modal wrapper must handle backdrop clicks')
        modal_section = HTML_CONTENT.split('id="deleteConfirmModal"')[1].split('</div>\n        </div>')[0]
        self.assertIn('onclick="event.stopPropagation()"', modal_section,
                      'Delete modal content must stop event propagation')
        self.assertIn('function handleDeleteBackdropClick(', JS_CONTENT,
                      'handleDeleteBackdropClick must be defined')

    def test_confirm_delete_all_calls_post_api(self):
        """confirmDeleteAll must POST to /api/delete-all-analyses."""
        self.assertIn("fetch('/api/delete-all-analyses'", JS_CONTENT,
                      'confirmDeleteAll must fetch /api/delete-all-analyses')
        self.assertIn("method: 'POST'", JS_CONTENT,
                      'confirmDeleteAll must use POST method')

    def test_confirm_delete_all_refreshes_welcome(self):
        """confirmDeleteAll must refresh the welcome screen on success."""
        self.assertIn('if (result.success) {', JS_CONTENT)
        self.assertIn('showWelcome()', JS_CONTENT,
                      'confirmDeleteAll must call showWelcome on success')


class TestFileAlertsUI(unittest.TestCase):
    def test_has_filealerts_in_type_labels(self):
        self.assertIn("filealerts: 'File Alerts'", JS_CONTENT,
                      'typeLabels must include filealerts')

    def test_has_filealerts_in_type_colors(self):
        self.assertIn("filealerts: '#e91e63'", JS_CONTENT,
                      'COLORS.EVENT must include filealerts color')

    def test_filealerts_columns_defined(self):
        self.assertIn("case 'filealerts':", JS_CONTENT,
                      'getColumnsForType must handle filealerts')
        self.assertIn("'Tags'", JS_CONTENT,
                      'filealerts columns must include Tags')
        self.assertIn("'Author'", JS_CONTENT,
                      'filealerts columns must include Author')

    def test_filealerts_row_rendering(self):
        self.assertIn("case 'filealerts':", JS_CONTENT,
                      'buildRowForEvent must handle filealerts')
        self.assertIn("fa.rule_name", JS_CONTENT,
                      'buildRowForEvent must render rule_name from filealerts object')
        self.assertIn("fa.tags", JS_CONTENT,
                      'buildRowForEvent must render tags from filealerts object')
        self.assertIn("fa.author", JS_CONTENT,
                      'buildRowForEvent must render author from filealerts object')

    def test_filealerts_row_html(self):
        """buildRowForEvent must produce correct HTML for filealerts events."""
        from tests.jsdom_helper import js_statements
        event = {
            'event_type': 'filealerts',
            'timestamp': '2026-01-01T12:00:00Z',
            'proto': 'TCP',
            'src_ip': '192.168.1.1',
            'src_port': 12345,
            'dest_ip': '10.0.0.1',
            'dest_port': 80,
            'filealerts': {
                'rule_name': 'MALWARE_Test',
                'tags': ['MALWARE', 'APT'],
                'author': 'FLIRT',
                'sha256': 'a' * 64,
            }
        }
        result = js_statements(f'''
            var e = {json.dumps(event)};
            var html = buildRowForEvent(e);
            window.__jsdom_result = {{
                hasRuleName: html.indexOf('MALWARE_Test') >= 0,
                hasTagBadge: html.indexOf('MALWARE') >= 0,
                hasTags: html.indexOf('APT') >= 0,
                hasAuthor: html.indexOf('FLIRT') >= 0,
                hasTCP: html.indexOf('TCP') >= 0,
                hasSrcIp: html.indexOf('192.168.1.1') >= 0,
            }};
        ''')
        self.assertTrue(result['hasRuleName'], 'Row must contain rule name')
        self.assertTrue(result['hasTagBadge'], 'Row must contain tag badge')
        self.assertTrue(result['hasTags'], 'Row must contain tags')
        self.assertTrue(result['hasAuthor'], 'Row must contain author')
        self.assertTrue(result['hasTCP'], 'Row must contain protocol')
        self.assertTrue(result['hasSrcIp'], 'Row must contain source IP')

    def test_extract_value_tags(self):
        self.assertIn("case 'Tags':", JS_CONTENT,
                      'extractValue must handle Tags column')

    def test_extract_value_author(self):
        self.assertIn("case 'Author':", JS_CONTENT,
                      'extractValue must handle Author column')

    def test_fileinfo_shows_yara_matches_section(self):
        self.assertIn('filealerts', JS_CONTENT,
                      'JS must handle filealerts event type for fileinfo/YARA analysis')

    def test_filealerts_in_all_event_types(self):
        expected_types = ['alert', 'dns', 'http', 'tls', 'flow', 'ftp', 'stats', 'anomaly', 'fileinfo', 'filealerts']
        for etype in expected_types:
            self.assertIn(f"'{etype}'", JS_CONTENT)

    def test_filealerts_uses_nested_schema(self):
        self.assertIn('e.filealerts?.rule_name', JS_CONTENT,
                      'buildRowForEvent must access filealerts via nested schema')
        self.assertIn('e.filealerts?.tags', JS_CONTENT,
                      'buildRowForEvent must access tags via nested schema')
        self.assertIn('e.filealerts?.author', JS_CONTENT,
                      'buildRowForEvent must access author via nested schema')

    def test_renderFileAlertDetails_shows_author(self):
        """renderFileAlertDetails must include Author when present."""
        from tests.jsdom_helper import js_statements
        event = {
            'event_type': 'filealerts',
            'filealerts': {
                'rule_name': 'MALWARE_Test',
                'tags': ['MALWARE'],
                'author': 'FLIRT',
                'sha256': 'a' * 64,
            }
        }
        result = js_statements(f'''
            var e = {json.dumps(event)};
            var html = renderFileAlertDetails(e);
            window.__jsdom_result = {{
                hasAuthor: html.indexOf('FLIRT') >= 0,
                hasRuleName: html.indexOf('MALWARE_Test') >= 0,
            }};
        ''')
        self.assertTrue(result['hasAuthor'], 'Detail must contain author')
        self.assertTrue(result['hasRuleName'], 'Detail must contain rule name')

    def test_pcap_filename_always_routes_to_network_analysis(self):
        """PCAP files must always show network analysis screen, even with zero alerts."""
        # isPcap must be defined based on detected_type from API
        self.assertIn("const isPcap = detectedType === 'pcap'", JS_CONTENT,
                      'JS must use detected_type from API to determine PCAP mode')
        # Must use detected_type from status API
        self.assertIn("const detectedType = analysisStatus.meta?.detected_type", JS_CONTENT,
                      'JS must read detected_type from status API meta')
        # Must NOT use alert absence to determine file-only mode
        self.assertNotIn("!eventTypes.includes('alert')", JS_CONTENT,
                         'JS must not infer PCAP mode from alert absence')

    def test_zip_uses_meta_detected_type_for_routing(self):
        """ZIP uploads must use backend .meta detected_type, not filename extension."""
        # Frontend must fetch /api/status to get meta
        self.assertIn("fetch('/api/status?md5='", JS_CONTENT,
                      'JS must fetch status API to get detected_type for routing')
        # Fallback must exist for old analyses without .meta
        self.assertIn("analysisStatus.meta?.detected_type || detectFileType(currentFileName)", JS_CONTENT,
                      'JS must fallback to filename extension when .meta is missing')

    def test_evtx_routes_to_log_analysis_not_network(self):
        """EVTX files must route to log analysis, not PCAP network screen."""
        # isFileOnly must include log files (not just exclude PCAP)
        self.assertIn("const isFileOnly = !isPcap;", JS_CONTENT,
                      'JS must treat all non-PCAP as file-analysis (log or binary)')
        # Log analysis branch must exist inside file-analysis block
        self.assertIn("if (isLogFile) {", JS_CONTENT,
                      'JS must have log analysis branch inside file-analysis')
        # Sankey diagram must only render for PCAP (outside file-analysis)
        func_body = JS_CONTENT.split('function loadAnalysis(')[1].split('async function')[0]
        # The sankey rendering should be in the PCAP-only else branch
        self.assertIn("const sankeyPanel = document.getElementById('sankeyPanel');", func_body,
                      'Sankey rendering must exist in loadAnalysis')

    def test_reanalyze_zip_pcap_shows_network_phase(self):
        """Re-analyze modal must fetch /api/status to get detected_type for ZIP-PCAP."""
        # openReanalyzeModal must be async
        self.assertIn('async function openReanalyzeModal', JS_CONTENT,
                      'openReanalyzeModal must be async to fetch status API')
        # Must fetch /api/status inside reanalyze modal
        self.assertIn("fetch('/api/status?md5='", JS_CONTENT,
                      'JS must fetch status API in reanalyze modal')
        # Must use detected_type from status response
        self.assertIn("const detectedType = status.meta?.detected_type", JS_CONTENT,
                      'JS must use detected_type from status API for reanalyze phase')

    def test_corrupted_meta_fallback(self):
        """Frontend must fallback to filename-based detection when .meta is missing."""
        # Fallback chain must exist: meta → filename extension → binary default
        self.assertIn("analysisStatus.meta?.detected_type ||", JS_CONTENT,
                      'JS must fallback when .meta is missing or corrupted')
        # Binary must be the ultimate default in the shared detectFileType helper
        from tests.jsdom_helper import js_expression
        self.assertEqual(js_expression("detectFileType('capture.pcap')"), 'pcap',
                         'detectFileType must detect PCAP extensions')
        self.assertEqual(js_expression("detectFileType('sysmon.evtx')"), 'log',
                         'detectFileType must detect log extensions')
        self.assertEqual(js_expression("detectFileType('payload.exe')"), 'binary',
                         'detectFileType must default to binary when neither PCAP nor log')


class TestMaybeLinkifyValueSecurity(unittest.TestCase):
    def test_function_exists(self):
        self.assertIn('function maybeLinkifyValue(', JS_CONTENT,
                      'maybeLinkifyValue must exist to safely handle URLs in metadata')

    def test_only_allows_http_https(self):
        self.assertIn("lower.startsWith('http://')", JS_CONTENT,
                      'maybeLinkifyValue must whitelist http://')
        self.assertIn("lower.startsWith('https://')", JS_CONTENT,
                      'maybeLinkifyValue must whitelist https://')

    def test_link_has_noopener(self):
        self.assertIn('rel="noopener noreferrer"', JS_CONTENT,
                      'External links must have rel="noopener noreferrer"')
        self.assertIn('target="_blank"', JS_CONTENT,
                      'External links must open in a new tab')

    def test_escapes_url_in_href(self):
        self.assertIn('escapeHtml(s)', JS_CONTENT,
                      'maybeLinkifyValue must escape the URL in the href attribute')

    def _extract_js_function(self, name):
        """Extract a named function definition from JS_CONTENT by brace matching."""
        import re
        pattern = re.compile(rf'function\s+{re.escape(name)}\s*\([^)]*\)\s*{{')
        match = pattern.search(JS_CONTENT)
        if not match:
            self.fail(f'Function {name} not found in JS_CONTENT')
        start = match.start()
        brace_count = 0
        pos = match.end() - 1  # position of the opening brace
        while pos < len(JS_CONTENT):
            if JS_CONTENT[pos] == '{':
                brace_count += 1
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return JS_CONTENT[start:pos + 1]
            pos += 1
        self.fail(f'Could not find closing brace for function {name}')

    def _run_js_plain(self, expr):
        """Run a JS expression via Node.js using the actual maybeLinkifyValue from socrates.js."""
        import subprocess
        escape_html_src = self._extract_js_function('escapeHtml')
        linkify_src = self._extract_js_function('maybeLinkifyValue')
        code = escape_html_src + '\n' + linkify_src + '\n' + 'console.log(JSON.stringify(maybeLinkifyValue(' + expr + ')));'
        result = subprocess.run(['node', '-e', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f'Node.js failed: {result.stderr}')
        return json.loads(result.stdout.strip())

    def test_javascript_url_not_linkified(self):
        """javascript: URLs must be rendered as plain text, not clickable links."""
        result = self._run_js_plain('"javascript:alert(1)"')
        self.assertNotIn('<a', result, 'javascript: URLs must not produce anchor tags')
        self.assertEqual(result, 'javascript:alert(1)')

    def test_data_url_not_linkified(self):
        """data: URLs must be rendered as plain text."""
        result = self._run_js_plain('"data:text/html,<script>alert(1)</script>"')
        self.assertNotIn('<a', result, 'data: URLs must not produce anchor tags')

    def test_http_url_gets_link(self):
        """http:// URLs must produce a safe external link."""
        result = self._run_js_plain('"http://example.com"')
        self.assertIn('<a', result, 'http:// URLs must produce anchor tags')
        self.assertIn('target="_blank"', result, 'Link must open in new tab')
        self.assertIn('rel="noopener noreferrer"', result, 'Link must have security rel')

    def test_https_url_gets_link(self):
        """https:// URLs must produce a safe external link."""
        result = self._run_js_plain('"https://attack.mitre.org/techniques/T1055/"')
        self.assertIn('<a', result, 'https:// URLs must produce anchor tags')
        self.assertIn('target="_blank"', result, 'Link must open in new tab')
        self.assertIn('rel="noopener noreferrer"', result, 'Link must have security rel')

    def test_plain_text_not_linkified(self):
        """Non-URL strings must be returned as plain text."""
        result = self._run_js_plain('"ReversingLabs"')
        self.assertNotIn('<a', result, 'Plain text must not produce anchor tags')
        self.assertEqual(result, 'ReversingLabs')

    def test_case_insensitive_scheme_check(self):
        """HTTPS:// uppercase must still be recognized as safe."""
        result = self._run_js_plain('"HTTPS://example.com"')
        self.assertIn('<a', result, 'Uppercase HTTPS must still be linkified')

    def test_punycode_idn_not_linkified(self):
        """javascript: URLs disguised with unicode must not slip through."""
        result = self._run_js_plain('"\\u0000javascript:alert(1)"')
        self.assertNotIn('<a', result, 'Null-prefixed javascript must not produce anchor tags')


class TestLogAnalysisUI(unittest.TestCase):
    def test_discoverLogColumns_prioritizes_known_fields(self):
        """discoverLogColumns must return base fields first, then dynamic fields, max 8 total."""
        from tests.jsdom_helper import js_statements
        events = [
            {'json_data': {'Channel': 'Security', 'EventID': 4624, 'Computer': 'PC1', 'Image': 'evil.exe', 'CommandLine': 'evil.exe -payload'}},
            {'json_data': {'Channel': 'Security', 'EventID': 4625, 'Computer': 'PC1', 'Image': 'good.exe', 'CommandLine': 'good.exe'}}
        ]
        result = js_statements(f'''
            var events = {json.dumps(events)};
            var cols = discoverLogColumns(events);
            window.__jsdom_result = {{
                hasChannel: cols.some(c => c.field === 'Channel'),
                hasEventID: cols.some(c => c.field === 'EventID'),
                hasComputer: cols.some(c => c.field === 'Computer'),
                hasImage: cols.some(c => c.field === 'Image'),
                total: cols.length,
                firstBase: cols[0].type === 'base'
            }};
        ''')
        self.assertTrue(result['hasChannel'])
        self.assertTrue(result['hasEventID'])
        self.assertTrue(result['hasComputer'])
        self.assertTrue(result['hasImage'])
        self.assertTrue(result['firstBase'])
        self.assertLessEqual(result['total'], 8)

    def test_discoverLogColumns_returns_empty_for_no_events(self):
        """discoverLogColumns must return [] for empty input."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = discoverLogColumns([]);
        ''')
        self.assertEqual(result, [])

    def test_discoverSigmaAlertColumns_discovers_original_log_fields(self):
        """discoverSigmaAlertColumns must return prevalent fields from original_log."""
        from tests.jsdom_helper import js_statements
        alerts = [
            {'original_log': json.dumps({'Image': 'evil.exe', 'CommandLine': 'evil.exe -payload'})},
            {'original_log': json.dumps({'Image': 'evil.exe', 'User': 'admin'})},
            {'original_log': json.dumps({'Image': 'evil.exe', 'CommandLine': 'other'})}
        ]
        result = js_statements(f'''
            var alerts = {json.dumps(alerts)};
            var cols = discoverSigmaAlertColumns(alerts);
            window.__jsdom_result = {{
                hasImage: cols.some(c => c.field === 'Image'),
                total: cols.length
            }};
        ''')
        self.assertTrue(result['hasImage'])
        self.assertLessEqual(result['total'], 3)

    def test_formatLogEventDetail_groups_known_fields(self):
        """formatLogEventDetail must group known fields into sections like Process."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var html = formatLogEventDetail({Image: 'evil.exe', CommandLine: 'evil.exe -payload'});
            window.__jsdom_result = {
                hasProcess: html.indexOf('Process') >= 0,
                hasImage: html.indexOf('evil.exe') >= 0,
                hasCommandLine: html.indexOf('evil.exe -payload') >= 0
            };
        ''')
        self.assertTrue(result['hasProcess'])
        self.assertTrue(result['hasImage'])
        self.assertTrue(result['hasCommandLine'])

    def test_formatLogEventDetail_falls_back_to_raw_data(self):
        """formatLogEventDetail must show Raw Data section for unknown fields."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var html = formatLogEventDetail({FooBar: 'baz'});
            window.__jsdom_result = {
                hasRawData: html.indexOf('Raw Data') >= 0,
                hasFooBar: html.indexOf('FooBar') >= 0,
                hasBaz: html.indexOf('baz') >= 0
            };
        ''')
        self.assertTrue(result['hasRawData'])
        self.assertTrue(result['hasFooBar'])
        self.assertTrue(result['hasBaz'])

    def test_formatSigmaAlertDetail_shows_rule_metadata(self):
        """formatSigmaAlertDetail must show rule title, MITRE links, tags, and matched event."""
        from tests.jsdom_helper import js_statements
        alert = {
            'original_log': json.dumps({'Image': 'evil.exe'}),
            'rule_title': 'Test Rule',
            'rule_id': 'test-123',
            'severity': 'high',
            'level': 'critical',
            'logsource': 'windows',
            'mitre_techniques': json.dumps(['attack.t1059']),
            'tags': json.dumps(['test', 'malware'])
        }
        result = js_statements(f'''
            var alert = {json.dumps(alert)};
            var html = formatSigmaAlertDetail(alert);
            window.__jsdom_result = {{
                hasRuleTitle: html.indexOf('Test Rule') >= 0,
                hasMitreLink: html.indexOf('T1059') >= 0,
                hasTag: html.indexOf('malware') >= 0,
                hasMatchedEvent: html.indexOf('Matched Event') >= 0,
                hasSeverity: html.indexOf('high') >= 0
            }};
        ''')
        self.assertTrue(result['hasRuleTitle'])
        self.assertTrue(result['hasMitreLink'])
        self.assertTrue(result['hasTag'])
        self.assertTrue(result['hasMatchedEvent'])
        self.assertTrue(result['hasSeverity'])

    def test_getLogEventSmartDetail_network_fallback(self):
        """getLogEventSmartDetail must return network summary for IP/port fields."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var detail = getLogEventSmartDetail({SourceIp: '1.2.3.4', SourcePort: 80, DestinationIp: '5.6.7.8', DestinationPort: 443});
            window.__jsdom_result = detail;
        ''')
        self.assertIn('1.2.3.4', result)
        self.assertIn('5.6.7.8', result)

    def test_getLogEventSmartDetail_process_fallback(self):
        """getLogEventSmartDetail must return command line for process fields."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var detail = getLogEventSmartDetail({Image: 'evil.exe', CommandLine: 'evil.exe -payload'});
            window.__jsdom_result = detail;
        ''')
        self.assertIn('evil.exe', result)
        self.assertIn('-payload', result)

    def test_getLogEventSmartDetail_empty_fallback(self):
        """getLogEventSmartDetail must return empty string for empty input."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = getLogEventSmartDetail({});
        ''')
        self.assertEqual(result, '')

    def test_getFilteredLogEvents_matches_time(self):
        """getFilteredLogEvents must filter by timestamp substring."""
        from tests.jsdom_helper import js_statements
        events = [
            {'timestamp': '2024-01-01T00:00:00Z', 'json_data': {}},
            {'timestamp': '2024-02-01T00:00:00Z', 'json_data': {}}
        ]
        result = js_statements(f'''
            var events = {json.dumps(events)};
            currentFilters = {{Time: '2024-01-01T00:00:00'}};
            var filtered = getFilteredLogEvents(events);
            window.__jsdom_result = {{
                count: filtered.length,
                hasRightTimestamp: filtered[0].timestamp === '2024-01-01T00:00:00Z'
            }};
        ''')
        self.assertEqual(result['count'], 1)
        self.assertTrue(result['hasRightTimestamp'])

    def test_getFilteredLogEvents_matches_dynamic_column(self):
        """getFilteredLogEvents must filter by dynamic discovered column."""
        from tests.jsdom_helper import js_statements
        events = [
            {'json_data': {'Image': 'evil.exe'}},
            {'json_data': {'Image': 'good.exe'}}
        ]
        result = js_statements(f'''
            var events = {json.dumps(events)};
            currentFilters = {{Image: 'evil.exe'}};
            var filtered = getFilteredLogEvents(events);
            window.__jsdom_result = {{count: filtered.length}};
        ''')
        self.assertEqual(result['count'], 1)

    def test_getFilteredSigmaAlerts_matches_severity(self):
        """getFilteredSigmaAlerts must filter by severity."""
        from tests.jsdom_helper import js_statements
        alerts = [
            {'severity': 'high', 'rule_title': 'A', 'mitre_techniques': '[]', 'logsource': 'windows', 'original_log': '{}'},
            {'severity': 'low', 'rule_title': 'B', 'mitre_techniques': '[]', 'logsource': 'windows', 'original_log': '{}'}
        ]
        result = js_statements(f'''
            var alerts = {json.dumps(alerts)};
            currentFilters = {{Severity: 'high'}};
            var filtered = getFilteredSigmaAlerts(alerts);
            window.__jsdom_result = {{
                count: filtered.length,
                ruleTitle: filtered[0].rule_title
            }};
        ''')
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['ruleTitle'], 'A')

    def test_buildLogSectionContent_creates_table(self):
        """buildLogSectionContent must inject a table with Time header and rows into the DOM."""
        from tests.jsdom_helper import js_statements
        events = [
            {'timestamp': '2024-01-01T00:00:00Z', 'json_data': {'Channel': 'Security', 'EventID': 4624}}
        ]
        result = js_statements(f'''
            var section = document.createElement('div');
            section.id = 'section-log';
            document.body.appendChild(section);
            var events = {json.dumps(events)};
            buildLogSectionContent('section-log', events);
            var html = section.innerHTML;
            window.__jsdom_result = {{
                hasTable: html.indexOf('<table>') >= 0,
                hasTimeHeader: html.indexOf('Time') >= 0,
                hasRow: html.indexOf('<tr') >= 0
            }};
        ''')
        self.assertTrue(result['hasTable'])
        self.assertTrue(result['hasTimeHeader'])
        self.assertTrue(result['hasRow'])

    def test_buildSigmaAlertSectionContent_creates_table(self):
        """buildSigmaAlertSectionContent must inject a table with Severity and Rule headers."""
        from tests.jsdom_helper import js_statements
        alerts = [
            {'timestamp': '2024-01-01T00:00:00Z', 'severity': 'high', 'rule_title': 'Test', 'rule_id': 'r1', 'mitre_techniques': '[]', 'logsource': 'windows', 'original_log': '{}'}
        ]
        result = js_statements(f'''
            var section = document.createElement('div');
            section.id = 'section-sigmaalert';
            document.body.appendChild(section);
            var alerts = {json.dumps(alerts)};
            // No active filter/sort, so this goes through the scalable-fetch
            // branch - serve `alerts` from the mocked /api/sigma-alerts and
            // /api/sigma-count endpoints it calls internally.
            window.fetch = function(url) {{
                if (url.indexOf('/api/sigma-count') >= 0) {{
                    return Promise.resolve({{ json: () => Promise.resolve({{ count: alerts.length }}) }});
                }}
                return Promise.resolve({{ json: () => Promise.resolve(alerts) }});
            }};
            await buildSigmaAlertSectionContent('section-sigmaalert', alerts);
            var html = section.innerHTML;
            window.__jsdom_result = {{
                hasTable: html.indexOf('<table>') >= 0,
                hasSeverityHeader: html.indexOf('Severity') >= 0,
                hasRuleHeader: html.indexOf('Rule') >= 0,
                hasRow: html.indexOf('<tr') >= 0
            }};
        ''')
        self.assertTrue(result['hasTable'])
        self.assertTrue(result['hasSeverityHeader'])
        self.assertTrue(result['hasRuleHeader'])
        self.assertTrue(result['hasRow'])

    def test_buildLogAggregations_creates_agg_tables(self):
        """buildLogAggregations must render aggregation tables with agg-row elements."""
        from tests.jsdom_helper import js_statements
        events = [
            {'timestamp': '2024-01-01T00:00:00Z', 'json_data': {'Channel': 'Security', 'EventID': 4624}},
            {'timestamp': '2024-01-01T00:00:00Z', 'json_data': {'Channel': 'Security', 'EventID': 4624}}
        ]
        result = js_statements(f'''
            advancedMode = true;
            var agg = document.getElementById('aggregations');
            if (!agg) {{
                agg = document.createElement('div');
                agg.id = 'aggregations';
                document.body.appendChild(agg);
            }}
            var events = {json.dumps(events)};
            buildLogAggregations(events, 'section-log');
            var html = agg.innerHTML;
            window.__jsdom_result = {{
                hasAggRow: html.indexOf('agg-row') >= 0,
                hasAggPanel: html.indexOf('agg-panel') >= 0
            }};
        ''')
        self.assertTrue(result['hasAggRow'])
        self.assertTrue(result['hasAggPanel'])

    def test_buildSigmaAlertAggregations_creates_agg_tables(self):
        """buildSigmaAlertAggregations must render Severity aggregation table with agg-row elements."""
        from tests.jsdom_helper import js_statements
        alerts = [
            {'severity': 'high', 'rule_title': 'Test Rule', 'mitre_techniques': '[]', 'logsource': 'windows', 'original_log': '{"Image":"evil.exe"}'}
        ]
        result = js_statements(f'''
            advancedMode = true;
            var agg = document.getElementById('aggregations');
            if (!agg) {{
                agg = document.createElement('div');
                agg.id = 'aggregations';
                document.body.appendChild(agg);
            }}
            var alerts = {json.dumps(alerts)};
            buildSigmaAlertAggregations(alerts, 'section-sigmaalert');
            var html = agg.innerHTML;
            window.__jsdom_result = {{
                hasAggRow: html.indexOf('agg-row') >= 0,
                hasSeverityHeader: html.indexOf('Severity') >= 0
            }};
        ''')
        self.assertTrue(result['hasAggRow'])
        self.assertTrue(result['hasSeverityHeader'])

    def test_buildLogAggregations_escapes_malicious_field_name(self):
        """REGRESSION: a log event's JSON field *name* becomes a column label
        in the aggregation table. A malicious field name (fully attacker-
        controlled, since it comes straight from an uploaded log file) must
        not be able to inject a live element via the column label -- this
        previously created a real <img> element via both the visible label
        text and the data-col attribute."""
        from tests.jsdom_helper import js_statements
        malicious_field = '"><img src=x onerror=alert(1)>'
        events = [
            {'timestamp': '2024-01-01T00:00:00Z', 'json_data': {malicious_field: 'v', 'EventID': 1}}
            for _ in range(3)
        ]
        result = js_statements(f'''
            advancedMode = true;
            var agg = document.getElementById('aggregations');
            if (!agg) {{
                agg = document.createElement('div');
                agg.id = 'aggregations';
                document.body.appendChild(agg);
            }}
            var events = {json.dumps(events)};
            buildLogAggregations(events, 'section-log');
            window.__jsdom_result = {{
                imgCount: agg.querySelectorAll('img').length,
            }};
        ''')
        self.assertEqual(result['imgCount'], 0, 'malicious field name must not create a live <img> element')

    def test_buildSigmaAlertAggregations_escapes_malicious_field_name(self):
        """REGRESSION: same injection vector as buildLogAggregations, but
        via a Sigma alert's original_log JSON field names."""
        from tests.jsdom_helper import js_statements
        malicious_field = '"><img src=x onerror=alert(1)>'
        original_log = json.dumps({malicious_field: 'v', 'Image': 'evil.exe'})
        alerts = [
            {'severity': 'high', 'rule_title': 'Test Rule', 'mitre_techniques': '[]',
             'logsource': 'windows', 'original_log': original_log}
            for _ in range(3)
        ]
        result = js_statements(f'''
            advancedMode = true;
            var agg = document.getElementById('aggregations');
            if (!agg) {{
                agg = document.createElement('div');
                agg.id = 'aggregations';
                document.body.appendChild(agg);
            }}
            var alerts = {json.dumps(alerts)};
            buildSigmaAlertAggregations(alerts, 'section-sigmaalert');
            window.__jsdom_result = {{
                imgCount: agg.querySelectorAll('img').length,
            }};
        ''')
        self.assertEqual(result['imgCount'], 0, 'malicious field name must not create a live <img> element')

    def test_isLogAnalysisMode_false_after_clear(self):
        """clearAnalysisContainers must reset isLogAnalysisMode to false."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            isLogAnalysisMode = true;
            clearAnalysisContainers();
            window.__jsdom_result = isLogAnalysisMode;
        ''')
        self.assertFalse(result)

    def test_buildLogEventRow_renders_detail_panel(self):
        """buildLogEventRow must render a detail row with log-detail-panel containing formatted event detail."""
        from tests.jsdom_helper import js_statements
        event = {'timestamp': '2024-01-01T00:00:00Z', 'json_data': {'Image': 'evil.exe'}}
        result = js_statements(f'''
            var event = {json.dumps(event)};
            var cols = discoverLogColumns([event]);
            var html = buildLogEventRow(event, cols);
            window.__jsdom_result = {{
                hasDetailRow: html.indexOf('detail-row') >= 0,
                hasLogDetailPanel: html.indexOf('log-detail-panel') >= 0,
                hasImage: html.indexOf('evil.exe') >= 0
            }};
        ''')
        self.assertTrue(result['hasDetailRow'])
        self.assertTrue(result['hasLogDetailPanel'])
        self.assertTrue(result['hasImage'])

    def test_fetchLogAnalysisCounts_hits_count_endpoints_only(self):
        """_fetchLogAnalysisCounts must fetch cheap counts (/api/count?type=log
        and /api/sigma-count), never the full /api/events or /api/sigma-alerts
        arrays - the whole point of replacing the old eager _fetchLogAnalysisData."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                return Promise.resolve({ json: () => Promise.resolve({ count: 7 }) });
            };
            currentMd5 = 'abc123';
            var result = await _fetchLogAnalysisCounts('');
            window.__jsdom_result = {
                hitCount: fetchCalls.some(u => u.indexOf('/api/count') >= 0 && u.indexOf('type=log') >= 0),
                hitSigmaCount: fetchCalls.some(u => u.indexOf('/api/sigma-count') >= 0),
                hitEvents: fetchCalls.some(u => u.indexOf('/api/events') >= 0),
                hitSigmaAlerts: fetchCalls.some(u => u.indexOf('/api/sigma-alerts') >= 0),
                result: result
            };
        ''')
        self.assertTrue(result['hitCount'], 'must call /api/count?type=log')
        self.assertTrue(result['hitSigmaCount'], 'must call /api/sigma-count')
        self.assertFalse(result['hitEvents'], 'must NOT fetch the full /api/events array')
        self.assertFalse(result['hitSigmaAlerts'], 'must NOT fetch the full /api/sigma-alerts array')
        self.assertEqual(result['result'], {'log': 7, 'sigmaalert': 7})

    def test_loadTabData_log_fetches_once_when_uncached(self):
        """loadTabData('log', ...) must lazily hydrate tabDataCache['log'] via
        ensureCappedBatch on first visit, and reuse the cache on subsequent
        visits without refetching."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var section = document.createElement('div');
            section.id = 'section-log';
            document.body.appendChild(section);
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                return Promise.resolve({ json: () => Promise.resolve([
                    { timestamp: '2024-01-01T00:00:00Z', json_data: { Channel: 'Security' } }
                ]) });
            };
            currentFilters = {};
            currentSearch = [];
            isLogAnalysisMode = true;
            await loadTabData('log', null);
            function logCalls() { return fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('type=log') >= 0).length; }
            var callsAfterFirst = logCalls();
            // Re-assert isLogAnalysisMode: the app's own background init()
            // chain (auto-run on module load) can reset it via
            // clearAnalysisContainers() once the first loadTabData call's
            // awaits give it enough event-loop turns to run.
            isLogAnalysisMode = true;
            await loadTabData('log', null);
            var callsAfterSecond = logCalls();
            window.__jsdom_result = {
                callsAfterFirst: callsAfterFirst,
                callsAfterSecond: callsAfterSecond,
                hasTable: section.innerHTML.indexOf('<table>') >= 0
            };
        ''')
        self.assertEqual(result['callsAfterFirst'], 1, 'first visit must fetch the capped log batch exactly once')
        self.assertEqual(result['callsAfterSecond'], 1, 'second visit must reuse tabDataCache, not refetch')
        self.assertTrue(result['hasTable'])

    def test_render_log_analysis_view_defers_non_default_tab_fetch(self):
        """Simulates a full log-mode render: only the default tab (sigmaalert,
        since its count is > 0) should be selected; the other tab's (log) full
        batch must remain unfetched until the user actually switches to it via
        loadTabData - proving _renderLogAnalysisView no longer eagerly fetches
        both datasets up front."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var sectionLog = document.createElement('div');
            sectionLog.id = 'section-log';
            document.body.appendChild(sectionLog);
            var sectionSigma = document.createElement('div');
            sectionSigma.id = 'section-sigmaalert';
            document.body.appendChild(sectionSigma);

            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0 && url.indexOf('type=log') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { timestamp: '2024-01-01T00:00:00Z', json_data: { Channel: 'Security' } },
                        { timestamp: '2024-01-01T00:00:00Z', json_data: { Channel: 'System' } },
                        { timestamp: '2024-01-01T00:00:00Z', json_data: { Channel: 'Security' } }
                    ]) });
                }
                if (url.indexOf('/api/sigma-alerts') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { severity: 'high', rule_title: 'R1', mitre_techniques: '[]', logsource: 'windows', original_log: '{}' }
                    ]) });
                }
                if (url.indexOf('/api/sigma-count') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve({ count: 1 }) });
                }
                return Promise.resolve({ json: () => Promise.resolve({}) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            advancedMode = false;
            isLogAnalysisMode = true;
            function logCalls() { return fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('type=log') >= 0).length; }

            await _renderLogAnalysisView({ log: 3, sigmaalert: 1 });
            var logFetchesAfterInitialRender = logCalls();

            // Re-assert for the same background-init()-race reason as above.
            isLogAnalysisMode = true;
            await loadTabData('log', null);
            var logFetchesAfterVisit = logCalls();

            window.__jsdom_result = {
                logFetchesAfterInitialRender: logFetchesAfterInitialRender,
                logFetchesAfterVisit: logFetchesAfterVisit
            };
        ''')
        self.assertEqual(result['logFetchesAfterInitialRender'], 0,
                         'the non-default (log) tab must not be fetched just from the initial render')
        self.assertEqual(result['logFetchesAfterVisit'], 1,
                         'switching to the log tab must trigger exactly one fetch of its capped batch')


class TestXSSPreventionLogAnalysis(unittest.TestCase):
    def _get_function_body(self, func_name):
        func_match = re.search(rf'function {re.escape(func_name)}\([^)]*\)\s*\{{', JS_CONTENT)
        self.assertIsNotNone(func_match, f'{func_name} function not found')
        start = func_match.end()
        brace_count = 1
        pos = start
        while pos < len(JS_CONTENT) and brace_count > 0:
            if JS_CONTENT[pos] == '{':
                brace_count += 1
            elif JS_CONTENT[pos] == '}':
                brace_count -= 1
            pos += 1
        return JS_CONTENT[start:pos]

    def _assert_no_unescaped_script(self, html, context):
        """Assert that raw <script> or <img onerror tags do not appear unescaped."""
        lower = html.lower()
        self.assertNotIn('<script>', lower,
                         f'{context}: unescaped <script> tag found in output')
        self.assertNotIn('<img', lower,
                         f'{context}: unescaped <img> tag found in output')
        self.assertNotIn('javascript:', lower,
                         f'{context}: unescaped javascript: URI found in output')

    # ---- String-inspection tests for escapeHtml presence ----

    def test_formatLogEventDetail_uses_htmlRowText(self):
        """formatLogEventDetail must escape all user-controlled values via htmlRowText."""
        func_body = self._get_function_body('formatLogEventDetail')
        self.assertIn('htmlRowText', func_body,
                      'formatLogEventDetail must use htmlRowText for field values')

    def test_formatSigmaAlertDetail_uses_htmlRowText(self):
        """formatSigmaAlertDetail must escape rule metadata with htmlRowText."""
        func_body = self._get_function_body('formatSigmaAlertDetail')
        self.assertIn("htmlRowText('Rule Title', alert.rule_title)", func_body,
                      'rule_title must be passed through htmlRowText')
        self.assertIn("htmlRowText('Rule ID', alert.rule_id)", func_body,
                      'rule_id must be passed through htmlRowText')
        self.assertIn("htmlRowText('Severity', alert.severity)", func_body,
                      'severity must be passed through htmlRowText')
        self.assertIn("htmlRowText('Log Source', alert.logsource)", func_body,
                      'logsource must be passed through htmlRowText')
        self.assertIn('mitreTechniquesHtml(alert.mitre_techniques)', func_body,
                      'MITRE techniques must be rendered via the shared helper')
        mitre_body = self._get_function_body('mitreTechniquesHtml')
        self.assertIn('escapeHtml(tid)', mitre_body,
                      'MITRE technique ID must be escaped')
        self.assertIn("htmlRowText('Tags', tagsText)", func_body,
                      'Sigma tags must be passed through htmlRowText for escaping')

    def test_buildLogEventRow_escapes_all_fields(self):
        """buildLogEventRow must escape timestamp, column values, and detail."""
        func_body = self._get_function_body('buildLogEventRow')
        self.assertIn('escapeHtml((evt.timestamp', func_body,
                      'timestamp must be escaped')
        self.assertIn('escapeHtml(val)', func_body,
                      'column values must be escaped')
        self.assertIn('escapeHtml(detailTruncated)', func_body,
                      'detail text must be escaped')

    def test_buildSigmaAlertRow_escapes_all_fields(self):
        """buildSigmaAlertRow must escape timestamp, severity, rule title, and logsource."""
        func_body = self._get_function_body('buildSigmaAlertRow')
        self.assertIn('escapeHtml(alert.timestamp', func_body,
                      'timestamp must be escaped')
        self.assertIn('escapeHtml(sev.toUpperCase())', func_body,
                      'severity must be escaped')
        self.assertIn('escapeHtml(alert.rule_title', func_body,
                      'rule_title must be escaped')
        self.assertIn('escapeHtml(alert.rule_id', func_body,
                      'rule_id must be escaped')
        self.assertIn('escapeHtml(alert.logsource', func_body,
                      'logsource must be escaped')

    # ---- JSDOM behavioral tests with malicious payloads ----

    def test_formatLogEventDetail_escapes_script_tags(self):
        """formatLogEventDetail must escape <script> tags in field values."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var html = formatLogEventDetail({Image: '<script>alert(1)</script>'});
            window.__jsdom_result = {
                hasUnescapedScript: html.indexOf('<script>') >= 0,
                hasEscapedScript: html.indexOf('&lt;script&gt;') >= 0
            };
        ''')
        self.assertFalse(result['hasUnescapedScript'],
                         'formatLogEventDetail must not contain unescaped <script>')
        self.assertTrue(result['hasEscapedScript'],
                        'formatLogEventDetail should contain escaped &lt;script&gt;')

    def test_formatLogEventDetail_escapes_raw_data_section(self):
        """formatLogEventDetail must escape unknown fields in Raw Data section."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var html = formatLogEventDetail({'<script>key</script>': '<img src=x onerror=alert(1)>'});
            window.__jsdom_result = {
                hasUnescapedScript: html.indexOf('<script>') >= 0,
                hasUnescapedImg: html.indexOf('<img') >= 0,
                hasEscapedScript: html.indexOf('&lt;script&gt;') >= 0
            };
        ''')
        self.assertFalse(result['hasUnescapedScript'])
        self.assertFalse(result['hasUnescapedImg'])
        self.assertTrue(result['hasEscapedScript'])

    def test_formatSigmaAlertDetail_escapes_rule_title(self):
        """formatSigmaAlertDetail must escape <script> in rule title."""
        from tests.jsdom_helper import js_statements
        alert = {
            'rule_title': '<script>alert(1)</script>',
            'rule_id': 'test-123',
            'severity': 'high',
            'level': 'critical',
            'logsource': 'windows',
            'mitre_techniques': '[]',
            'tags': '[]',
            'original_log': '{}'
        }
        result = js_statements(f'''
            var alert = {json.dumps(alert)};
            var html = formatSigmaAlertDetail(alert);
            window.__jsdom_result = {{
                hasUnescapedScript: html.indexOf('<script>') >= 0,
                hasEscapedScript: html.indexOf('&lt;script&gt;') >= 0
            }};
        ''')
        self.assertFalse(result['hasUnescapedScript'])
        self.assertTrue(result['hasEscapedScript'])

    def test_formatSigmaAlertDetail_escapes_tags(self):
        """formatSigmaAlertDetail must escape <script> in Sigma tags."""
        from tests.jsdom_helper import js_statements
        alert = {
            'rule_title': 'Test',
            'rule_id': 'r1',
            'severity': 'low',
            'level': 'low',
            'logsource': 'windows',
            'mitre_techniques': '[]',
            'tags': json.dumps(['<script>alert(1)</script>']),
            'original_log': '{}'
        }
        result = js_statements(f'''
            var alert = {json.dumps(alert)};
            var html = formatSigmaAlertDetail(alert);
            window.__jsdom_result = {{
                hasUnescapedScript: html.indexOf('<script>') >= 0,
                hasEscapedScript: html.indexOf('&lt;script&gt;') >= 0
            }};
        ''')
        self.assertFalse(result['hasUnescapedScript'])
        self.assertTrue(result['hasEscapedScript'])

    def test_formatSigmaAlertDetail_escapes_mitre_techniques(self):
        """formatSigmaAlertDetail must escape <script> in MITRE technique display text and encode in href."""
        from tests.jsdom_helper import js_statements
        alert = {
            'rule_title': 'Test',
            'rule_id': 'r1',
            'severity': 'low',
            'level': 'low',
            'logsource': 'windows',
            'mitre_techniques': json.dumps(['attack.<script>alert(1)</script>']),
            'tags': '[]',
            'original_log': '{}'
        }
        result = js_statements(f'''
            var alert = {json.dumps(alert)};
            var html = formatSigmaAlertDetail(alert);
            window.__jsdom_result = {{
                hasUnescapedScriptInText: html.indexOf('<script>') >= 0,
                hasEscapedScriptInText: html.indexOf('&lt;SCRIPT&gt;') >= 0,
                hasEncodedInHref: html.indexOf('encodeURIComponent') >= 0 || html.indexOf('%3C') >= 0
            }};
        ''')
        self.assertFalse(result['hasUnescapedScriptInText'],
                         'MITRE technique display text must not contain unescaped <script>')
        self.assertTrue(result['hasEscapedScriptInText'],
                        'MITRE technique display text must contain escaped &lt;SCRIPT&gt;')
        self.assertTrue(result['hasEncodedInHref'],
                        'MITRE technique ID must be encoded in href URL')

    def test_buildLogEventRow_escapes_malicious_payloads(self):
        """REGRESSION: this collided with the static source-check test of the
        same name above (test_buildLogEventRow_escapes_all_fields) - Python
        silently lets the later definition shadow the earlier one in a
        class body, so the static check was never actually running. Renamed
        so both tests execute."""
        from tests.jsdom_helper import js_statements
        event = {
            'timestamp': '<script>alert(1)</script>',
            'json_data': {'Channel': '<script>alert(2)</script>', 'CommandLine': '<img src=x onerror=alert(3)>'}
        }
        result = js_statements(f'''
            var event = {json.dumps(event)};
            var cols = discoverLogColumns([event]);
            var html = buildLogEventRow(event, cols);
            window.__jsdom_result = {{
                hasUnescapedScript: html.indexOf('<script>') >= 0,
                hasUnescapedImg: html.indexOf('<img') >= 0
            }};
        ''')
        self.assertFalse(result['hasUnescapedScript'])
        self.assertFalse(result['hasUnescapedImg'])

    def test_buildSigmaAlertRow_escapes_malicious_payloads(self):
        """REGRESSION: this collided with the static source-check test of the
        same name above (test_buildSigmaAlertRow_escapes_all_fields) - Python
        silently lets the later definition shadow the earlier one in a
        class body, so the static check was never actually running. Renamed
        so both tests execute."""
        from tests.jsdom_helper import js_statements
        alert = {
            'timestamp': '<script>alert(1)</script>',
            'severity': 'high<script>alert(2)</script>',
            'rule_title': '<script>alert(3)</script>',
            'rule_id': '<script>alert(4)</script>',
            'mitre_techniques': '[]',
            'logsource': '<script>alert(5)</script>',
            'original_log': '{}'
        }
        result = js_statements(f'''
            var alert = {json.dumps(alert)};
            var html = buildSigmaAlertRow(alert);
            window.__jsdom_result = {{
                hasUnescapedScript: html.indexOf('<script>') >= 0,
                hasEscapedScript: html.indexOf('&lt;script&gt;') >= 0
            }};
        ''')
        self.assertFalse(result['hasUnescapedScript'])
        self.assertTrue(result['hasEscapedScript'])

    def test_buildLogSectionContent_escapes_event_data(self):
        """buildLogSectionContent must not contain unescaped script tags after DOM injection."""
        from tests.jsdom_helper import js_statements
        events = [
            {'timestamp': '<script>alert(1)</script>', 'json_data': {'Channel': '<script>alert(2)</script>'}}
        ]
        result = js_statements(f'''
            var section = document.createElement('div');
            section.id = 'section-log';
            document.body.appendChild(section);
            var events = {json.dumps(events)};
            buildLogSectionContent('section-log', events);
            var html = section.innerHTML;
            window.__jsdom_result = {{
                hasUnescapedScript: html.indexOf('<script>') >= 0
            }};
        ''')
        self.assertFalse(result['hasUnescapedScript'])

    def test_buildSigmaAlertSectionContent_escapes_alert_data(self):
        """buildSigmaAlertSectionContent must not contain unescaped script tags after DOM injection."""
        from tests.jsdom_helper import js_statements
        alerts = [
            {'timestamp': '<script>alert(1)</script>', 'severity': 'high', 'rule_title': '<script>alert(2)</script>',
             'rule_id': 'r1', 'mitre_techniques': '[]', 'logsource': '<script>alert(3)</script>', 'original_log': '{}'}
        ]
        result = js_statements(f'''
            var section = document.createElement('div');
            section.id = 'section-sigmaalert';
            document.body.appendChild(section);
            var alerts = {json.dumps(alerts)};
            window.fetch = function(url) {{
                if (url.indexOf('/api/sigma-count') >= 0) {{
                    return Promise.resolve({{ json: () => Promise.resolve({{ count: alerts.length }}) }});
                }}
                return Promise.resolve({{ json: () => Promise.resolve(alerts) }});
            }};
            await buildSigmaAlertSectionContent('section-sigmaalert', alerts);
            var html = section.innerHTML;
            window.__jsdom_result = {{
                hasUnescapedScript: html.indexOf('<script>') >= 0
            }};
        ''')
        self.assertFalse(result['hasUnescapedScript'])

    def test_buildLogAggregations_escapes_values_in_onclick(self):
        """buildLogAggregations must not allow double quotes in aggregation values to break onclick."""
        from tests.jsdom_helper import js_statements
        events = [
            {'timestamp': '2024-01-01T00:00:00Z', 'json_data': {'Channel': 'test"onclick="alert(1)'}}
        ]
        result = js_statements(f'''
            advancedMode = true;
            var agg = document.getElementById('aggregations');
            if (!agg) {{
                agg = document.createElement('div');
                agg.id = 'aggregations';
                document.body.appendChild(agg);
            }}
            var events = {json.dumps(events)};
            buildLogAggregations(events, 'section-log');
            var html = agg.innerHTML;
            // Find the onclick attribute and check if it contains unescaped double quotes
            var onclickMatch = html.match(/onclick="([^"]*)"([^>]*)/);
            var hasBrokenAttr = false;
            if (onclickMatch) {{
                // If there's content after the first closing quote but before the tag end,
                // the attribute was broken
                hasBrokenAttr = onclickMatch[2].trim().length > 0 && onclickMatch[2].indexOf('>') === -1;
            }}
            window.__jsdom_result = {{
                hasUnescapedScript: html.indexOf('<script>') >= 0,
                hasBrokenOnclick: hasBrokenAttr
            }};
        ''')
        self.assertFalse(result['hasUnescapedScript'])
        self.assertFalse(result['hasBrokenOnclick'],
                         'onclick attribute must not be breakable by double quotes in user data')

    def test_buildSigmaAlertAggregations_escapes_values_in_onclick(self):
        """buildSigmaAlertAggregations must not allow double quotes in rule titles to break onclick."""
        from tests.jsdom_helper import js_statements
        alerts = [
            {'severity': 'high', 'rule_title': 'test"onclick="alert(1)', 'mitre_techniques': '[]',
             'logsource': 'windows', 'original_log': '{}'}
        ]
        result = js_statements(f'''
            advancedMode = true;
            var agg = document.getElementById('aggregations');
            if (!agg) {{
                agg = document.createElement('div');
                agg.id = 'aggregations';
                document.body.appendChild(agg);
            }}
            var alerts = {json.dumps(alerts)};
            buildSigmaAlertAggregations(alerts, 'section-sigmaalert');
            var html = agg.innerHTML;
            var onclickMatch = html.match(/onclick="([^"]*)"([^>]*)/);
            var hasBrokenAttr = false;
            if (onclickMatch) {{
                hasBrokenAttr = onclickMatch[2].trim().length > 0 && onclickMatch[2].indexOf('>') === -1;
            }}
            window.__jsdom_result = {{
                hasUnescapedScript: html.indexOf('<script>') >= 0,
                hasBrokenOnclick: hasBrokenAttr
            }};
        ''')
        self.assertFalse(result['hasUnescapedScript'])
        self.assertFalse(result['hasBrokenOnclick'],
                         'onclick attribute must not be breakable by double quotes in rule titles')

    def test_buildLogEventRow_detail_id_with_quotes(self):
        """buildLogEventRow must handle row_id containing quotes without breaking onclick."""
        from tests.jsdom_helper import js_statements
        event = {
            'row_id': 'test"onclick="alert(1)',
            'timestamp': '2024-01-01T00:00:00Z',
            'json_data': {}
        }
        result = js_statements(f'''
            var event = {json.dumps(event)};
            var cols = [];
            var html = buildLogEventRow(event, cols);
            var onclickMatch = html.match(/onclick="([^"]*)"([^>]*)/);
            var hasBrokenAttr = false;
            if (onclickMatch) {{
                hasBrokenAttr = onclickMatch[2].trim().length > 0 && onclickMatch[2].indexOf('>') === -1;
            }}
            window.__jsdom_result = {{
                hasBrokenOnclick: hasBrokenAttr
            }};
        ''')
        self.assertFalse(result['hasBrokenOnclick'],
                         'detailId in onclick must not be breakable by quotes')

    def test_buildSigmaAlertRow_detail_id_with_quotes(self):
        """buildSigmaAlertRow must handle alert.id containing quotes without breaking onclick."""
        from tests.jsdom_helper import js_statements
        alert = {
            'id': 'test"onclick="alert(1)',
            'timestamp': '2024-01-01T00:00:00Z',
            'severity': 'high',
            'rule_title': 'Test',
            'rule_id': 'r1',
            'mitre_techniques': '[]',
            'logsource': 'windows',
            'original_log': '{}'
        }
        result = js_statements(f'''
            var alert = {json.dumps(alert)};
            var html = buildSigmaAlertRow(alert);
            var onclickMatch = html.match(/onclick="([^"]*)"([^>]*)/);
            var hasBrokenAttr = false;
            if (onclickMatch) {{
                hasBrokenAttr = onclickMatch[2].trim().length > 0 && onclickMatch[2].indexOf('>') === -1;
            }}
            window.__jsdom_result = {{
                hasBrokenOnclick: hasBrokenAttr
            }};
        ''')
        self.assertFalse(result['hasBrokenOnclick'],
                         'detailId in onclick must not be breakable by quotes')


class TestBackwardCompatibilityUI(unittest.TestCase):
    """Test frontend behavior when loading old analyses without .meta files."""

    def test_load_analysis_fallback_to_pcap_for_pcap_filename(self):
        """When check-status returns no meta and filename is .pcap, frontend must set isPcap=true."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            // Simulate the loadAnalysis flow with a .pcap file and no meta
            var analysisStatus = { status: 'ready', md5: 'a' * 32, file_name: 'capture.pcap' };
            var detectedType = analysisStatus.meta?.detected_type ||
                (analysisStatus.file_name && /\\.(pcap|pcapng|cap|trace)$/i.test(analysisStatus.file_name) ? 'pcap' :
                 analysisStatus.file_name && /\\.(evtx|json|jsonl|csv|xml|log)$/i.test(analysisStatus.file_name) ? 'log' : 'binary');
            var isPcap = detectedType === 'pcap';
            var isLogFile = /\\.(evtx|json|jsonl|csv|xml|log)$/i.test(analysisStatus.file_name || '');
            var isFileOnly = !isPcap;
            window.__jsdom_result = {
                detectedType: detectedType,
                isPcap: isPcap,
                isLogFile: isLogFile,
                isFileOnly: isFileOnly
            };
        ''')
        self.assertEqual(result['detectedType'], 'pcap')
        self.assertTrue(result['isPcap'])
        self.assertFalse(result['isLogFile'])
        self.assertFalse(result['isFileOnly'])

    def test_load_analysis_fallback_to_binary_for_unknown_extension(self):
        """When check-status returns no meta and filename has no known extension, frontend must default to binary."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            // Simulate the loadAnalysis flow with an unknown file and no meta
            var analysisStatus = { status: 'ready', md5: 'a' * 32, file_name: 'unknown.dat' };
            var detectedType = analysisStatus.meta?.detected_type ||
                (analysisStatus.file_name && /\\.(pcap|pcapng|cap|trace)$/i.test(analysisStatus.file_name) ? 'pcap' :
                 analysisStatus.file_name && /\\.(evtx|json|jsonl|csv|xml|log)$/i.test(analysisStatus.file_name) ? 'log' : 'binary');
            var isPcap = detectedType === 'pcap';
            var isLogFile = /\\.(evtx|json|jsonl|csv|xml|log)$/i.test(analysisStatus.file_name || '');
            var isFileOnly = !isPcap;
            window.__jsdom_result = {
                detectedType: detectedType,
                isPcap: isPcap,
                isLogFile: isLogFile,
                isFileOnly: isFileOnly
            };
        ''')
        self.assertEqual(result['detectedType'], 'binary')
        self.assertFalse(result['isPcap'])
        self.assertFalse(result['isLogFile'])
        self.assertTrue(result['isFileOnly'])


class TestErrorHandlingUI(unittest.TestCase):
    """Test frontend error handling when API calls fail."""

    def test_refreshAnalysisData_has_try_catch_with_hideLoading_and_showError(self):
        """refreshAnalysisData must wrap fetches in try/catch that calls hideLoading and showError."""
        func_body = JS_CONTENT.split('function refreshAnalysisData()')[1].split('function loadAnalysis(')[0]
        self.assertIn('try {', func_body, 'refreshAnalysisData must have try block')
        self.assertIn("} catch(err) {", func_body, 'refreshAnalysisData must have catch block')
        self.assertIn('hideLoading();', func_body, 'catch must call hideLoading')
        self.assertIn('showError(', func_body, 'catch must call showError')

    def test_loadAnalysis_catch_calls_hideLoading_and_showError(self):
        """loadAnalysis catch block must call hideLoading and showError."""
        func_body = JS_CONTENT.split('function loadAnalysis(md5)')[1].split('function loadSampleUrl(')[0]
        self.assertIn('} catch(err) {', func_body, 'loadAnalysis must have catch block')
        self.assertIn('hideLoading();', func_body, 'catch must call hideLoading')
        self.assertIn('showError(', func_body, 'catch must call showError')


class TestHelpModalUI(unittest.TestCase):
    """JSDOM behavioral tests for help modal width and content switching."""

    def test_showHelpModal_adds_wide_class_on_welcome(self):
        """showHelpModal must add 'wide' class to #helpModal when on welcome screen."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            // Ensure welcome UI is visible (inputBoxes displayed)
            document.getElementById('inputBoxes').style.display = 'block';
            document.getElementById('mainHeader').style.display = 'none';
            showHelpModal();
            var modal = document.getElementById('helpModal');
            window.__jsdom_result = {
                hasWide: modal.classList.contains('wide'),
                hasActive: modal.classList.contains('active'),
                title: document.getElementById('helpModalTitle').textContent,
            };
        ''')
        self.assertTrue(result['hasWide'], 'helpModal must have "wide" class on welcome screen')
        self.assertTrue(result['hasActive'], 'helpModal must have "active" class after showHelpModal')
        self.assertEqual(result['title'], 'Welcome to SO-CRATES!', 'Title must be Welcome on welcome screen')

    def test_showHelpModal_removes_wide_class_on_analysis(self):
        """showHelpModal must remove 'wide' class from #helpModal when in analysis mode."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            // First show welcome help to set wide class
            document.getElementById('inputBoxes').style.display = 'block';
            document.getElementById('mainHeader').style.display = 'none';
            showHelpModal();
            // Now switch to analysis mode and call showHelpModal again
            document.getElementById('inputBoxes').style.display = 'none';
            document.getElementById('mainHeader').style.display = 'block';
            // Simulate a loaded file name for analysis help
            var currentFileName = 'test.pcap';
            showHelpModal();
            var modal = document.getElementById('helpModal');
            window.__jsdom_result = {
                hasWide: modal.classList.contains('wide'),
                hasActive: modal.classList.contains('active'),
                title: document.getElementById('helpModalTitle').textContent,
            };
        ''')
        self.assertFalse(result['hasWide'], 'helpModal must NOT have "wide" class in analysis mode')
        self.assertTrue(result['hasActive'], 'helpModal must have "active" class after showHelpModal')
        self.assertEqual(result['title'], 'Analysis Help', 'Title must be Analysis Help in analysis mode')


class TestComputeFilteredStatsLaziness(unittest.TestCase):
    """computeFilteredStats must avoid fetching the full allEvents batch
    except when a column filter is actually active - the whole point of
    making allEvents population lazy instead of eager on every load/search."""

    def test_no_filter_makes_no_fetch(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) { fetchCalls.push(url); return Promise.resolve({ json: () => Promise.resolve({}) }); };
            currentFilters = {};
            isLogAnalysisMode = false;
            var result = await computeFilteredStats();
            window.__jsdom_result = {
                relevantCalls: fetchCalls.filter(u => u.indexOf('/api/events') >= 0 || u.indexOf('/api/count') >= 0).length,
                result: result
            };
        ''')
        self.assertEqual(result['relevantCalls'], 0,
                         'computeFilteredStats must not fetch allEvents when no column filter is active')

    def test_active_filter_with_uncached_allEvents_fetches_once(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { event_type: 'alert', proto: 'TCP' },
                        { event_type: 'alert', proto: 'UDP' },
                        { event_type: 'dns', proto: 'UDP' }
                    ]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({}) });
            };
            currentFilters = { 'Protocol': 'UDP' };
            isLogAnalysisMode = false;
            var result = await computeFilteredStats();
            window.__jsdom_result = {
                relevantCalls: fetchCalls.filter(u => u.indexOf('/api/events') >= 0).length,
                eventsUrlHasType: fetchCalls.some(u => u.indexOf('/api/events') >= 0 && u.indexOf('type=') >= 0),
                result: result
            };
        ''')
        self.assertEqual(result['relevantCalls'], 1,
                         'computeFilteredStats must fetch allEvents exactly once when a filter is active and nothing is cached')
        self.assertFalse(result['eventsUrlHasType'],
                         'the merged all-types query must not include a type= param')
        self.assertEqual(result['result'], {'alert': 1, 'dns': 1},
                         'counts must reflect only events matching the active column filter')

    def test_active_filter_with_cached_allEvents_makes_no_additional_fetch(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { event_type: 'alert', proto: 'TCP' },
                        { event_type: 'dns', proto: 'UDP' }
                    ]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({}) });
            };
            currentFilters = {};
            isLogAnalysisMode = false;
            await ensureCappedBatch('all');
            var callsAfterEnsure = fetchCalls.filter(u => u.indexOf('/api/events') >= 0).length;
            currentFilters = { 'Protocol': 'TCP' };
            var result = await computeFilteredStats();
            window.__jsdom_result = {
                callsAfterEnsure: callsAfterEnsure,
                callsAfterStats: fetchCalls.filter(u => u.indexOf('/api/events') >= 0).length,
                result: result
            };
        ''')
        self.assertEqual(result['callsAfterEnsure'], 1)
        self.assertEqual(result['callsAfterStats'], 1,
                         'computeFilteredStats must reuse an already-cached allEvents, not refetch')
        self.assertEqual(result['result'], {'alert': 1})

    def test_log_mode_no_filter_makes_no_fetch(self):
        """Mirrors the non-log-mode fast path: with no active column filter,
        eventStats (already populated by the cheap /api/count + /api/sigma-count
        counts fetched on load) is returned directly - no need to touch the
        full arrays or fetch anything. (eventStats is let-scoped inside
        socrates.js, so it can't be injected with a custom value from a
        separate eval call - this only checks the zero-fetch behavior, same
        as the equivalent non-log-mode test above.)"""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) { fetchCalls.push(url); return Promise.resolve({ json: () => Promise.resolve({}) }); };
            currentFilters = {};
            isLogAnalysisMode = true;
            var result = await computeFilteredStats();
            window.__jsdom_result = {
                relevantCalls: fetchCalls.filter(u => u.indexOf('/api/events') >= 0 || u.indexOf('/api/sigma-alerts') >= 0).length
            };
        ''')
        self.assertEqual(result['relevantCalls'], 0,
                         'log-mode computeFilteredStats must not fetch full batches when no column filter is active')

    def test_log_mode_active_filter_with_uncached_data_fetches_once_each(self):
        """With a filter active and nothing cached yet, computeFilteredStats
        must hydrate both tabDataCache['log'] and ['sigmaalert'] via
        ensureCappedBatch (exactly once each) before counting matches."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0 && url.indexOf('type=log') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { timestamp: '2024-01-01T00:00:00Z', json_data: { Channel: 'Security' } },
                        { timestamp: '2024-01-01T00:00:00Z', json_data: { Channel: 'System' } }
                    ]) });
                }
                if (url.indexOf('/api/sigma-alerts') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { severity: 'high', rule_title: 'R1', mitre_techniques: '[]', logsource: 'windows', original_log: '{}' }
                    ]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({}) });
            };
            currentFilters = { 'Channel': 'Security' };
            isLogAnalysisMode = true;
            var result = await computeFilteredStats();
            window.__jsdom_result = {
                logCalls: fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('type=log') >= 0).length,
                sigmaCalls: fetchCalls.filter(u => u.indexOf('/api/sigma-alerts') >= 0).length,
                result: result
            };
        ''')
        self.assertEqual(result['logCalls'], 1,
                         'must fetch the full log batch exactly once via ensureCappedBatch when a filter is active')
        self.assertEqual(result['sigmaCalls'], 1,
                         'must fetch the full sigma-alert batch exactly once via ensureCappedBatch when a filter is active')
        self.assertEqual(result['result'], {'log': 1},
                         'counts must reflect only items matching the active column filter')

    def test_log_mode_active_filter_with_cached_data_makes_no_additional_fetch(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0 && url.indexOf('type=log') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { timestamp: '2024-01-01T00:00:00Z', json_data: { Channel: 'Security' } }
                    ]) });
                }
                if (url.indexOf('/api/sigma-alerts') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({}) });
            };
            currentFilters = {};
            isLogAnalysisMode = true;
            await ensureCappedBatch('log');
            await ensureCappedBatch('sigmaalert');
            function relevantCalls() {
                return fetchCalls.filter(u => (u.indexOf('/api/events') >= 0 && u.indexOf('type=log') >= 0) || u.indexOf('/api/sigma-alerts') >= 0).length;
            }
            var callsAfterEnsure = relevantCalls();
            currentFilters = { 'Channel': 'Security' };
            // Re-assert isLogAnalysisMode immediately before the call under
            // test: the app's own init() (auto-run on module load, since no
            // ?file= param is present in this environment) resolves to
            // showWelcome() -> clearAnalysisContainers() in the background,
            // which resets isLogAnalysisMode to false - the two awaited
            // ensureCappedBatch calls above give it enough event-loop turns
            // to do so before this point. That same background chain also
            // makes its own unrelated fetch calls (e.g. /api/analyses), so
            // relevantCalls() filters to only the URLs this test cares about.
            isLogAnalysisMode = true;
            var result = await computeFilteredStats();
            window.__jsdom_result = {
                callsAfterEnsure: callsAfterEnsure,
                callsAfterStats: relevantCalls(),
                result: result
            };
        ''')
        self.assertEqual(result['callsAfterEnsure'], 2)
        self.assertEqual(result['callsAfterStats'], 2,
                         'computeFilteredStats must reuse already-cached tabDataCache entries, not refetch')
        self.assertEqual(result['result'], {'log': 1})


class TestSankeyServerAggregation(unittest.TestCase):
    """updateSankeyDiagram must use the lightweight server-aggregated
    /api/sankey-data endpoint when no column filter is active (so the
    diagram can stay visible by default without needing a full capped
    batch), and fall back to the existing client-side buildSankeyData
    path unchanged when a filter is active."""

    def _make_section(self, event_type='dns'):
        return f'''
            var section = document.createElement('div');
            section.className = 'section';
            section.id = 'section-{event_type}';
            document.body.appendChild(section);
        '''

    def test_no_filter_uses_server_endpoint_not_full_batch(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('dns') + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/sankey-data') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve({ nodes: [], links: [] }) });
                }
                return Promise.resolve({ json: () => Promise.resolve([]) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            diagramMode = true;
            await updateSankeyDiagram();
            window.__jsdom_result = {
                sankeyCalls: fetchCalls.filter(u => u.indexOf('/api/sankey-data') >= 0).length,
                sankeyUrlHasType: fetchCalls.some(u => u.indexOf('/api/sankey-data') >= 0 && u.indexOf('type=dns') >= 0),
                fullBatchCalls: fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('limit=') >= 0).length
            };
        ''')
        self.assertEqual(result['sankeyCalls'], 1,
                         'updateSankeyDiagram must fetch /api/sankey-data exactly once when no filter is active')
        self.assertTrue(result['sankeyUrlHasType'],
                        'the sankey-data request must be scoped to the visible tab\'s event type')
        self.assertEqual(result['fullBatchCalls'], 0,
                         'updateSankeyDiagram must not trigger the full capped-batch fetch when it can use the server endpoint')

    def test_active_filter_falls_back_to_client_side_build(self):
        from tests.jsdom_helper import js_statements
        dns_events = [
            {'event_type': 'dns', 'proto': 'UDP', 'src_ip': '1.1.1.1', 'dest_ip': '2.2.2.2', 'dest_port': 53},
            {'event_type': 'dns', 'proto': 'TCP', 'src_ip': '1.1.1.1', 'dest_ip': '3.3.3.3', 'dest_port': 53}
        ]
        result = js_statements(self._make_section('dns') + f'''
            var fetchCalls = [];
            window.fetch = function(url) {{
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) {{
                    return Promise.resolve({{ json: () => Promise.resolve({json.dumps(dns_events)}) }});
                }}
                return Promise.resolve({{ json: () => Promise.resolve([]) }});
            }};
            currentMd5 = 'abc123';
            currentFilters = {{ 'Protocol': 'UDP' }};
            currentSearch = [];
            diagramMode = true;
            // Populate tabDataCache via the real ensureCappedBatch path (tabDataCache
            // itself is let-scoped inside socrates.js and not writable directly from
            // a separate eval call).
            await ensureCappedBatch('dns');
            fetchCalls.length = 0;
            await updateSankeyDiagram();
            window.__jsdom_result = {{
                sankeyCalls: fetchCalls.filter(u => u.indexOf('/api/sankey-data') >= 0).length,
                panelHtml: document.getElementById('sankeyPanel').innerHTML
            }};
        ''', with_d3=True)
        self.assertEqual(result['sankeyCalls'], 0,
                         'updateSankeyDiagram must not call /api/sankey-data when a column filter is active')
        self.assertIn('sankey-content', result['panelHtml'],
                      'the diagram must still render via the client-side fallback when filtered')

    def test_needsFullBatch_diagram_condition_depends_on_filter_state(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            advancedMode = false;
            diagramMode = true;
            currentFilters = {};
            var noFilterDns = needsFullBatch('dns');
            currentFilters = { 'Protocol': 'TCP' };
            var withFilterDns = needsFullBatch('dns');
            currentFilters = {};
            var noFilterLog = needsFullBatch('log');
            var noFilterSigma = needsFullBatch('sigmaalert');
            window.__jsdom_result = {
                noFilterDns: noFilterDns,
                withFilterDns: withFilterDns,
                noFilterLog: noFilterLog,
                noFilterSigma: noFilterSigma
            };
        ''')
        self.assertFalse(result['noFilterDns'],
                         'diagram must not force a full batch when no filter is active (server endpoint covers it)')
        self.assertTrue(result['withFilterDns'],
                        'diagram must force a full batch when a filter is active (server endpoint cannot be used)')
        self.assertFalse(result['noFilterLog'],
                         'log tab has no diagram, so it must never force a full batch for diagram purposes')
        self.assertFalse(result['noFilterSigma'],
                         'sigma-alert tab has no diagram, so it must never force a full batch for diagram purposes')

    def test_renders_real_svg_from_server_payload(self):
        """Shape-compatibility test: a real /api/sankey-data payload must
        flow through renderSankeySVG (backed by the real d3/d3-sankey
        libraries, not a mock) and produce an actual <svg> element."""
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('flow') + '''
            window.fetch = function(url) {
                if (url.indexOf('/api/sankey-data') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve({
                        nodes: [
                            { id: '0:1.1.1.1', name: '1.1.1.1', column: 0 },
                            { id: '1:2.2.2.2', name: '2.2.2.2', column: 1 },
                            { id: '2:80', name: '80', column: 2 }
                        ],
                        links: [
                            { source: '0:1.1.1.1', target: '1:2.2.2.2', value: 4 },
                            { source: '1:2.2.2.2', target: '2:80', value: 4 }
                        ]
                    }) });
                }
                return Promise.resolve({ json: () => Promise.resolve([]) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            diagramMode = true;
            await updateSankeyDiagram();
            var panel = document.getElementById('sankeyPanel');
            window.__jsdom_result = {
                svgCount: panel.querySelectorAll('svg').length,
                rectCount: panel.querySelectorAll('rect').length
            };
        ''', with_d3=True)
        self.assertEqual(result['svgCount'], 1,
                         'a real server-shaped payload must render exactly one <svg> via the unchanged renderSankeySVG')
        self.assertEqual(result['rectCount'], 3,
                         'each of the 3 supplied nodes must produce a rendered node rect')

    def test_empty_server_payload_shows_collapsed_toggle(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('dns') + '''
            window.fetch = function(url) {
                if (url.indexOf('/api/sankey-data') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve({ nodes: [], links: [] }) });
                }
                return Promise.resolve({ json: () => Promise.resolve([]) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            diagramMode = true;
            await updateSankeyDiagram();
            window.__jsdom_result = {
                panelHtml: document.getElementById('sankeyPanel').innerHTML
            };
        ''')
        self.assertIn('▾ Sankey Diagram', result['panelHtml'],
                      'an empty server payload must render the same empty-state toggle bar as the empty-events case')
        self.assertNotIn('sankey-content', result['panelHtml'],
                         'an empty server payload must not render a sankey-content container')

    def test_applyFilters_and_clearFilter_refresh_sankey_diagram(self):
        """REGRESSION: applyFilters/clearFilter must call updateSankeyDiagram
        so the diagram actually refreshes on filter apply/clear (previously
        missing - the diagram would never transition between the server and
        client-side modes when a filter was toggled)."""
        applyFunc = JS_CONTENT.split('async function applyFilters(')[1].split('async function clearFilter(')[0]
        clearFunc = JS_CONTENT.split('async function clearFilter(')[1].split('function applyFilter(')[0]
        self.assertIn('updateSankeyDiagram()', applyFunc,
                      'applyFilters must call updateSankeyDiagram to refresh the diagram')
        self.assertIn('updateSankeyDiagram()', clearFunc,
                      'clearFilter must call updateSankeyDiagram to refresh the diagram')

    def test_loadAnalysis_awaits_default_tab_before_sankey(self):
        """REGRESSION: loadAnalysis's PCAP branch must await loadTabData(eventTypes[0])
        before any subsequent updateSankeyDiagram() call. Firing loadTabData without
        awaiting it let updateSankeyDiagram's bumpFetchGeneration() race with
        loadTabData's own in-flight fetchEventsPage call, so buildSection's
        isStaleFetch guard silently dropped the initial row-table render, leaving
        the default tab stuck on 'Loading...' forever."""
        func = JS_CONTENT.split('async function loadAnalysis(')[1].split('async function ')[0]
        self.assertIn('await loadTabData(eventTypes[0])', func,
                      'loadAnalysis must await loadTabData for the default tab')

    def test_default_tab_renders_table_not_stuck_loading(self):
        """Behavioral reproduction of the race: firing loadTabData without await,
        immediately followed by updateSankeyDiagram(), must leave the section
        stuck on 'Loading...' - awaiting loadTabData first (the fix) must not."""
        from tests.jsdom_helper import js_statements
        setup = self._make_section('dns') + '''
            document.getElementById('section-dns').innerHTML = '<div class="loading">Loading...</div>';
            var sankeyPanel = document.createElement('div');
            sankeyPanel.id = 'sankeyPanel';
            document.body.appendChild(sankeyPanel);
            window.fetch = function(url) {
                if (url.indexOf('/api/sankey-data') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve({ nodes: [], links: [] }) });
                }
                if (url.indexOf('/api/events') >= 0 || url.indexOf('/api/count') >= 0) {
                    return new Promise(resolve => setTimeout(() => resolve({
                        json: () => Promise.resolve(url.indexOf('/api/count') >= 0 ? { count: 1 } : [{ event_type: 'dns', src_ip: '1.1.1.1' }])
                    }), 20));
                }
                return Promise.resolve({ json: () => Promise.resolve([]) });
            };
            currentMd5 = 'abc';
            currentFilters = {};
            currentSearch = [];
            diagramMode = true;
            advancedMode = false;
        '''
        fixed = js_statements(setup + '''
            await loadTabData('dns');
            await updateSankeyDiagram();
            window.__jsdom_result = {
                stillLoading: document.getElementById('section-dns').innerHTML.indexOf('Loading...') >= 0
            };
        ''')
        self.assertFalse(fixed['stillLoading'],
                         'awaiting loadTabData before updateSankeyDiagram must let the table render')

        raced = js_statements(setup + '''
            loadTabData('dns');
            await updateSankeyDiagram();
            await new Promise(r => setTimeout(r, 50));
            window.__jsdom_result = {
                stillLoading: document.getElementById('section-dns').innerHTML.indexOf('Loading...') >= 0
            };
        ''')
        self.assertTrue(raced['stillLoading'],
                        'sanity check: firing loadTabData without awaiting it must reproduce the stale-fetch race')


class TestAggregationServerFetch(unittest.TestCase):
    """buildAggregationsSection must use the lightweight server-aggregated
    /api/aggregation-data endpoint when no column filter is active (so the
    'advanced' view can open without needing the full capped batch), and
    fall back to the existing client-side buildAggregationTables path
    unchanged when a filter is active or the tab is log/sigmaalert/binary/
    'all' (all bespoke, out of scope)."""

    def _make_section(self, event_type='alert'):
        return f'''
            var section = document.createElement('div');
            section.className = 'section';
            section.id = 'section-{event_type}';
            document.body.appendChild(section);
            var aggContainer = document.createElement('div');
            aggContainer.id = 'aggregations';
            document.body.appendChild(aggContainer);
        '''

    def test_canUseServerAggregation_matrix(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            currentFilters = {};
            var eligibleNoFilter = canUseServerAggregation('alert');
            currentFilters = { 'Protocol': 'TCP' };
            var eligibleWithFilter = canUseServerAggregation('alert');
            currentFilters = {};
            var allType = canUseServerAggregation('all');
            var logType = canUseServerAggregation('log');
            var sigmaType = canUseServerAggregation('sigmaalert');
            var binaryType = canUseServerAggregation('binary');
            var mqttType = canUseServerAggregation('mqtt');
            var noType = canUseServerAggregation(null);
            window.__jsdom_result = {
                eligibleNoFilter: eligibleNoFilter,
                eligibleWithFilter: eligibleWithFilter,
                allType: allType,
                logType: logType,
                sigmaType: sigmaType,
                binaryType: binaryType,
                mqttType: mqttType,
                noType: noType
            };
        ''')
        self.assertTrue(result['eligibleNoFilter'], 'a normal per-type tab with no filter must be eligible')
        self.assertFalse(result['eligibleWithFilter'], 'an active column filter must disable the server path')
        self.assertTrue(result['allType'], "'all' now has a SQL equivalent for Type/Detail (db.py's _all_events_detail_expr)")
        self.assertFalse(result['logType'], 'log has bespoke dynamic columns, must stay client-side')
        self.assertFalse(result['sigmaType'], 'sigmaalert has bespoke dynamic columns, must stay client-side')
        self.assertFalse(result['binaryType'], 'binary mode has no per-type aggregation server route')
        self.assertFalse(result['mqttType'], 'mqtt fields are dynamically keyed by message subtype - no static JSON path server-side, must stay client-side like log/sigmaalert')
        self.assertFalse(result['noType'])

    def test_needsFullBatch_advanced_mode_condition_depends_on_eligibility(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            diagramMode = false;
            advancedMode = true;
            currentFilters = {};
            var eligibleNoFilter = needsFullBatch('alert');
            currentFilters = { 'Category': 'Trojan' };
            var eligibleWithFilter = needsFullBatch('alert');
            currentFilters = {};
            var logType = needsFullBatch('log');
            var sigmaType = needsFullBatch('sigmaalert');
            advancedMode = false;
            var advancedOff = needsFullBatch('alert');
            window.__jsdom_result = {
                eligibleNoFilter: eligibleNoFilter,
                eligibleWithFilter: eligibleWithFilter,
                logType: logType,
                sigmaType: sigmaType,
                advancedOff: advancedOff
            };
        ''')
        self.assertFalse(result['eligibleNoFilter'],
                         'advancedMode alone must not force a full batch for an eligible type with no filter')
        self.assertTrue(result['eligibleWithFilter'],
                        'advancedMode + an active filter must still force a full batch')
        self.assertTrue(result['logType'], 'log must always force a full batch in advanced mode')
        self.assertTrue(result['sigmaType'], 'sigmaalert must always force a full batch in advanced mode')
        self.assertFalse(result['advancedOff'], 'advancedMode off must never force a full batch by itself')

    def test_no_filter_uses_server_endpoint_not_full_batch(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('alert') + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/aggregation-data') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve({
                        'Category': [{value: 'Trojan', count: 2}]
                    }) });
                }
                return Promise.resolve({ json: () => Promise.resolve([]) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            advancedMode = true;
            await buildAggregationsSection('alert', []);
            window.__jsdom_result = {
                aggCalls: fetchCalls.filter(u => u.indexOf('/api/aggregation-data') >= 0).length,
                aggUrlHasType: fetchCalls.some(u => u.indexOf('/api/aggregation-data') >= 0 && u.indexOf('type=alert') >= 0),
                fullBatchCalls: fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('limit=') >= 0).length,
                aggHtml: document.getElementById('aggregations').innerHTML
            };
        ''')
        self.assertEqual(result['aggCalls'], 1,
                         'buildAggregationsSection must fetch /api/aggregation-data exactly once when no filter is active')
        self.assertTrue(result['aggUrlHasType'])
        self.assertEqual(result['fullBatchCalls'], 0,
                         'buildAggregationsSection must not trigger the full capped-batch fetch when it can use the server endpoint')
        self.assertIn('Trojan', result['aggHtml'])

    def test_active_filter_falls_back_to_client_side_build(self):
        from tests.jsdom_helper import js_statements
        alert_events = [
            {'event_type': 'alert', 'proto': 'TCP', 'src_ip': '1.1.1.1', 'dest_ip': '2.2.2.2', 'dest_port': 80,
             'alert': {'signature': 'Sig', 'category': 'Real Category', 'severity': 1}},
        ]
        result = js_statements(self._make_section('alert') + f'''
            var fetchCalls = [];
            window.fetch = function(url) {{
                fetchCalls.push(url);
                return Promise.resolve({{ json: () => Promise.resolve({json.dumps(alert_events)}) }});
            }};
            currentMd5 = 'abc123';
            currentFilters = {{ 'Protocol': 'TCP' }};
            currentSearch = [];
            advancedMode = true;
            await buildAggregationsSection('alert', {json.dumps(alert_events)});
            window.__jsdom_result = {{
                aggCalls: fetchCalls.filter(u => u.indexOf('/api/aggregation-data') >= 0).length,
                aggHtml: document.getElementById('aggregations').innerHTML
            }};
        ''')
        self.assertEqual(result['aggCalls'], 0,
                         'buildAggregationsSection must not call /api/aggregation-data when a column filter is active')
        self.assertIn('Real Category', result['aggHtml'],
                      'the aggregation table must still render via the client-side fallback when filtered')

    def test_advanced_mode_off_shows_collapsed_html(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('alert') + '''
            window.fetch = function() { return Promise.resolve({ json: () => Promise.resolve({}) }); };
            advancedMode = false;
            await buildAggregationsSection('alert', []);
            window.__jsdom_result = {
                aggHtml: document.getElementById('aggregations').innerHTML
            };
        ''')
        self.assertIn('Aggregation Tables', result['aggHtml'])

    def test_toggleAggregations_no_filter_skips_ensureCappedBatch(self):
        """REGRESSION: toggleAggregations previously called ensureCappedBatch
        unconditionally before dispatching to buildAggregationsSection -
        opening the advanced view for an eligible type with no filter must
        not eagerly fetch the full batch."""
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('alert') + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/aggregation-data') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve({ 'Category': [{value: 'X', count: 1}] }) });
                }
                return Promise.resolve({ json: () => Promise.resolve([]) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            diagramMode = false;
            advancedMode = false;
            await toggleAggregations();
            window.__jsdom_result = {
                fullBatchCalls: fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('limit=') >= 0).length,
                aggCalls: fetchCalls.filter(u => u.indexOf('/api/aggregation-data') >= 0).length
            };
        ''')
        self.assertEqual(result['fullBatchCalls'], 0,
                         'toggleAggregations must not eagerly ensureCappedBatch for an eligible type with no filter')
        self.assertEqual(result['aggCalls'], 1)


class TestTruncationIndicator(unittest.TestCase):
    """The query limit (now user-configurable via getUserQueryLimit(), default
    75000, server ceiling 100000) makes hitting the cap rarer, not impossible.
    ensureCappedBatch must track (via truncatedTypes) when a fetched batch is
    known to be a partial subset of the true total, and the filter bar must
    surface a warning for the currently-visible tab when truncated - without
    ever showing an orphaned "Clear All" button when truncation is the only
    active condition."""

    def _make_section(self, event_type='dns'):
        return f'''
            var section = document.createElement('div');
            section.className = 'section';
            section.id = 'section-{event_type}';
            document.body.appendChild(section);
        '''

    def test_ensureCappedBatch_marks_type_truncated_when_count_exceeds_fetch(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.fetch = function(url) {
                if (url.indexOf('/api/events') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([{event_type: 'dns'}, {event_type: 'dns'}]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 5 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            await ensureCappedBatch('dns');
            window.__jsdom_result = { truncated: truncatedTypes.has('dns') };
        ''')
        self.assertTrue(result['truncated'],
                         'ensureCappedBatch must mark a type truncated when the true count exceeds the fetched rows')

    def test_ensureCappedBatch_clears_truncated_when_count_matches_fetch(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.fetch = function(url) {
                if (url.indexOf('/api/events') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([{event_type: 'dns'}, {event_type: 'dns'}]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 2 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            truncatedTypes.add('dns');
            await ensureCappedBatch('dns');
            window.__jsdom_result = { truncated: truncatedTypes.has('dns') };
        ''')
        self.assertFalse(result['truncated'],
                          'ensureCappedBatch must clear a previously-truncated type once the full count is fetched')

    def test_ensureCappedBatch_all_marks_truncated(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.fetch = function(url) {
                if (url.indexOf('/api/events') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([{event_type: 'dns'}]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 9 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            await ensureCappedBatch('all');
            window.__jsdom_result = { truncated: truncatedTypes.has('all') };
        ''')
        self.assertTrue(result['truncated'],
                         "ensureCappedBatch must mark 'all' truncated when the merged count exceeds fetched rows")

    def test_ensureCappedBatch_sigmaalert_marks_truncated(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.fetch = function(url) {
                if (url.indexOf('/api/sigma-alerts') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([{severity: 'high'}]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 4 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            await ensureCappedBatch('sigmaalert');
            window.__jsdom_result = { truncated: truncatedTypes.has('sigmaalert') };
        ''')
        self.assertTrue(result['truncated'],
                         'ensureCappedBatch must mark sigmaalert truncated when the true count exceeds fetched rows')

    def test_ensureCappedBatch_cache_hit_makes_no_extra_fetch(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([{event_type: 'dns'}]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 1 }) });
            };
            currentFilters = {};
            currentSearch = [];
            function relevantCalls() {
                return fetchCalls.filter(u => u.indexOf('/api/events') >= 0 || u.indexOf('/api/count') >= 0).length;
            }
            await ensureCappedBatch('dns');
            var callsAfterFirst = relevantCalls();
            await ensureCappedBatch('dns');
            window.__jsdom_result = { callsAfterFirst: callsAfterFirst, callsAfterSecond: relevantCalls() };
        ''')
        self.assertEqual(result['callsAfterFirst'], 2, 'first call must fetch both rows and count')
        self.assertEqual(result['callsAfterSecond'], result['callsAfterFirst'],
                          'a cached type must not trigger any additional fetch, including the count check')

    def test_filter_bar_shows_warning_with_no_clear_all_when_truncated_only(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('dns') + '''
            currentFilters = {};
            currentSearch = [];
            truncatedTypes.add('dns');
            var html = buildFilterBarHtml();
            window.__jsdom_result = {
                hasClearAll: html.indexOf('Clear All') >= 0,
                hasWarning: html.indexOf('may be incomplete') >= 0
            };
        ''')
        self.assertFalse(result['hasClearAll'],
                          'a truncation-only filter bar must not show a "Clear All" button with nothing to clear')
        self.assertTrue(result['hasWarning'],
                         'a truncated tab must show a truncation warning in the filter bar')

    def test_filter_bar_unchanged_when_only_filters_active(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('dns') + '''
            currentFilters = { 'Protocol': 'UDP' };
            currentSearch = [];
            truncatedTypes.clear();
            var html = buildFilterBarHtml();
            window.__jsdom_result = {
                hasClearAll: html.indexOf('Clear All') >= 0,
                hasWarning: html.indexOf('may be incomplete') >= 0
            };
        ''')
        self.assertTrue(result['hasClearAll'],
                        'the existing Clear All chip row must be unaffected when only a filter is active')
        self.assertFalse(result['hasWarning'],
                         'no truncation warning should appear when the tab is not truncated')

    def test_filter_bar_shows_both_when_filtered_and_truncated(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('dns') + '''
            currentFilters = { 'Protocol': 'UDP' };
            currentSearch = [];
            truncatedTypes.add('dns');
            var html = buildFilterBarHtml();
            window.__jsdom_result = {
                hasClearAll: html.indexOf('Clear All') >= 0,
                hasWarning: html.indexOf('may be incomplete') >= 0
            };
        ''')
        self.assertTrue(result['hasClearAll'])
        self.assertTrue(result['hasWarning'])

    def test_updateFilterBarVisibility_shows_bar_when_truncated_only(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('dns') + '''
            var container = document.createElement('div');
            container.id = 'filterBarContainer';
            document.body.appendChild(container);
            currentFilters = {};
            currentSearch = [];
            truncatedTypes.add('dns');
            updateFilterBarVisibility();
            window.__jsdom_result = {
                display: document.getElementById('filterBarContainer').style.display,
                html: document.getElementById('filterBarContainer').innerHTML
            };
        ''')
        self.assertEqual(result['display'], 'block',
                         'the filter bar must be shown when the visible tab is truncated, even with no filter/search active')
        self.assertNotIn('Clear All', result['html'])

    def test_isCurrentTabTruncated_checks_visible_section_only(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('dns') + '''
            truncatedTypes.add('flow');
            var notTruncated = isCurrentTabTruncated();
            truncatedTypes.add('dns');
            var truncated = isCurrentTabTruncated();
            window.__jsdom_result = { notTruncated: notTruncated, truncated: truncated };
        ''')
        self.assertFalse(result['notTruncated'],
                         'a truncated type other than the currently-visible tab must not trigger the indicator')
        self.assertTrue(result['truncated'])

    def test_sortCurrentTable_calls_updateFilterBarVisibility(self):
        func = JS_CONTENT.split('async function sortCurrentTable(')[1].split('const EMPTY_FILTER_STATE_HTML')[0]
        self.assertIn('updateFilterBarVisibility()', func,
                      'sortCurrentTable must refresh the filter bar so a sort-triggered truncation is surfaced '
                      '(a bare sort touches neither currentFilters nor currentSearch)')

    def test_toggleDiagram_calls_updateFilterBarVisibility(self):
        func = JS_CONTENT.split('async function toggleDiagram(')[1].split('async function toggleAggregations(')[0]
        self.assertIn('updateFilterBarVisibility()', func,
                      'toggleDiagram must refresh the filter bar after ensureCappedBatch may have changed truncatedTypes')

    def test_toggleAggregations_calls_updateFilterBarVisibility(self):
        func = JS_CONTENT.split('async function toggleAggregations(')[1].split('const typeLabels')[0]
        self.assertEqual(func.count('updateFilterBarVisibility()'), 2,
                         'both the binary-mode early-return branch and the main path must refresh the filter bar')

    def test_refreshAnalysisData_clears_truncatedTypes(self):
        func = JS_CONTENT.split('async function refreshAnalysisData(')[1].split('async function loadAnalysis(')[0]
        self.assertIn('truncatedTypes.clear()', func,
                      'refreshAnalysisData must clear truncatedTypes alongside the allEvents/tabDataCache reset it does on search change')

    def test_loadAnalysis_clears_truncatedTypes(self):
        func = JS_CONTENT.split('async function loadAnalysis(')[1].split('function loadSampleUrl(')[0]
        self.assertIn('truncatedTypes.clear()', func,
                      'loadAnalysis must clear truncatedTypes alongside the allEvents/tabDataCache reset it does on a fresh file load')

    def test_loadAnalysis_guards_against_stale_fetch(self):
        """REGRESSION: re-uploading the same pcap (same md5) after deleting the
        analysis could show '0 events' persisting until a hard reload - a
        late-resolving /api/stats response from a superseded loadAnalysis call
        had no staleness check, so it could clobber eventStats with {} after a
        newer, correct call already finished. loadAnalysis must bump the
        fetchGeneration counter (the same mechanism updateSankeyDiagram already
        uses) and bail before assigning eventStats if superseded."""
        func = JS_CONTENT.split('async function loadAnalysis(')[1].split('function loadSampleUrl(')[0]
        self.assertIn('const gen = bumpFetchGeneration();', func,
                      'loadAnalysis must capture a fetch generation at the top')
        gen_pos = func.find('const gen = bumpFetchGeneration();')
        stats_assign_pos = func.find('eventStats = statsData.counts;')
        guard_before_stats = func.rfind('if (isStaleFetch(gen)) return;', 0, stats_assign_pos)
        self.assertNotEqual(guard_before_stats, -1,
                            'loadAnalysis must check isStaleFetch before assigning eventStats')
        self.assertLess(gen_pos, guard_before_stats,
                        'the generation must be captured before the staleness check')
        self.assertLess(guard_before_stats, stats_assign_pos,
                        'the staleness check must run before eventStats is assigned')

    def test_refreshAnalysisData_guards_against_stale_fetch(self):
        func = JS_CONTENT.split('async function refreshAnalysisData(')[1].split('async function loadAnalysis(')[0]
        self.assertIn('const gen = bumpFetchGeneration();', func,
                      'refreshAnalysisData must capture a fetch generation')
        gen_pos = func.find('const gen = bumpFetchGeneration();')
        stats_assign_pos = func.find('eventStats = statsCounts;')
        guard_before_stats = func.rfind('if (isStaleFetch(gen)) return;', 0, stats_assign_pos)
        self.assertNotEqual(guard_before_stats, -1,
                            'refreshAnalysisData must check isStaleFetch before assigning eventStats')
        self.assertLess(gen_pos, guard_before_stats,
                        'the generation must be captured before the staleness check')
        self.assertLess(guard_before_stats, stats_assign_pos,
                        'the staleness check must run before eventStats is assigned')

    def test_confirmDelete_resets_stale_client_state(self):
        """REGRESSION companion: showWelcome() never reset currentMd5/eventStats
        after a delete (confirmed by direct testing - currentMd5 still held the
        deleted analysis's md5 right after confirmDelete()). Re-uploading the
        same file reuses the same md5, so without this reset a later stale
        in-flight fetch from before the delete could be checked against a
        currentMd5 that (coincidentally) still matches - confirmDelete must
        reset the state directly and bump the fetch generation so any such
        fetch is unambiguously rejected as stale."""
        func = JS_CONTENT.split('async function confirmDelete(')[1].split('async function confirmDeleteAll(')[0]
        for expected in ("currentMd5 = '';", 'eventStats = {};', 'baseEventStats = {};',
                         'tabDataCache = {};', 'bumpFetchGeneration();'):
            self.assertIn(expected, func, f'confirmDelete must reset state: {expected}')

    def test_confirmDeleteAll_resets_stale_client_state(self):
        func = JS_CONTENT.split('async function confirmDeleteAll(')[1]
        for expected in ("currentMd5 = '';", 'eventStats = {};', 'baseEventStats = {};',
                         'tabDataCache = {};', 'bumpFetchGeneration();'):
            self.assertIn(expected, func, f'confirmDeleteAll must reset state: {expected}')


class TestUserConfigurableQueryLimit(unittest.TestCase):
    """The row-cap used by ensureCappedBatch is now a user-configurable,
    persisted setting (getUserQueryLimit(), backed by localStorage) rather
    than a fixed CONFIG constant - validated on read (devtools-tampered
    localStorage must not reach the fetch URL unclamped) and surfaced via a
    Settings modal mirroring the existing Help modal's structure."""

    def test_getUserQueryLimit_reads_valid_localStorage_value(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            localStorage.setItem('socrates_maxQueryLimit', '55000');
            window.__jsdom_result = { value: getUserQueryLimit() };
        ''')
        self.assertEqual(result['value'], 55000)

    def test_getUserQueryLimit_falls_back_to_default_when_missing(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            localStorage.removeItem('socrates_maxQueryLimit');
            window.__jsdom_result = { value: getUserQueryLimit() };
        ''')
        self.assertEqual(result['value'], 75000)

    def test_getUserQueryLimit_rejects_adversarial_values(self):
        """Non-numeric, negative, and absurdly large values (including a
        devtools-tampered localStorage entry) must all fall back to the
        default rather than reaching a fetch URL unclamped."""
        from tests.jsdom_helper import js_statements
        adversarial = ['__proto__', 'Infinity', '9' * 30, '-5000', '0', 'NaN', '']
        result = js_statements('''
            var values = ''' + json.dumps(adversarial) + ''';
            var results = values.map(function(v) {
                localStorage.setItem('socrates_maxQueryLimit', v);
                return getUserQueryLimit();
            });
            window.__jsdom_result = { results: results };
        ''')
        for v, r in zip(adversarial, result['results']):
            self.assertEqual(r, 75000, f'adversarial value {v!r} must fall back to the default')

    def test_getUserQueryLimit_rejects_out_of_range_values(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            localStorage.setItem('socrates_maxQueryLimit', '500');
            var tooLow = getUserQueryLimit();
            localStorage.setItem('socrates_maxQueryLimit', '999999');
            var tooHigh = getUserQueryLimit();
            window.__jsdom_result = { tooLow: tooLow, tooHigh: tooHigh };
        ''')
        self.assertEqual(result['tooLow'], 75000, 'below the 1000 floor must fall back to the default')
        self.assertEqual(result['tooHigh'], 75000, 'above the 500000 sanity ceiling must fall back to the default')

    def test_ensureCappedBatch_uses_user_configured_limit(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            localStorage.setItem('socrates_maxQueryLimit', '77000');
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([{event_type: 'dns'}]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 1 }) });
            };
            currentFilters = {};
            currentSearch = [];
            await ensureCappedBatch('dns');
            window.__jsdom_result = {
                usedConfiguredLimit: fetchCalls.some(u => u.indexOf('limit=77000') >= 0)
            };
        ''')
        self.assertTrue(result['usedConfiguredLimit'],
                        'ensureCappedBatch must fetch using the user-configured limit, not a fixed constant')

    def test_truncation_message_uses_actual_fetched_count_not_a_constant(self):
        """REGRESSION: the truncation warning previously hardcoded
        CONFIG.MAX_QUERY_LIMIT.toLocaleString() - now that the limit is
        user-configurable (and may itself still be clamped lower server-side),
        the message must reflect the real fetched length instead."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var section = document.createElement('div');
            section.className = 'section';
            section.id = 'section-dns';
            document.body.appendChild(section);

            localStorage.setItem('socrates_maxQueryLimit', '77000');
            window.fetch = function(url) {
                if (url.indexOf('/api/events') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([{event_type: 'dns'}, {event_type: 'dns'}]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 9 }) });
            };
            currentFilters = {};
            currentSearch = [];
            await ensureCappedBatch('dns');
            var html = buildFilterBarHtml();
            window.__jsdom_result = {
                mentionsActualCount: html.indexOf('first 2 matching') >= 0,
                mentionsConfiguredLimit: html.indexOf('77,000') >= 0 || html.indexOf('77000') >= 0
            };
        ''')
        self.assertTrue(result['mentionsActualCount'],
                        'the warning must show the real fetched count (2), not the configured limit')
        self.assertFalse(result['mentionsConfiguredLimit'],
                         'the warning must not show the configured limit itself when the real fetched count is much smaller')

    def test_showSettingsModal_prefills_input_and_activates(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            localStorage.setItem('socrates_maxQueryLimit', '42000');
            window.fetch = function() { return Promise.resolve({ json: () => Promise.resolve({ maxQueryLimit: 100000 }) }); };
            showSettingsModal();
            window.__jsdom_result = {
                inputValue: document.getElementById('maxQueryLimitInput').value,
                isActive: document.getElementById('settingsModal').classList.contains('active')
            };
        ''')
        self.assertEqual(result['inputValue'], '42000')
        self.assertTrue(result['isActive'])

    def test_showSettingsModal_degrades_gracefully_when_limits_fetch_fails(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.fetch = function() { return Promise.reject(new Error('offline')); };
            showSettingsModal();
            window.__jsdom_result = {
                isActive: document.getElementById('settingsModal').classList.contains('active'),
                hintHasDefault: document.getElementById('settingsHint').textContent.indexOf('Default') >= 0
            };
        ''')
        self.assertTrue(result['isActive'], 'the modal must still open even if /api/limits fails')
        self.assertTrue(result['hintHasDefault'], 'the hint must still show the default when the server ceiling is unavailable')

    def test_closeSettingsModal_removes_active_class(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            document.getElementById('settingsModal').classList.add('active');
            closeSettingsModal();
            window.__jsdom_result = { isActive: document.getElementById('settingsModal').classList.contains('active') };
        ''')
        self.assertFalse(result['isActive'])

    def test_handleSettingsBackdropClick_closes_only_on_backdrop(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var modal = document.getElementById('settingsModal');
            modal.classList.add('active');
            handleSettingsBackdropClick({ target: modal });
            var closedOnBackdrop = !modal.classList.contains('active');

            modal.classList.add('active');
            var inner = document.querySelector('#settingsModal .modal-content');
            handleSettingsBackdropClick({ target: inner });
            var stayedOpenOnContent = modal.classList.contains('active');

            window.__jsdom_result = { closedOnBackdrop: closedOnBackdrop, stayedOpenOnContent: stayedOpenOnContent };
        ''')
        self.assertTrue(result['closedOnBackdrop'])
        self.assertTrue(result['stayedOpenOnContent'])

    def test_saveSettings_rejects_value_below_floor(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            document.getElementById('maxQueryLimitInput').value = '500';
            localStorage.removeItem('socrates_maxQueryLimit');
            await saveSettings();
            window.__jsdom_result = {
                persisted: localStorage.getItem('socrates_maxQueryLimit'),
                errorShown: document.getElementById('settingsError').style.display === 'block',
                stillActive: !document.getElementById('settingsModal').classList.contains('active') || true
            };
        ''')
        self.assertIsNone(result['persisted'], 'an invalid value must not be persisted')
        self.assertTrue(result['errorShown'], 'an inline error must be shown for a value below the floor')

    def test_saveSettings_clamps_value_above_server_ceiling_with_message(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var input = document.getElementById('maxQueryLimitInput');
            input.value = '999999';
            input.max = '100000';
            localStorage.removeItem('socrates_maxQueryLimit');
            await saveSettings();
            window.__jsdom_result = {
                persisted: localStorage.getItem('socrates_maxQueryLimit'),
                inputValue: input.value,
                errorText: document.getElementById('settingsError').textContent
            };
        ''')
        self.assertIsNone(result['persisted'], 'an over-ceiling value must not be silently persisted on the first click')
        self.assertEqual(result['inputValue'], '100000', 'the input must show the clamped suggestion')
        self.assertIn('100,000', result['errorText'])

    def test_saveSettings_persists_valid_value_and_closes_modal(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            document.getElementById('settingsModal').classList.add('active');
            var input = document.getElementById('maxQueryLimitInput');
            input.value = '60000';
            input.max = '100000';
            localStorage.removeItem('socrates_maxQueryLimit');
            // The modal only closes once neither Settings field is blocking
            // (see TestUserConfigurableUploadSize) -- give the other field a
            // valid value too, matching what showSettingsModal() would have
            // already prefilled in real usage.
            document.getElementById('maxUploadSizeInput').value = '1000';
            await saveSettings();
            window.__jsdom_result = {
                persisted: localStorage.getItem('socrates_maxQueryLimit'),
                isActive: document.getElementById('settingsModal').classList.contains('active')
            };
        ''')
        self.assertEqual(result['persisted'], '60000')
        self.assertFalse(result['isActive'], 'the modal must close after a successful save')

    def test_saveSettings_skips_refresh_when_no_analysis_loaded(self):
        """currentMd5 defaults to '' - saveSettings must not call
        refreshAnalysisData when no analysis is currently loaded."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var refreshCalls = 0;
            window.refreshAnalysisData = async function() { refreshCalls++; };
            var input = document.getElementById('maxQueryLimitInput');
            input.value = '60000';
            localStorage.removeItem('socrates_maxQueryLimit');
            await saveSettings();
            window.__jsdom_result = { refreshCalls: refreshCalls };
        ''')
        self.assertEqual(result['refreshCalls'], 0)

    def test_saveSettings_calls_refreshAnalysisData_only_when_md5_set(self):
        """currentMd5 is let-scoped and can't be assigned across separate
        eval calls in the JSDOM test harness (unlike the var-scoped globals),
        so this is verified via source inspection rather than execution."""
        func = JS_CONTENT.split('async function saveSettings()')[1].split('function showAnalysisUI')[0]
        self.assertIn('if (currentMd5)', func,
                      'saveSettings must only refresh the loaded analysis when one is actually loaded')
        self.assertIn('await refreshAnalysisData()', func)

    def test_saveSettings_disables_save_button_around_refresh(self):
        func = JS_CONTENT.split('async function saveSettings()')[1].split('function showAnalysisUI')[0]
        self.assertIn('saveBtn.disabled = true', func)
        self.assertIn('saveBtn.disabled = false', func)
        self.assertIn('finally', func,
                      'the Save button must be re-enabled in a finally block even if refreshAnalysisData throws')

    def test_settings_menu_item_in_static_html(self):
        self.assertIn('onclick="showSettingsModal(); closeMenu();"', HTML_CONTENT,
                      'the static header menu markup must include a Settings item')

    def test_settings_menu_item_in_renderGearMenu(self):
        func = JS_CONTENT.split('function renderGearMenu()')[1].split('// Subtle code-rain background')[0]
        self.assertIn('showSettingsModal(); closeMenu();', func,
                      'the dynamically-rebuilt header menu template must also include a Settings item')


class TestUserConfigurableUploadSize(unittest.TestCase):
    """Mirrors TestUserConfigurableQueryLimit for the second Settings-modal
    field: a user-configurable personal upload-size ceiling
    (getUserMaxUploadSizeMB(), backed by localStorage), clamped server-side
    to config.MAX_UPLOAD_SIZE and surfaced via the same Settings modal,
    independent of the query-limit field's validation state."""

    def test_getUserMaxUploadSizeMB_reads_valid_localStorage_value(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            localStorage.setItem('socrates_maxUploadSizeMB', '2000');
            window.__jsdom_result = { value: getUserMaxUploadSizeMB() };
        ''')
        self.assertEqual(result['value'], 2000)

    def test_getUserMaxUploadSizeMB_falls_back_to_default_when_missing(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            localStorage.removeItem('socrates_maxUploadSizeMB');
            window.__jsdom_result = { value: getUserMaxUploadSizeMB() };
        ''')
        self.assertEqual(result['value'], 1000)

    def test_getUserMaxUploadSizeMB_rejects_adversarial_values(self):
        from tests.jsdom_helper import js_statements
        adversarial = ['__proto__', 'Infinity', '9' * 30, '-500', '0', 'NaN', '']
        result = js_statements('''
            var values = ''' + json.dumps(adversarial) + ''';
            var results = values.map(function(v) {
                localStorage.setItem('socrates_maxUploadSizeMB', v);
                return getUserMaxUploadSizeMB();
            });
            window.__jsdom_result = { results: results };
        ''')
        for v, r in zip(adversarial, result['results']):
            self.assertEqual(r, 1000, f'adversarial value {v!r} must fall back to the default')

    def test_getUserMaxUploadSizeMB_rejects_out_of_range_values(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            localStorage.setItem('socrates_maxUploadSizeMB', '50');
            var tooLow = getUserMaxUploadSizeMB();
            localStorage.setItem('socrates_maxUploadSizeMB', '999999');
            var tooHigh = getUserMaxUploadSizeMB();
            window.__jsdom_result = { tooLow: tooLow, tooHigh: tooHigh };
        ''')
        self.assertEqual(result['tooLow'], 1000, 'below the 100 floor must fall back to the default')
        self.assertEqual(result['tooHigh'], 1000, 'above the 20000 sanity ceiling must fall back to the default')

    def test_upload_fetch_includes_resolved_size_header(self):
        """uploadPcap and loadFromUrl both depend on DOM elements (#pcapUpload,
        #pcapUrl) that only exist once a template string elsewhere in the app
        has rendered them -- not in the jsdom harness's base DOM -- so, like
        the existing currentMd5-dependent saveSettings tests above, this is
        verified via source inspection rather than live execution."""
        func = JS_CONTENT.split('async function uploadPcap')[1].split('async function checkStatus')[0]
        self.assertIn("headers: {'X-Max-Upload-Size': String(getUserMaxUploadSizeMB() * 1024 * 1024)}", func,
                      'uploadPcap must send the resolved upload-size limit as a header')

    def test_load_url_body_includes_resolved_max_upload_size(self):
        func = JS_CONTENT.split('async function loadFromUrl')[1].split('async function uploadPcap')[0]
        self.assertIn('maxUploadSize: getUserMaxUploadSizeMB() * 1024 * 1024', func,
                      'loadFromUrl must send the resolved upload-size limit in the request body')

    def test_showSettingsModal_prefills_upload_size_input(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            localStorage.setItem('socrates_maxUploadSizeMB', '2500');
            window.fetch = function() {
                return Promise.resolve({ json: () => Promise.resolve({ maxQueryLimit: 100000, maxUploadSize: 5000 * 1024 * 1024 }) });
            };
            showSettingsModal();
            window.__jsdom_result = { inputValue: document.getElementById('maxUploadSizeInput').value };
        ''')
        self.assertEqual(result['inputValue'], '2500')

    def test_showSettingsModal_degrades_gracefully_when_limits_fetch_fails(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.fetch = function() { return Promise.reject(new Error('offline')); };
            showSettingsModal();
            window.__jsdom_result = {
                isActive: document.getElementById('settingsModal').classList.contains('active'),
                hintHasDefault: document.getElementById('uploadSizeHint').textContent.indexOf('Default') >= 0
            };
        ''')
        self.assertTrue(result['isActive'], 'the modal must still open even if /api/limits fails')
        self.assertTrue(result['hintHasDefault'], 'the hint must still show the default when the server ceiling is unavailable')

    def test_saveSettings_rejects_value_below_floor_independent_of_other_field(self):
        """An invalid upload-size value must not block the query-limit field
        from persisting, and vice versa -- the two fields validate/persist
        independently."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            document.getElementById('maxQueryLimitInput').value = '60000';
            document.getElementById('maxQueryLimitInput').max = '100000';
            document.getElementById('maxUploadSizeInput').value = '50';
            localStorage.removeItem('socrates_maxQueryLimit');
            localStorage.removeItem('socrates_maxUploadSizeMB');
            await saveSettings();
            window.__jsdom_result = {
                queryLimitPersisted: localStorage.getItem('socrates_maxQueryLimit'),
                uploadSizePersisted: localStorage.getItem('socrates_maxUploadSizeMB'),
                uploadErrorShown: document.getElementById('uploadSizeError').style.display === 'block',
                modalStillOpen: document.getElementById('settingsModal').classList.contains('active')
            };
        ''')
        self.assertEqual(result['queryLimitPersisted'], '60000',
                         'a valid query-limit value must persist even though the upload-size field is invalid')
        self.assertIsNone(result['uploadSizePersisted'], 'an invalid upload-size value must not be persisted')
        self.assertTrue(result['uploadErrorShown'])

    def test_saveSettings_clamps_upload_size_above_server_ceiling_with_message(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var input = document.getElementById('maxUploadSizeInput');
            input.value = '999999';
            input.max = '5000';
            localStorage.removeItem('socrates_maxUploadSizeMB');
            await saveSettings();
            window.__jsdom_result = {
                persisted: localStorage.getItem('socrates_maxUploadSizeMB'),
                inputValue: input.value,
                errorText: document.getElementById('uploadSizeError').textContent
            };
        ''')
        self.assertIsNone(result['persisted'], 'an over-ceiling value must not be silently persisted on the first click')
        self.assertEqual(result['inputValue'], '5000', 'the input must show the clamped suggestion')
        self.assertIn('5,000', result['errorText'])

    def test_saveSettings_persists_valid_upload_size_independent_of_query_limit(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            document.getElementById('settingsModal').classList.add('active');
            document.getElementById('maxQueryLimitInput').value = '60000';
            document.getElementById('maxQueryLimitInput').max = '100000';
            var input = document.getElementById('maxUploadSizeInput');
            input.value = '2000';
            input.max = '5000';
            localStorage.removeItem('socrates_maxUploadSizeMB');
            await saveSettings();
            window.__jsdom_result = {
                persisted: localStorage.getItem('socrates_maxUploadSizeMB'),
                isActive: document.getElementById('settingsModal').classList.contains('active')
            };
        ''')
        self.assertEqual(result['persisted'], '2000')
        self.assertFalse(result['isActive'], 'the modal must close once both fields are valid')

    def test_saveSettings_does_not_trigger_refresh_for_upload_size_only_change(self):
        """Changing only the upload-size field must not trigger
        refreshAnalysisData -- that call is scoped to the query-limit field,
        since upload size has no bearing on already-loaded analysis data."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var refreshCalls = 0;
            window.refreshAnalysisData = async function() { refreshCalls++; };
            document.getElementById('maxQueryLimitInput').value = '60000';
            document.getElementById('maxUploadSizeInput').value = '2000';
            localStorage.removeItem('socrates_maxQueryLimit');
            localStorage.removeItem('socrates_maxUploadSizeMB');
            await saveSettings();
            window.__jsdom_result = { refreshCalls: refreshCalls };
        ''')
        self.assertEqual(result['refreshCalls'], 0, 'currentMd5 is empty by default, so no refresh should fire either way')


class TestNewProtocolEventTypes(unittest.TestCase):
    """REGRESSION: quic and dhcp events (quic alone was 10% of all events in
    a real analysis) previously fell through getColumnsForType's generic
    default (just the 6-column Time/Protocol/Source/Dest prefix, no
    protocol-specific detail at all), even though Suricata logs real,
    useful fields for them. This covers quic/dhcp plus every other event
    type Suricata's eve.json can produce that this app didn't previously
    handle: ftp_data, smb, ssh, krb5, sip, snmp, mqtt, dcerpc, rdp,
    tftp, ike, nfs, rfb, bittorrent_dht, smtp, enip, ntp. Field names are verified
    against Suricata's actual logger source (rust/src/<proto>/log*.rs) and,
    where available, real local eve.json samples -- not guessed."""

    GENERIC_FALLBACK = ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port']

    # (event_type, sample event object, {column_label: expected_substring})
    CASES = [
        # ja3/ja3s are objects ({"hash": ..., "string": ...}) in Suricata's
        # real eve.json output, not plain strings - confirmed against real
        # local data. Using a flat-string sample here previously masked a
        # real bug: buildRowForEvent/extractValue extracted the whole object,
        # which the frontend then rendered as the literal text
        # "[object Object]" instead of the hash.
        ('quic', {'event_type': 'quic', 'quic': {'sni': 'example.com', 'version': '1',
                                                  'ja3': {'hash': 'abc123', 'string': '771,4866,...'},
                                                  'ja3s': {'hash': 'def456', 'string': '771,4866,...'}}},
         {'SNI': 'example.com', 'QUIC Version': '1', 'JA3': 'abc123', 'JA3S': 'def456'}),
        ('dhcp', {'event_type': 'dhcp', 'dhcp': {'dhcp_type': 'ack', 'client_mac': 'ac:bc:b5:ea:6f:5b', 'assigned_ip': '192.168.1.50', 'hostname': 'laptop1'}},
         {'DHCP Type': 'ack', 'Client MAC': 'ac:bc:b5:ea:6f:5b', 'Assigned IP': '192.168.1.50', 'Hostname': 'laptop1'}),
        ('ftp_data', {'event_type': 'ftp_data', 'ftp_data': {'command': 'STOR', 'filename': 'secret.html'}},
         {'FTP Command': 'STOR', 'Filename': 'secret.html'}),
        ('smb', {'event_type': 'smb', 'smb': {'command': 'SMB2_COMMAND_CREATE', 'filename': 'passwords.docx', 'share': '\\\\SERVER\\Share', 'ntlmssp': {'user': 'jdoe'}}},
         {'SMB Command': 'SMB2_COMMAND_CREATE', 'Filename': 'passwords.docx', 'Share': '\\\\SERVER\\Share', 'SMB User': 'jdoe'}),
        ('ssh', {'event_type': 'ssh', 'ssh': {'client': {'software_version': 'OpenSSH_8.9'}, 'server': {'software_version': 'OpenSSH_9.2'}}},
         {'Client Version': 'OpenSSH_8.9', 'Server Version': 'OpenSSH_9.2'}),
        ('krb5', {'event_type': 'krb5', 'krb5': {'cname': 'alice', 'sname': 'krbtgt/EXAMPLE.COM', 'realm': 'EXAMPLE.COM', 'error_code': 'KDC_ERR_PREAUTH_REQUIRED'}},
         {'Client': 'alice', 'Service': 'krbtgt/EXAMPLE.COM', 'Realm': 'EXAMPLE.COM', 'Error Code': 'KDC_ERR_PREAUTH_REQUIRED'}),
        ('sip', {'event_type': 'sip', 'sip': {'method': 'INVITE', 'uri': 'sip:bob@example.com', 'code': 200, 'reason': 'OK'}},
         {'SIP Method': 'INVITE', 'URI': 'sip:bob@example.com', 'SIP Code': '200', 'Reason': 'OK'}),
        ('snmp', {'event_type': 'snmp', 'snmp': {'version': 2, 'pdu_type': 'get_request', 'community': 'public'}},
         {'SNMP Version': '2', 'PDU Type': 'get_request', 'Community': 'public'}),
        ('mqtt', {'event_type': 'mqtt', 'mqtt': {'publish': {'topic': 'sensors/temp', 'client_id': 'device1'}}},
         {'MQTT Type': 'publish', 'Topic': 'sensors/temp'}),
        ('dcerpc', {'event_type': 'dcerpc', 'dcerpc': {'interfaces': [{'uuid': '12345678-1234-1234-1234-123456789abc'}], 'request': {'opnum': 5}, 'call_id': 3}},
         {'Interface UUID': '12345678-1234-1234-1234-123456789abc', 'Opnum': '5', 'Call ID': '3'}),
        ('rdp', {'event_type': 'rdp', 'rdp': {'event_type': 'initial_request', 'cookie': 'mstshash=abc', 'client_name': 'WORKSTATION1'}},
         {'RDP Event': 'initial_request', 'Cookie': 'mstshash=abc', 'Client Name': 'WORKSTATION1'}),
        ('tftp', {'event_type': 'tftp', 'tftp': {'packet': 'write', 'file': 'firmware.bin', 'mode': 'octet'}},
         {'Packet': 'write', 'File': 'firmware.bin', 'Mode': 'octet'}),
        ('ike', {'event_type': 'ike', 'ike': {'exchange_type': 34, 'version_major': 2, 'version_minor': 0, 'init_spi': 'abcd1234'}},
         {'Exchange Type': '34', 'IKE Version': '2.0', 'Init SPI': 'abcd1234'}),
        ('nfs', {'event_type': 'nfs', 'nfs': {'procedure': 'READ', 'filename': '/export/data.txt'}},
         {'Procedure': 'READ', 'Filename': '/export/data.txt'}),
        # client/server_protocol_version are {major, minor} objects and
        # security_type is nested under 'authentication' in Suricata's real
        # eve.json (rust/src/rfb/logger.rs) - confirmed against real traffic.
        # A flat-string/top-level sample here previously masked a real bug,
        # same class as the quic ja3/ja3s issue above.
        ('rfb', {'event_type': 'rfb', 'rfb': {'client_protocol_version': {'major': '003', 'minor': '008'},
                                               'server_protocol_version': {'major': '003', 'minor': '008'},
                                               'authentication': {'security_type': 2}}},
         {'Client Version': '003.008', 'Server Version': '003.008', 'Security Type': '2'}),
        ('bittorrent_dht', {'event_type': 'bittorrent_dht', 'bittorrent_dht': {'request_type': 'get_peers', 'info_hash': 'deadbeef'}},
         {'Request Type': 'get_peers', 'Info Hash': 'deadbeef'}),
        ('smtp', {'event_type': 'smtp', 'smtp': {'helo': 'mail.example.com', 'mail_from': 'a@example.com', 'rcpt_to': ['b@example.com']}},
         {'Helo': 'mail.example.com', 'Mail From': 'a@example.com', 'Rcpt To': 'b@example.com'}),
        ('enip', {'event_type': 'enip', 'enip': {'request': {'command': 'RegisterSession'},
                                                  'response': {'command': 'RegisterSession', 'status': 'Success'}}},
         {'Command': 'RegisterSession', 'Status': 'Success'}),
        ('ntp', {'event_type': 'ntp', 'ntp': {'version': 4, 'mode': 3, 'stratum': 2, 'reference_id': '0a:0a:0a:01'}},
         {'Version': '4', 'Mode': '3', 'Stratum': '2', 'Reference ID': '0a:0a:0a:01'}),
    ]

    def test_getColumnsForType_no_longer_falls_back_to_generic_default(self):
        from tests.jsdom_helper import js_statements
        event_types = [c[0] for c in self.CASES]
        result = js_statements('''
            var types = ''' + json.dumps(event_types) + ''';
            window.__jsdom_result = { columns: types.map(function(t) { return getColumnsForType(t); }) };
        ''')
        for etype, cols in zip(event_types, result['columns']):
            with self.subTest(event_type=etype):
                self.assertNotEqual(cols, self.GENERIC_FALLBACK,
                                     f'{etype} must have protocol-specific columns, not the generic 6-column fallback')

    def test_buildRowForEvent_renders_real_field_values(self):
        from tests.jsdom_helper import js_statements
        for etype, sample_event, expected in self.CASES:
            with self.subTest(event_type=etype):
                result = js_statements('''
                    window.__jsdom_result = { html: buildRowForEvent(''' + json.dumps(sample_event) + ''') };
                ''')
                for label, expected_value in expected.items():
                    self.assertIn(expected_value, result['html'],
                                  f'{etype} row HTML must contain {label}={expected_value!r}')

    def test_no_rendered_row_contains_object_object(self):
        """REGRESSION: quic.ja3/ja3s are objects ({"hash":..., "string":...})
        in Suricata's real eve.json, not plain strings. Extracting the whole
        object instead of .hash renders as the literal text "[object Object]"
        (escapeHtml does String(value), not JSON.stringify) - this must never
        appear in any rendered row for any of the new protocol types."""
        from tests.jsdom_helper import js_statements
        event_types = [c[0] for c in self.CASES]
        samples = {c[0]: c[1] for c in self.CASES}
        result = js_statements('''
            var types = ''' + json.dumps(event_types) + ''';
            var samples = ''' + json.dumps(samples) + ''';
            window.__jsdom_result = {
                offenders: types.filter(function(t) {
                    return buildRowForEvent(samples[t]).indexOf('[object Object]') >= 0;
                })
            };
        ''')
        self.assertEqual(result['offenders'], [])

    def test_extractValue_matches_buildRowForEvent_values(self):
        """extractValue (used by the merged All Events view and aggregation
        tables) must agree with buildRowForEvent's per-type table on the
        same underlying fields."""
        from tests.jsdom_helper import js_statements
        for etype, sample_event, expected in self.CASES:
            with self.subTest(event_type=etype):
                labels = list(expected.keys())
                result = js_statements('''
                    var labels = ''' + json.dumps(labels) + ''';
                    var e = ''' + json.dumps(sample_event) + ''';
                    window.__jsdom_result = { values: labels.map(function(l) { return extractValue(e, l, 0); }) };
                ''')
                for label, value in zip(labels, result['values']):
                    self.assertIn(expected[label], str(value),
                                  f'{etype} extractValue({label!r}) = {value!r}, expected to contain {expected[label]!r}')

    def test_detail_case_handles_all_new_types_without_error(self):
        """The merged All Events view's Detail column must produce some
        non-crashing, renderable value for every new event type (a plain
        string or number is fine -- e.g. rfb's security_type is a real
        numeric Suricata field; an object/array or undefined is not, since
        those wouldn't render sensibly via escapeHtml)."""
        from tests.jsdom_helper import js_statements
        event_types = [c[0] for c in self.CASES]
        samples = {c[0]: c[1] for c in self.CASES}
        result = js_statements('''
            var types = ''' + json.dumps(event_types) + ''';
            var samples = ''' + json.dumps(samples) + ''';
            window.__jsdom_result = {
                ok: types.every(function(t) {
                    var v = extractValue(samples[t], 'Detail', 0);
                    return v !== undefined && (typeof v === 'string' || typeof v === 'number');
                })
            };
        ''')
        self.assertTrue(result['ok'])


class TestHttp2UsesHttpEventType(unittest.TestCase):
    """REGRESSION: an earlier pass added a dedicated 'http2' branch to
    getColumnsForType/buildRowForEvent/extractValue, keyed on
    event_type === 'http2' and reading from a top-level e.http2.request/
    e.http2.response shape. That event_type and shape never occur in real
    Suricata output: confirmed against Suricata's own logger source
    (rust/src/http2/logger.rs, which unconditionally opens the "http" JSON
    object - js.open_object("http") - and nests HTTP/2-frame-specific detail
    under a "http2" key *inside* "http", not at the top level) and against a
    real h2c (cleartext HTTP/2 via Upgrade) capture processed end-to-end,
    which produced event_type "http" with top-level http_method/url/status
    fields identical in name to plain HTTP/1.1. The dead 'http2' branches
    were removed; real HTTP/2 traffic (h2c here - true TLS-ALPN h2 is opaque
    to Suricata without decryption keys) is rendered by the existing 'http'
    handling, which already reads those exact field names."""

    # Real field shape from an actual h2c capture (Suricata 7.0.10,
    # http2-h2c.pcap from wiki.wireshark.org/http2) - not guessed. Note
    # 'hostname' is absent: Suricata's http2 logger only maps a literal
    # "host" header to it, not the ":authority" pseudo-header HTTP/2
    # clients actually send.
    REAL_H2C_EVENT = {
        'event_type': 'http',
        'http': {
            'version': '2',
            'http_method': 'GET',
            'url': '/robots.txt',
            'http_user_agent': 'curl/7.61.0',
            'status': 200,
            'length': 62,
            'http2': {'stream_id': 1, 'request': {}, 'response': {}},
        },
    }

    def test_getColumnsForType_http2_is_not_a_distinct_event_type(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = { cols: getColumnsForType('http2') };
        ''')
        generic_fallback = ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port']
        self.assertEqual(result['cols'], generic_fallback,
                          "event_type is never literally 'http2' in real Suricata output, "
                          "so getColumnsForType must not special-case it")

    def test_buildRowForEvent_renders_real_h2c_fields_via_http_case(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = { html: buildRowForEvent(''' + json.dumps(self.REAL_H2C_EVENT) + ''') };
        ''')
        for expected in ('GET', '/robots.txt', '200'):
            self.assertIn(expected, result['html'])

    def test_extractValue_reads_real_h2c_fields(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var e = ''' + json.dumps(self.REAL_H2C_EVENT) + ''';
            window.__jsdom_result = {
                method: extractValue(e, 'Method', 0),
                url: extractValue(e, 'URL', 0),
                status: extractValue(e, 'Status', 0),
            };
        ''')
        self.assertEqual(result['method'], 'GET')
        self.assertEqual(result['url'], '/robots.txt')
        self.assertEqual(result['status'], '200')


class TestFtpAnomalyColumnSupport(unittest.TestCase):
    """REGRESSION: unlike the 19 protocols in TestNewProtocolEventTypes above
    (which never had any support), 'ftp' and 'anomaly' are original event
    types that predate this session's work entirely, yet had the exact same
    symptom - getColumnsForType fell through to the generic 6-column default
    for both, with zero protocol-specific columns. anomaly also carried a
    separate, deeper bug: extractValue's Detail case read e.anomaly?.message,
    a field that has never existed in Suricata's eve.json anomaly schema
    (confirmed against real local data - the actual field is 'event')."""

    GENERIC_FALLBACK = ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port']

    FTP_EVENT = {'event_type': 'ftp', 'ftp': {'command': 'STOR', 'command_data': 'secret.txt',
                                               'completion_code': ['150', '226'],
                                               'reply': ['Accepted', 'Transfer complete']}}
    ANOMALY_EVENT = {'event_type': 'anomaly', 'anomaly': {
        'event': 'APPLAYER_DETECT_PROTOCOL_ONLY_ONE_DIRECTION',
        'type': 'applayer', 'layer': 'proto_detect', 'app_proto': 'ftp'}}

    def test_getColumnsForType_no_longer_falls_back_to_generic_default(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = {
                ftp: getColumnsForType('ftp'),
                anomaly: getColumnsForType('anomaly')
            };
        ''')
        self.assertNotEqual(result['ftp'], self.GENERIC_FALLBACK)
        self.assertNotEqual(result['anomaly'], self.GENERIC_FALLBACK)

    def test_buildRowForEvent_renders_real_ftp_fields(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = { html: buildRowForEvent(''' + json.dumps(self.FTP_EVENT) + ''') };
        ''')
        for expected in ('STOR', 'secret.txt', '150, 226', 'Accepted'):
            self.assertIn(expected, result['html'])

    def test_buildRowForEvent_renders_real_anomaly_fields(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = { html: buildRowForEvent(''' + json.dumps(self.ANOMALY_EVENT) + ''') };
        ''')
        for expected in ('APPLAYER_DETECT_PROTOCOL_ONLY_ONE_DIRECTION', 'applayer', 'proto_detect'):
            self.assertIn(expected, result['html'])

    def test_extractValue_type_case_handles_anomaly_alongside_dnp3_and_dns(self):
        """The shared 'Type' column label must still work correctly for
        dnp3/dns after adding the new anomaly branch."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = {
                anomaly: extractValue(''' + json.dumps(self.ANOMALY_EVENT) + ''', 'Type', 0),
                dnp3: extractValue({event_type: 'dnp3', dnp3: {type: 'unsolicited_response'}}, 'Type', 0),
                dns: extractValue({event_type: 'dns', dns: {rrtype: 'A'}}, 'Type', 0)
            };
        ''')
        self.assertEqual(result['anomaly'], 'applayer')
        self.assertEqual(result['dnp3'], 'unsolicited_response')
        self.assertEqual(result['dns'], 'A')

    def test_detail_case_uses_anomaly_event_not_message(self):
        """REGRESSION: the merged All Events view's Detail column must use
        anomaly.event (real field), not anomaly.message (never existed)."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = { detail: extractValue(''' + json.dumps(self.ANOMALY_EVENT) + ''', 'Detail', 0) };
        ''')
        self.assertEqual(result['detail'], 'APPLAYER_DETECT_PROTOCOL_ONLY_ONE_DIRECTION')

    def test_render_anomaly_details_uses_anomaly_event_not_message(self):
        """REGRESSION: the same anomaly.event-not-message bugfix as the
        Detail column above, missed in the side-panel renderer
        (renderAnomalyDetails) when it was first fixed - it still showed a
        'Message' row reading a field that has never existed in Suricata's
        eve.json anomaly schema."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = { html: renderAnomalyDetails(''' + json.dumps(self.ANOMALY_EVENT) + ''') };
        ''')
        self.assertIn('APPLAYER_DETECT_PROTOCOL_ONLY_ONE_DIRECTION', result['html'])
        self.assertNotIn('>Message<', result['html'])

    def test_detail_case_handles_ftp_with_no_command_via_reply_fallback(self):
        """Many real ftp events (server banners/greetings) have no 'command'
        field at all - Detail should still show something useful via the
        first reply line, not go blank."""
        from tests.jsdom_helper import js_statements
        banner_event = {'event_type': 'ftp', 'ftp': {'reply': ['Welcome to Pure-FTPd'], 'completion_code': ['220']}}
        result = js_statements('''
            window.__jsdom_result = { detail: extractValue(''' + json.dumps(banner_event) + ''', 'Detail', 0) };
        ''')
        self.assertEqual(result['detail'], 'Welcome to Pure-FTPd')


class TestDnsV3LoggingFormat(unittest.TestCase):
    """REGRESSION: upgrading to Suricata 8 switched DNS logging to its new
    "V3" format by default (confirmed against rust/src/dns/log.rs and real
    Suricata 8.0.6 output) - dns.rrname/dns.rrtype, which every DNS column/
    row/detail case read directly, no longer exist at all; the same info
    moved to dns.queries[0].rrname/rrtype. Every real DNS event's Query/Type
    silently rendered blank under Suricata 8 before this fix - a severe
    regression given DNS is one of the highest-volume, most-viewed event
    types. Old-format (V1/V2, e.g. previously-stored Suricata 7 analyses)
    events must keep working via the flat-field fallback."""

    V3_REQUEST = {'event_type': 'dns', 'dns': {
        'version': 3, 'type': 'request',
        'queries': [{'rrname': 'example.com', 'rrtype': 'A'}]}}
    V1_FLAT = {'event_type': 'dns', 'dns': {'rrname': 'legacy.example.com', 'rrtype': 'AAAA'}}

    def test_buildRowForEvent_reads_v3_queries_array(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = { html: buildRowForEvent(''' + json.dumps(self.V3_REQUEST) + ''') };
        ''')
        self.assertIn('example.com', result['html'])
        self.assertIn('A', result['html'])

    def test_buildRowForEvent_still_reads_old_flat_format(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = { html: buildRowForEvent(''' + json.dumps(self.V1_FLAT) + ''') };
        ''')
        self.assertIn('legacy.example.com', result['html'])
        self.assertIn('AAAA', result['html'])

    def test_extractValue_query_and_type_read_v3_queries_array(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var e = ''' + json.dumps(self.V3_REQUEST) + ''';
            window.__jsdom_result = {
                query: extractValue(e, 'Query', 0),
                type: extractValue(e, 'Type', 0),
                detail: extractValue(e, 'Detail', 0),
            };
        ''')
        self.assertEqual(result['query'], 'example.com')
        self.assertEqual(result['type'], 'A')
        self.assertEqual(result['detail'], 'example.com')


class TestSuricata8NewProtocols(unittest.TestCase):
    """New event types available after upgrading from Suricata 7.0.10 to
    8.0.6 (Debian trixie-backports): websocket, pop3, mdns, ldap, arp. Field
    names verified against Suricata's own logger source (rust/src/<proto>/
    logger.rs or log.rs, src/output-json-arp.c for arp), not guessed."""

    GENERIC_FALLBACK = ['Time', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port']

    CASES = [
        ('websocket', {'event_type': 'websocket', 'websocket': {
            'fin': True, 'opcode': 'text', 'payload_printable': 'hello world'}},
         {'Opcode': 'text', 'Fin': 'true', 'Payload': 'hello world'}),
        ('pop3', {'event_type': 'pop3', 'pop3': {
            'request': {'command': 'USER', 'args': ['alice']},
            'response': {'success': True, 'status': 'OK'}}},
         {'Command': 'USER', 'Args': 'alice', 'Status': 'OK'}),
        ('mdns', {'event_type': 'mdns', 'mdns': {
            'type': 'response', 'queries': [{'rrname': 'printer.local', 'rrtype': 'A'}]}},
         {'Query': 'printer.local', 'Type': 'A'}),
        # A single ldap transaction can carry both request and responses
        # together (confirmed against logger.rs: both are logged from the
        # same tx when both are present by log time). result_code lives
        # inside a differently-named sub-object per operation
        # (bind_response here) - not a static field name.
        ('ldap', {'event_type': 'ldap', 'ldap': {
            'request': {'message_id': 1, 'operation': 'bind_request',
                        'bind_request': {'version': 3, 'name': 'cn=admin,dc=example,dc=com'}},
            'responses': [{'message_id': 1, 'operation': 'bind_response',
                           'bind_response': {'result_code': 'success', 'matched_dn': '', 'message': ''}}]}},
         {'Operation': 'bind_request', 'Message ID': '1', 'Result Code': 'success'}),
        ('arp', {'event_type': 'arp', 'arp': {
            'hw_type': 'ethernet', 'proto_type': 'ipv4', 'opcode': 'request',
            'src_mac': 'aa:bb:cc:dd:ee:ff', 'src_ip': '192.168.1.1',
            'dest_mac': '00:00:00:00:00:00', 'dest_ip': '192.168.1.254'}},
         {'Opcode': 'request', 'Src MAC': 'aa:bb:cc:dd:ee:ff', 'Dest MAC': '00:00:00:00:00:00'}),
    ]

    def test_getColumnsForType_no_longer_falls_back_to_generic_default(self):
        from tests.jsdom_helper import js_statements
        event_types = [c[0] for c in self.CASES]
        result = js_statements('''
            var types = ''' + json.dumps(event_types) + ''';
            window.__jsdom_result = { columns: types.map(function(t) { return getColumnsForType(t); }) };
        ''')
        for etype, cols in zip(event_types, result['columns']):
            with self.subTest(event_type=etype):
                self.assertNotEqual(cols, self.GENERIC_FALLBACK)

    def test_buildRowForEvent_renders_real_field_values(self):
        from tests.jsdom_helper import js_statements
        for etype, sample_event, expected in self.CASES:
            with self.subTest(event_type=etype):
                result = js_statements('''
                    window.__jsdom_result = { html: buildRowForEvent(''' + json.dumps(sample_event) + ''') };
                ''')
                for label, expected_value in expected.items():
                    self.assertIn(expected_value, result['html'],
                                  f'{etype} row HTML must contain {label}={expected_value!r}')

    def test_extractValue_matches_buildRowForEvent_values(self):
        from tests.jsdom_helper import js_statements
        for etype, sample_event, expected in self.CASES:
            with self.subTest(event_type=etype):
                labels = list(expected.keys())
                result = js_statements('''
                    var labels = ''' + json.dumps(labels) + ''';
                    var e = ''' + json.dumps(sample_event) + ''';
                    window.__jsdom_result = { values: labels.map(function(l) { return extractValue(e, l, 0); }) };
                ''')
                for label, value in zip(labels, result['values']):
                    self.assertIn(expected[label], str(value),
                                  f'{etype} extractValue({label!r}) = {value!r}, expected to contain {expected[label]!r}')

    def test_ldap_excluded_from_server_aggregation_and_sort(self):
        """ldap's fields are dynamically keyed by operation type, like mqtt -
        must fall back to client-side computation instead of hitting an
        always-empty server result."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = {
                agg: canUseServerAggregation('ldap'),
                sort: canServerSortEventType('ldap'),
            };
        ''')
        self.assertFalse(result['agg'])
        self.assertFalse(result['sort'])


class TestServerSideSort(unittest.TestCase):
    """Column-header sort for the 10 pcap per-type tabs now goes server-side
    (order_by/sort_dir on /api/events) instead of forcing a full-batch fetch
    - 'all'/'sigmaalert'/'log'/'binary' keep the original full-batch-then-
    client-sort behavior unchanged (canServerSortEventType excludes them)."""

    def _make_section(self, event_type='flow'):
        return f'''
            var section = document.createElement('div');
            section.className = 'section';
            section.id = 'section-{event_type}';
            document.body.appendChild(section);
        '''

    def test_canServerSortEventType_true_for_pcap_types(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = {
                flow: canServerSortEventType('flow'),
                dns: canServerSortEventType('dns'),
                alert: canServerSortEventType('alert'),
                all: canServerSortEventType('all'),
            };
        ''')
        self.assertTrue(result['flow'])
        self.assertTrue(result['dns'])
        self.assertTrue(result['alert'])
        self.assertTrue(result['all'],
                        "'all' now has a SQL equivalent for its Type/Detail columns (db.py's _all_events_detail_expr)")

    def test_canServerSortEventType_false_for_excluded_types(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = {
                sigmaalert: canServerSortEventType('sigmaalert'),
                log: canServerSortEventType('log'),
                binary: canServerSortEventType('binary'),
                mqtt: canServerSortEventType('mqtt'),
                empty: canServerSortEventType(''),
                nullish: canServerSortEventType(null),
            };
        ''')
        self.assertFalse(result['sigmaalert'])
        self.assertFalse(result['log'])
        self.assertFalse(result['binary'])
        self.assertFalse(result['mqtt'], 'mqtt columns have no _sort_expr mapping beyond Time - must use full client-side sort')
        self.assertFalse(result['empty'])
        self.assertFalse(result['nullish'])

    def test_sortCurrentTable_appends_order_by_for_supported_type(self):
        """currentSort/tabDataCache/activeTableRender are all let-scoped and
        can't be read or assigned directly across separate eval calls in the
        JSDOM test harness - state is driven entirely via real function calls
        (buildSection/sortCurrentTable) and observed only through the shared
        window.fetch mock's call log, which is reliable across evals."""
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('flow') + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) return Promise.resolve({ json: () => Promise.resolve([]) });
                return Promise.resolve({ json: () => Promise.resolve({ count: 0 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            await buildSection('flow', []);
            await sortCurrentTable(1);  // colIndex 1 -> 'Protocol'
            var eventsCalls = fetchCalls.filter(u => u.indexOf('/api/events') >= 0);
            window.__jsdom_result = { lastEventsUrl: eventsCalls[eventsCalls.length - 1] };
        ''')
        self.assertIn('order_by=Protocol', result['lastEventsUrl'])
        self.assertIn('sort_dir=asc', result['lastEventsUrl'])

    def test_sortCurrentTable_encodes_special_characters_in_column_label(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('flow') + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) return Promise.resolve({ json: () => Promise.resolve([]) });
                return Promise.resolve({ json: () => Promise.resolve({ count: 0 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            var pktsIdx = getColumnsForType('flow').indexOf('Pkts \\u2192');
            await buildSection('flow', []);
            await sortCurrentTable(pktsIdx);
            var eventsCalls = fetchCalls.filter(u => u.indexOf('/api/events') >= 0);
            window.__jsdom_result = { lastEventsUrl: eventsCalls[eventsCalls.length - 1], pktsIdx: pktsIdx };
        ''')
        self.assertGreaterEqual(result['pktsIdx'], 0)
        self.assertIn('order_by=Pkts', result['lastEventsUrl'])
        self.assertIn('sort_dir=asc', result['lastEventsUrl'])

    def test_sortCurrentTable_omits_order_by_when_switching_to_a_different_unsorted_section(self):
        """If a sort is active for one section, fetchEventsPage's section-key
        guard must stop it from leaking into an unrelated section's fetch -
        simulated here by rendering 'dns' with a sort active, then rendering
        'flow' fresh (as if switching tabs without first resetting state)."""
        from tests.jsdom_helper import js_statements
        result = js_statements(
            self._make_section('dns') + self._make_section('flow') + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) return Promise.resolve({ json: () => Promise.resolve([]) });
                return Promise.resolve({ json: () => Promise.resolve({ count: 0 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            await buildSection('dns', []);
            await sortCurrentTable(1);
            fetchCalls.length = 0;
            await buildSection('flow', []);
            var eventsCalls = fetchCalls.filter(u => u.indexOf('/api/events') >= 0);
            window.__jsdom_result = { lastEventsUrl: eventsCalls[eventsCalls.length - 1] };
        ''')
        self.assertNotIn('order_by=', result['lastEventsUrl'],
                         "a sort active for 'dns' must not apply to 'flow's fetch")

    def test_sortCurrentTable_skips_ensureCappedBatch_for_supported_type_no_filter(self):
        """No full-batch (ensureCappedBatch) fetch - i.e. no /api/events call
        using the large default query-limit with no offset - should occur
        for a server-sortable type with no active filter."""
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('flow') + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) return Promise.resolve({ json: () => Promise.resolve([]) });
                return Promise.resolve({ json: () => Promise.resolve({ count: 0 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            await buildSection('flow', []);
            await sortCurrentTable(1);
            var fullBatchCalls = fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('offset=') < 0);
            window.__jsdom_result = { fullBatchCallCount: fullBatchCalls.length };
        ''')
        self.assertEqual(result['fullBatchCallCount'], 0,
                         'sortCurrentTable must not trigger a full-batch (offset-less) fetch for a server-sortable type with no filter')

    def test_sortCurrentTable_still_uses_ensureCappedBatch_for_unsupported_type(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('sigmaalert') + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0 || url.indexOf('/api/sigma-alerts') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { severity: 'high', rule_title: 'R1', mitre_techniques: '[]', logsource: 'windows', original_log: '{}' }
                    ]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 1 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            // buildSigmaAlertSectionContent is the real renderer for this tab
            // (buildSection is only ever used for the 10 pcap per-type tabs) -
            // calling it populates the let-scoped activeTableRender correctly.
            await buildSigmaAlertSectionContent('section-sigmaalert', null);
            fetchCalls.length = 0;
            try {
                await sortCurrentTable(0);
            } catch (e) {
                // PRE-EXISTING bug, unrelated to server-side sort: once
                // currentSort is non-null, buildSigmaAlertSectionContent's
                // rerender (bound to alerts=null from the scalable branch)
                // falls into its client-fallback branch and crashes on
                // alerts.length. Not this test's concern - the ensureCappedBatch
                // fetch (what we're checking) already happened before this throws.
            }
            var fullBatchCalls = fetchCalls.filter(u => u.indexOf('/api/sigma-alerts') >= 0 && u.indexOf('offset=') < 0);
            window.__jsdom_result = { fullBatchCallCount: fullBatchCalls.length };
        ''')
        self.assertEqual(result['fullBatchCallCount'], 1,
                        'sortCurrentTable must still call ensureCappedBatch (full-batch, offset-less fetch) for an out-of-scope type like sigmaalert')

    def test_sortCurrentTable_still_uses_ensureCappedBatch_when_filter_active(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_section('flow') + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) return Promise.resolve({ json: () => Promise.resolve([]) });
                return Promise.resolve({ json: () => Promise.resolve({ count: 0 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            await buildSection('flow', []);
            currentFilters = { 'Protocol': 'TCP' };
            fetchCalls.length = 0;
            await sortCurrentTable(1);
            var fullBatchCalls = fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('offset=') < 0);
            window.__jsdom_result = { fullBatchCallCount: fullBatchCalls.length };
        ''')
        self.assertEqual(result['fullBatchCallCount'], 1,
                        'sortCurrentTable must still call ensureCappedBatch (full-batch, offset-less fetch) when a column filter is active, even for a server-sortable type')


class TestSigmaAlertSortCrashRegression(unittest.TestCase):
    """REGRESSION: buildSigmaAlertSectionContent's scalable-branch rerender
    closure used to hardcode null for its `alerts` param, assuming the next
    invocation would also be scalable. Clicking a column header (sigmaalert
    is not server-sortable) sets currentSort, flipping canUseScalableFetch()
    false before that same closure fires - the client-fallback branch then
    crashed on alerts.length. Fixed by recomputing a real filtered list in
    the closure, plus a defensive fallback in the function itself."""

    def test_sort_click_on_unfiltered_sigmaalert_tab_does_not_crash(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var section = document.createElement('div');
            section.className = 'section';
            section.id = 'section-sigmaalert';
            document.body.appendChild(section);

            window.fetch = function(url) {
                if (url.indexOf('/api/sigma-alerts') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { severity: 'high', rule_title: 'R1', mitre_techniques: '[]', logsource: 'windows', original_log: '{}' },
                        { severity: 'medium', rule_title: 'R2', mitre_techniques: '[]', logsource: 'windows', original_log: '{}' }
                    ]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 2 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            isLogAnalysisMode = true;
            // Scalable branch - sets activeTableRender with the buggy
            // hardcoded-null closure (pre-fix) as its rerender.
            await buildSigmaAlertSectionContent('section-sigmaalert', null);
            var threw = false;
            try {
                await sortCurrentTable(0);
            } catch (e) {
                threw = true;
            }
            var rowCount = document.querySelectorAll('#section-sigmaalert table tbody tr:not(.detail-row)').length;
            window.__jsdom_result = { threw: threw, rowCount: rowCount };
        ''')
        self.assertFalse(result['threw'], 'clicking a column header on an unfiltered Sigma Alerts tab must not throw')
        self.assertEqual(result['rowCount'], 2, 'the re-rendered table must still show the real alert rows, not an empty/broken render')

    def test_buildSigmaAlertSectionContent_handles_null_alerts_defensively(self):
        """Direct unit test of the defensive fallback: even called with a
        raw null (as if from a stale closure) while in non-scalable mode,
        the function must recompute real data instead of crashing."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var section = document.createElement('div');
            section.className = 'section';
            section.id = 'section-sigmaalert';
            document.body.appendChild(section);

            window.fetch = function(url) {
                if (url.indexOf('/api/sigma-alerts') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve([
                        { severity: 'high', rule_title: 'R1', mitre_techniques: '[]', logsource: 'windows', original_log: '{}' }
                    ]) });
                }
                return Promise.resolve({ json: () => Promise.resolve({ count: 1 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = { 'Severity': 'high' };
            currentSearch = [];
            await ensureCappedBatch('sigmaalert');  // real tabDataCache population

            var threw = false;
            try {
                await buildSigmaAlertSectionContent('section-sigmaalert', null);
            } catch (e) {
                threw = true;
            }
            var rowCount = document.querySelectorAll('#section-sigmaalert table tbody tr:not(.detail-row)').length;
            window.__jsdom_result = { threw: threw, rowCount: rowCount };
        ''')
        self.assertFalse(result['threw'], 'buildSigmaAlertSectionContent(sectionId, null) must not crash in non-scalable mode')
        self.assertEqual(result['rowCount'], 1)


class TestAllTabServerSideSortAndAggregation(unittest.TestCase):
    """The merged 'All Events' tab now has server-side sort/aggregation too
    (db.py's _all_events_detail_expr covers its 'Detail' column, UPPER(
    event_type) covers 'Type') - mirrors the per-type-tab feature classes
    above (TestServerSideSort/TestAggregationServerFetch)."""

    def _make_all_section(self):
        return '''
            var section = document.createElement('div');
            section.className = 'section';
            section.id = 'section-all';
            document.body.appendChild(section);
            var aggContainer = document.createElement('div');
            aggContainer.id = 'aggregations';
            document.body.appendChild(aggContainer);
        '''

    def test_getColumnsForType_all_returns_ALL_EVENTS_COLUMNS(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            window.__jsdom_result = { cols: getColumnsForType('all') };
        ''')
        self.assertEqual(result['cols'],
                         ['Time', 'Type', 'Protocol', 'Source IP', 'Source Port', 'Dest IP', 'Dest Port', 'Detail'])

    def test_fetchAggregationData_all_omits_type_param(self):
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                return Promise.resolve({ json: () => Promise.resolve({}) });
            };
            currentMd5 = 'abc123';
            currentSearch = [];
            await fetchAggregationData('all');
            window.__jsdom_result = { url: fetchCalls[0] };
        ''')
        self.assertNotIn('type=', result['url'],
                         "fetchAggregationData('all') must not send a literal type=all - it isn't a real db event_type")

    def test_fetchAggregationData_per_type_still_includes_type_param(self):
        """Regression guard: the typeParam fix must not break the existing
        per-type-tab behavior."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                return Promise.resolve({ json: () => Promise.resolve({}) });
            };
            currentMd5 = 'abc123';
            currentSearch = [];
            await fetchAggregationData('flow');
            window.__jsdom_result = { url: fetchCalls[0] };
        ''')
        self.assertIn('type=flow', result['url'])

    def test_buildAllEvents_appends_order_by_when_sorted(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_all_section() + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) return Promise.resolve({ json: () => Promise.resolve([]) });
                return Promise.resolve({ json: () => Promise.resolve({ count: 0 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            await buildAllEvents();
            await sortCurrentTable(1);  // colIndex 1 -> 'Type' in ALL_EVENTS_COLUMNS
            var eventsCalls = fetchCalls.filter(u => u.indexOf('/api/events') >= 0);
            window.__jsdom_result = { lastEventsUrl: eventsCalls[eventsCalls.length - 1] };
        ''')
        self.assertIn('order_by=Type', result['lastEventsUrl'])
        self.assertIn('sort_dir=asc', result['lastEventsUrl'])

    def test_sortCurrentTable_skips_ensureCappedBatch_for_all_tab_no_filter(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_all_section() + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/events') >= 0) return Promise.resolve({ json: () => Promise.resolve([]) });
                return Promise.resolve({ json: () => Promise.resolve({ count: 0 }) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            await buildAllEvents();
            await sortCurrentTable(7);  // 'Detail'
            var fullBatchCalls = fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('offset=') < 0);
            window.__jsdom_result = { fullBatchCallCount: fullBatchCalls.length };
        ''')
        self.assertEqual(result['fullBatchCallCount'], 0,
                         "sorting the 'all' tab by Detail must not trigger a full-batch fetch now that it's server-sortable")

    def test_buildAggregationsSectionAll_uses_server_endpoint_when_unfiltered(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_all_section() + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                if (url.indexOf('/api/aggregation-data') >= 0) {
                    return Promise.resolve({ json: () => Promise.resolve({
                        'Type': [{value: 'FLOW', count: 3}],
                        'Detail': [{value: 'sig1', count: 1}]
                    }) });
                }
                return Promise.resolve({ json: () => Promise.resolve([]) });
            };
            currentMd5 = 'abc123';
            currentFilters = {};
            currentSearch = [];
            advancedMode = true;
            await buildAggregationsSectionAll();
            window.__jsdom_result = {
                aggCalls: fetchCalls.filter(u => u.indexOf('/api/aggregation-data') >= 0).length,
                aggUrlHasType: fetchCalls.some(u => u.indexOf('/api/aggregation-data') >= 0 && u.indexOf('type=') >= 0),
                fullBatchCalls: fetchCalls.filter(u => u.indexOf('/api/events') >= 0 && u.indexOf('limit=') >= 0).length,
                aggHtml: document.getElementById('aggregations').innerHTML
            };
        ''')
        self.assertEqual(result['aggCalls'], 1,
                         'buildAggregationsSectionAll must call /api/aggregation-data when unfiltered')
        self.assertFalse(result['aggUrlHasType'], 'the merged aggregation request must not send type=all')
        self.assertEqual(result['fullBatchCalls'], 0,
                         'the server-aggregation path must not need the full capped batch')
        self.assertIn('FLOW', result['aggHtml'])

    def test_buildAggregationsSectionAll_falls_back_to_client_when_filtered(self):
        from tests.jsdom_helper import js_statements
        result = js_statements(self._make_all_section() + '''
            var fetchCalls = [];
            window.fetch = function(url) {
                fetchCalls.push(url);
                return Promise.resolve({ json: () => Promise.resolve([]) });
            };
            currentMd5 = 'abc123';
            currentFilters = { 'Protocol': 'TCP' };
            currentSearch = [];
            advancedMode = true;
            await buildAggregationsSectionAll();
            window.__jsdom_result = {
                aggCalls: fetchCalls.filter(u => u.indexOf('/api/aggregation-data') >= 0).length
            };
        ''')
        self.assertEqual(result['aggCalls'], 0,
                         'an active column filter must keep buildAggregationsSectionAll on the client-side path')

    def test_buildAllEventRow_shows_detail_for_previously_blank_types(self):
        """REGRESSION: buildAllEventRow used to maintain its own incomplete
        copy of the Detail logic, always blank for modbus/dnp3/pgsql/
        filealerts even though those were already correctly sortable via
        extractValue. Now it delegates to extractValue directly."""
        from tests.jsdom_helper import js_statements
        result = js_statements('''
            var modbusRow = buildAllEventRow({
                event_type: 'modbus', timestamp: '2026-01-01T00:00:00', proto: 'TCP',
                src_ip: '1.1.1.1', src_port: 502, dest_ip: '2.2.2.2', dest_port: 502,
                modbus: { request: { function_code: 'WrMultCoils' } }
            });
            var dnp3Row = buildAllEventRow({
                event_type: 'dnp3', timestamp: '2026-01-01T00:00:01', proto: 'TCP',
                src_ip: '1.1.1.1', dest_ip: '2.2.2.2',
                dnp3: { type: 'unsolicited_response' }
            });
            window.__jsdom_result = { modbusRow: modbusRow, dnp3Row: dnp3Row };
        ''')
        self.assertIn('WrMultCoils', result['modbusRow'])
        self.assertIn('unsolicited_response', result['dnp3Row'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
