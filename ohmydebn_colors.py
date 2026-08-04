#!/usr/bin/env python3
"""Derives a full SO-CRATES theme (CSS custom properties) from an OhMyDebn/
Aether color palette (colors.toml or, as a fallback, alacritty.toml), for
themes SO-CRATES has no hand-built CSS for. Pure functions, no I/O - the
caller handles reading/parsing the TOML file and never lets exceptions
from that escape to the request handler.
"""

import re

HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')

REQUIRED_KEYS = (
    'accent', 'foreground', 'background',
    'color1', 'color8', 'color9', 'color10', 'color11', 'color12', 'color13',
)


def _hex_to_rgb(hex_str):
    return tuple(int(hex_str[i:i + 2], 16) for i in (1, 3, 5))


def _rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(
        max(0, min(255, round(r))),
        max(0, min(255, round(g))),
        max(0, min(255, round(b))),
    )


def _mix(hex1, hex2, t):
    r1, g1, b1 = _hex_to_rgb(hex1)
    r2, g2, b2 = _hex_to_rgb(hex2)
    return _rgb_to_hex(
        r1 + (r2 - r1) * t,
        g1 + (g2 - g1) * t,
        b1 + (b2 - b1) * t,
    )


def _relative_luminance(hex_str):
    """Simple weighted-average luminance - a cheap 'which side is darker'
    signal (used to pick a lighten-vs-darken direction), not a legibility
    guarantee. See _wcag_luminance()/_contrast_ratio() for the latter."""
    r, g, b = _hex_to_rgb(hex_str)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def _srgb_channel_to_linear(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _wcag_luminance(hex_str):
    r, g, b = (_srgb_channel_to_linear(c) for c in _hex_to_rgb(hex_str))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast_ratio(hex1, hex2):
    """WCAG 2.x contrast ratio (1-21). Unlike _relative_luminance(), this
    is gamma-corrected and is what real legibility thresholds (e.g. the
    3:1/4.5:1 AA cutoffs) are actually defined against."""
    l1, l2 = _wcag_luminance(hex1), _wcag_luminance(hex2)
    lighter, darker = (l1, l2) if l1 >= l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


# WCAG AA's "large text"/UI-component threshold - the compact uppercase
# labels/table headers/tag-and-badge text these CSS variables style are
# closer to that category than to full-paragraph body text (4.5:1).
MIN_TEXT_CONTRAST_RATIO = 3.0


def _ensure_min_contrast(candidate, background, foreground, min_ratio=MIN_TEXT_CONTRAST_RATIO):
    """Nudges `candidate` toward `foreground` until it reaches at least
    `min_ratio` WCAG contrast against `background`, so it stays legible as
    text. Confirmed necessary on real installed OhMyDebn themes (e.g.
    amberbyte, solarized, red-monarch) where bright-black (color8) or the
    accent/tag colors sit almost exactly on top of a near-monochrome
    background, making anything styled with --text-muted/--tag-gray-text
    (table headers, stat-card labels), --accent, or the --tag-*-text/
    --badge-*-text colors functionally invisible - a first attempt at
    this using a simple linear luminance-gap target measurably
    under-corrected (~1.6:1 real contrast, still far below legible) since
    WCAG contrast isn't linear in the underlying RGB values.
    Binary-searches the mix fraction instead - contrast ratio only
    increases as candidate's luminance moves further from background's,
    which holds as long as foreground itself has reasonable contrast
    against background (true almost by definition, since foreground is
    the theme's primary text color)."""
    if _contrast_ratio(candidate, background) >= min_ratio:
        return candidate
    if _contrast_ratio(foreground, background) < min_ratio:
        # Even fully switching to foreground can't reach the target (a
        # low-contrast theme overall) - that's the best available, and
        # still strictly better than the original candidate.
        return foreground
    lo, hi = 0.0, 1.0
    best = foreground
    for _ in range(24):
        mid = (lo + hi) / 2
        mixed = _mix(candidate, foreground, mid)
        if _contrast_ratio(mixed, background) >= min_ratio:
            best = mixed
            hi = mid
        else:
            lo = mid
    return best


def derive_theme_colors(palette):
    """Takes a dict parsed from colors.toml and returns a dict of CSS
    custom-property names (including the leading '--') to hex values,
    or None if the palette is missing a required key or has an invalid
    (non '#rrggbb') value for one - fails closed rather than emitting a
    partially-populated theme."""
    for key in REQUIRED_KEYS:
        value = palette.get(key)
        if not isinstance(value, str) or not HEX_RE.match(value):
            return None

    accent = palette['accent']
    foreground = palette['foreground']
    background = palette['background']
    color1 = palette['color1']
    color8 = palette['color8']
    color9 = palette['color9']
    color10 = palette['color10']
    color11 = palette['color11']
    color12 = palette['color12']
    color13 = palette['color13']

    bg_is_darker = _relative_luminance(background) <= _relative_luminance(foreground)
    contrast_extreme = '#ffffff' if bg_is_darker else '#000000'

    # Every color rendered as text directly against --bg-primary (not just
    # --text-muted) gets the same contrast-safety nudge - confirmed a real
    # installed theme (red-monarch) has a low-contrast accent/tag palette
    # overall, not just a low-contrast muted color.
    accent = _ensure_min_contrast(accent, background, foreground)
    muted = _ensure_min_contrast(color8, background, foreground)
    tag_red = _ensure_min_contrast(color9, background, foreground)
    tag_green = _ensure_min_contrast(color10, background, foreground)
    tag_warning = _ensure_min_contrast(color11, background, foreground)
    tag_blue = _ensure_min_contrast(color12, background, foreground)
    tag_purple = _ensure_min_contrast(color13, background, foreground)
    tag_orange = _ensure_min_contrast(_mix(color9, color11, 0.5), background, foreground)

    return {
        '--accent': accent,
        '--help-icon-color': accent,
        '--accent-hover': _mix(accent, contrast_extreme, 0.18),
        '--bg-primary': background,
        '--bg-secondary': _mix(background, foreground, 0.05),
        '--bg-tertiary': _mix(background, foreground, 0.09),
        '--bg-hover': _mix(background, foreground, 0.14),
        '--bg-hover-light': _mix(background, foreground, 0.22),
        '--border-color': _mix(background, foreground, 0.14),
        '--bg-drop-active': _mix(background, foreground, 0.09),
        '--badge-bg-neutral': _mix(background, foreground, 0.09),
        '--text-primary': foreground,
        '--text-bright': _mix(foreground, contrast_extreme, 0.2),
        '--text-muted': muted,
        '--tag-gray-text': muted,
        '--tag-red-text': tag_red,
        '--badge-danger-text': tag_red,
        '--tag-green-text': tag_green,
        '--badge-success-text': tag_green,
        '--badge-warning-text': tag_warning,
        '--tag-blue-text': tag_blue,
        '--tag-purple-text': tag_purple,
        '--tag-orange-text': tag_orange,
        '--danger-bg': _mix(background, color1, 0.15),
        '--modal-backdrop': 'rgba(0,0,0,0.85)' if bg_is_darker else 'rgba(0,0,0,0.5)',
    }


# Maps a semantic field name (as found in this variant of colors.toml) to
# the color0-15 slot name derive_theme_colors() expects.
_NAMED_PALETTE_SLOTS = {
    'red': 'color1',
    'muted': 'color8',
    'bright_red': 'color9',
    'bright_green': 'color10',
    'bright_yellow': 'color11',
    'bright_blue': 'color12',
    'bright_magenta': 'color13',
}


def derive_theme_colors_from_named_palette(palette):
    """Some OhMyDebn colors.toml files use semantic color names (red,
    green, blue, ..., bright_red, bright_green, ..., muted) instead of the
    numbered color0-15 ANSI-slot scheme derive_theme_colors() expects
    directly - confirmed on a real installed theme ('midnight'), whose
    'muted' field is a near-perfect semantic match for color8's
    text-muted/tag-gray-text role. Remaps into the same flat shape and
    delegates to derive_theme_colors(), so REQUIRED_KEYS stays the single
    source of truth for what's actually needed - this is not a full
    schema, just an alternate set of names for a subset of the same
    slots."""
    flat = {}
    for key in ('accent', 'foreground', 'background'):
        if key in palette:
            flat[key] = palette[key]
    for name, slot in _NAMED_PALETTE_SLOTS.items():
        if name in palette:
            flat[slot] = palette[name]
    return derive_theme_colors(flat)


# ANSI slot order color0-7/color8-15 map to, within alacritty's
# [colors.normal]/[colors.bright] tables.
_ANSI_SLOT_NAMES = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')


def _normalize_alacritty_hex(value):
    """Alacritty accepts both '#rrggbb' and '0xrrggbb' - confirmed a real
    installed theme (solarizedosaka) uses the latter exclusively. Convert
    to '#rrggbb' so derive_theme_colors()'s HEX_RE validation still applies
    uniformly; anything else is returned as-is and will fail that check."""
    if isinstance(value, str) and (value.startswith('0x') or value.startswith('0X')):
        return '#' + value[2:]
    return value


def derive_theme_colors_from_alacritty(alacritty_dict):
    """Takes a dict parsed from an Alacritty color-scheme TOML (standard
    [colors.primary]/[colors.normal]/[colors.bright] tables - no 'accent'
    field exists in this format) and returns the same CSS custom-property
    dict derive_theme_colors() produces, or None if it can't be normalized
    into something derive_theme_colors() accepts.

    Builds the flat palette optimistically from whatever keys are present
    rather than requiring a fixed set here - derive_theme_colors()'s own
    REQUIRED_KEYS check remains the single source of truth for what's
    actually needed, so the two can't silently drift out of sync. Each
    bright.* slot individually falls back to the matching normal.* value
    when absent (mirrors real terminal behavior - some real-world themes,
    e.g. one that only sets bright.black, rely on exactly this)."""
    colors = alacritty_dict.get('colors')
    if not isinstance(colors, dict):
        return None

    primary = colors.get('primary') or {}
    normal = colors.get('normal') or {}
    bright = colors.get('bright') or {}

    palette = {}
    if 'background' in primary:
        palette['background'] = _normalize_alacritty_hex(primary['background'])
    if 'foreground' in primary:
        palette['foreground'] = _normalize_alacritty_hex(primary['foreground'])
    if 'blue' in normal:
        palette['accent'] = _normalize_alacritty_hex(normal['blue'])

    for i, name in enumerate(_ANSI_SLOT_NAMES):
        if name in normal:
            palette[f'color{i}'] = _normalize_alacritty_hex(normal[name])
        bright_value = bright.get(name, normal.get(name))
        if bright_value is not None:
            palette[f'color{i + 8}'] = _normalize_alacritty_hex(bright_value)

    return derive_theme_colors(palette)
