#!/usr/bin/env python3
"""Tests for ohmydebn_colors.py."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import ohmydebn_colors


VALID_PALETTE = {
    'accent': '#5c7a9d',
    'cursor': '#FCE7A1',
    'foreground': '#FCE7A1',
    'background': '#000617',
    'selection_foreground': '#000617',
    'selection_background': '#FCE7A1',
    'color0': '#000617',
    'color1': '#eb3836',
    'color2': '#A5B699',
    'color3': '#E0DCAB',
    'color4': '#5c7a9d',
    'color5': '#96738b',
    'color6': '#709DA0',
    'color7': '#FCE7A1',
    'color8': '#595d62',
    'color9': '#ff5851',
    'color10': '#c3d7b1',
    'color11': '#f0eb90',
    'color12': '#7d9dcb',
    'color13': '#be95b4',
    'color14': '#91c4c7',
    'color15': '#ffeb72',
}


class TestDeriveThemeColors(unittest.TestCase):
    def test_valid_palette_returns_full_dict(self):
        result = ohmydebn_colors.derive_theme_colors(VALID_PALETTE)
        self.assertIsNotNone(result)
        self.assertEqual(result['--accent'], '#5c7a9d')
        self.assertEqual(result['--help-icon-color'], '#5c7a9d')
        self.assertEqual(result['--bg-primary'], '#000617')
        self.assertEqual(result['--text-primary'], '#FCE7A1')
        self.assertEqual(result['--text-muted'], '#595d62')
        self.assertEqual(result['--tag-gray-text'], '#595d62')
        self.assertEqual(result['--tag-red-text'], '#ff5851')
        self.assertEqual(result['--badge-danger-text'], '#ff5851')
        self.assertEqual(result['--tag-green-text'], '#c3d7b1')
        self.assertEqual(result['--tag-blue-text'], '#7d9dcb')
        self.assertEqual(result['--tag-purple-text'], '#be95b4')
        self.assertEqual(result['--badge-warning-text'], '#f0eb90')

    def test_all_keys_are_valid_hex_or_rgba(self):
        result = ohmydebn_colors.derive_theme_colors(VALID_PALETTE)
        for name, value in result.items():
            if name == '--modal-backdrop':
                self.assertTrue(value.startswith('rgba('), name)
            else:
                self.assertRegex(value, r'^#[0-9a-fA-F]{6}$', name)

    def test_dark_background_uses_lighter_derived_shades(self):
        # background (#000617) is much darker than foreground (#FCE7A1),
        # so bg-secondary/tertiary/hover should progressively lighten and
        # modal-backdrop should pick the "dark theme" alpha.
        result = ohmydebn_colors.derive_theme_colors(VALID_PALETTE)
        bg = ohmydebn_colors._hex_to_rgb(result['--bg-primary'])
        secondary = ohmydebn_colors._hex_to_rgb(result['--bg-secondary'])
        tertiary = ohmydebn_colors._hex_to_rgb(result['--bg-tertiary'])
        hover = ohmydebn_colors._hex_to_rgb(result['--bg-hover'])
        self.assertLess(sum(bg), sum(secondary))
        self.assertLess(sum(secondary), sum(tertiary))
        self.assertLess(sum(tertiary), sum(hover))
        self.assertEqual(result['--modal-backdrop'], 'rgba(0,0,0,0.85)')

    def test_light_background_uses_darker_derived_shades(self):
        palette = dict(VALID_PALETTE, background='#f5f5f0', foreground='#101010')
        result = ohmydebn_colors.derive_theme_colors(palette)
        bg = ohmydebn_colors._hex_to_rgb(result['--bg-primary'])
        secondary = ohmydebn_colors._hex_to_rgb(result['--bg-secondary'])
        self.assertGreater(sum(bg), sum(secondary))
        self.assertEqual(result['--modal-backdrop'], 'rgba(0,0,0,0.5)')

    def test_missing_required_key_returns_none(self):
        palette = dict(VALID_PALETTE)
        del palette['color9']
        self.assertIsNone(ohmydebn_colors.derive_theme_colors(palette))

    def test_invalid_hex_value_returns_none(self):
        palette = dict(VALID_PALETTE, accent='not-a-color')
        self.assertIsNone(ohmydebn_colors.derive_theme_colors(palette))

    def test_three_digit_hex_rejected(self):
        palette = dict(VALID_PALETTE, background='#000')
        self.assertIsNone(ohmydebn_colors.derive_theme_colors(palette))

    def test_empty_palette_returns_none(self):
        self.assertIsNone(ohmydebn_colors.derive_theme_colors({}))

    def test_close_luminance_background_and_foreground_still_returns_dict(self):
        # Low-contrast source palette - not a crash case, just narrow deltas.
        palette = dict(VALID_PALETTE, background='#808080', foreground='#828282')
        result = ohmydebn_colors.derive_theme_colors(palette)
        self.assertIsNotNone(result)
        self.assertRegex(result['--bg-secondary'], r'^#[0-9a-fA-F]{6}$')


ALACRITTY_DICT = {
    'colors': {
        'primary': {'background': '#282a36', 'foreground': '#f8f8f2'},
        'normal': {
            'black': '#21222c', 'red': '#ff5555', 'green': '#50fa7b', 'yellow': '#f1fa8c',
            'blue': '#bd93f9', 'magenta': '#ff79c6', 'cyan': '#8be9fd', 'white': '#f8f8f2',
        },
        'bright': {
            'black': '#6272a4', 'red': '#ff6e6e', 'green': '#69ff94', 'yellow': '#ffffa5',
            'blue': '#d6acff', 'magenta': '#ff92df', 'cyan': '#a4ffff', 'white': '#ffffff',
        },
    },
}


NAMED_PALETTE = {
    'mode': 'dark',
    'accent': '#407e70',
    'selection': '#333333',
    'muted': '#1e1e1e',
    'background': '#000000',
    'dark_background': '#0d0d0d',
    'darker_background': '#000000',
    'lighter_background': '#121212',
    'foreground': '#EFEFEF',
    'dark_foreground': '#555555',
    'light_foreground': '#8a8a8d',
    'bright_foreground': '#ffffff',
    'red': '#D35F5F',
    'yellow': '#FFC107',
    'orange': '#F59E0B',
    'green': '#8A9A7B',
    'cyan': '#88AABB',
    'blue': '#8A9FBE',
    'magenta': '#C1A1C1',
    'brown': '#8a8a8d',
    'bright_red': '#B91C1C',
    'bright_yellow': '#F59E0B',
    'bright_green': '#A5B799',
    'bright_cyan': '#A2C4D3',
    'bright_blue': '#A4BBDD',
    'bright_magenta': '#D9B9D9',
}


class TestDeriveThemeColorsFromNamedPalette(unittest.TestCase):
    def test_real_midnight_theme_derives_successfully(self):
        """REGRESSION: OhMyDebn's own 'midnight' theme uses semantic color
        names (red/blue/bright_red/muted/...) instead of the numbered
        color0-15 scheme derive_theme_colors() expects directly - this
        used to fall through both the native and alacritty paths and
        disable sync entirely."""
        result = ohmydebn_colors.derive_theme_colors_from_named_palette(NAMED_PALETTE)
        self.assertIsNotNone(result)
        self.assertEqual(result['--accent'], '#407e70')
        self.assertEqual(result['--bg-primary'], '#000000')
        self.assertEqual(result['--text-primary'], '#EFEFEF')
        # 'muted' (#1e1e1e) sits too close to background (#000000) to read
        # as text on its own - must be nudged toward foreground, not used
        # verbatim (see TestEnsureMinContrast).
        ratio = ohmydebn_colors._contrast_ratio(result['--text-muted'], result['--bg-primary'])
        self.assertGreaterEqual(ratio, ohmydebn_colors.MIN_TEXT_CONTRAST_RATIO - 0.05)
        self.assertEqual(result['--tag-red-text'], '#B91C1C', 'bright_red must map to color9')

    def test_missing_muted_returns_none(self):
        palette = {k: v for k, v in NAMED_PALETTE.items() if k != 'muted'}
        self.assertIsNone(ohmydebn_colors.derive_theme_colors_from_named_palette(palette),
                          'color8 has no source without muted, so this must fail closed')

    def test_ansi_slot_palette_is_not_matched_by_named_normalizer(self):
        """The ANSI-slot scheme (color0-15) and this semantic-name scheme
        are mutually exclusive in practice - a palette using 'color1' etc.
        has no 'red'/'bright_red' keys, so this normalizer correctly finds
        nothing to map and returns None (the caller tries derive_theme_colors()
        directly for that scheme instead)."""
        self.assertIsNone(ohmydebn_colors.derive_theme_colors_from_named_palette(VALID_PALETTE))


class TestDeriveThemeColorsFromAlacritty(unittest.TestCase):
    def test_valid_alacritty_dict_returns_full_dict(self):
        result = ohmydebn_colors.derive_theme_colors_from_alacritty(ALACRITTY_DICT)
        self.assertIsNotNone(result)
        self.assertEqual(result['--bg-primary'], '#282a36')
        self.assertEqual(result['--text-primary'], '#f8f8f2')
        self.assertEqual(result['--tag-red-text'], '#ff6e6e')  # bright.red
        self.assertEqual(result['--tag-green-text'], '#69ff94')  # bright.green

    def test_accent_derived_from_normal_blue(self):
        result = ohmydebn_colors.derive_theme_colors_from_alacritty(ALACRITTY_DICT)
        self.assertEqual(result['--accent'], '#bd93f9')

    def test_missing_bright_colors_fall_back_to_normal_per_key(self):
        """REGRESSION: a real installed theme (green-garden) only sets
        bright.black and leaves every other bright.* unset - must fall
        back to the matching normal.* color per-key, not fail closed."""
        palette = {
            'colors': {
                'primary': {'background': '#1d271f', 'foreground': '#e4d8b4'},
                'normal': {
                    'black': '#293427', 'red': '#c45b5b', 'green': '#7e9c58', 'yellow': '#d29c5a',
                    'blue': '#65a0d9', 'magenta': '#d6885e', 'cyan': '#89d9d0', 'white': '#e4d8b4',
                },
                'bright': {'black': '#505b51'},
            },
        }
        result = ohmydebn_colors.derive_theme_colors_from_alacritty(palette)
        self.assertIsNotNone(result)
        # --tag-gray-text/--text-muted go through the contrast-safety nudge
        # (see TestEnsureMinContrast), so only check it meets that bar here -
        # the point of *this* test is the bright->normal per-key fallback,
        # which --tag-red-text/--tag-green-text (not nudged) demonstrate directly.
        ratio = ohmydebn_colors._contrast_ratio(result['--bg-primary'], result['--tag-gray-text'])
        self.assertGreaterEqual(ratio, ohmydebn_colors.MIN_TEXT_CONTRAST_RATIO - 0.05)
        self.assertEqual(result['--tag-red-text'], '#c45b5b', 'missing bright.red must fall back to normal.red')
        self.assertEqual(result['--tag-green-text'], '#7e9c58', 'missing bright.green must fall back to normal.green')

    def test_0x_prefixed_hex_values_are_normalized(self):
        """REGRESSION: a real installed theme (solarizedosaka) uses
        '0xrrggbb' instead of '#rrggbb' throughout - Alacritty accepts
        both, so we must normalize before hex validation rejects it."""
        palette = {
            'colors': {
                'primary': {'background': '0x001c2b', 'foreground': '0x6c7c81'},
                'normal': {
                    'black': '0x072a39', 'red': '0xd8322f', 'green': '0x809900', 'yellow': '0xb38800',
                    'blue': '0x268bd2', 'magenta': '0xd03682', 'cyan': '0x2aa198', 'white': '0xe9e2d0',
                },
                'bright': {
                    'black': '0x5f6f74', 'red': '0xd8322f', 'green': '0x809900', 'yellow': '0xb38800',
                    'blue': '0x268bd2', 'magenta': '0xd03682', 'cyan': '0x2aa198', 'white': '0xfcf6e3',
                },
            },
        }
        result = ohmydebn_colors.derive_theme_colors_from_alacritty(palette)
        self.assertIsNotNone(result)
        self.assertEqual(result['--bg-primary'], '#001c2b')
        self.assertEqual(result['--accent'], '#268bd2')

    def test_missing_required_field_returns_none(self):
        palette = {
            'colors': {
                'primary': {'foreground': '#f8f8f2'},  # no background
                'normal': ALACRITTY_DICT['colors']['normal'],
                'bright': ALACRITTY_DICT['colors']['bright'],
            },
        }
        self.assertIsNone(ohmydebn_colors.derive_theme_colors_from_alacritty(palette))

    def test_missing_colors_table_returns_none(self):
        self.assertIsNone(ohmydebn_colors.derive_theme_colors_from_alacritty({}))

    def test_missing_accent_source_returns_none(self):
        palette = {
            'colors': {
                'primary': {'background': '#282a36', 'foreground': '#f8f8f2'},
                'normal': {k: v for k, v in ALACRITTY_DICT['colors']['normal'].items() if k != 'blue'},
                'bright': ALACRITTY_DICT['colors']['bright'],
            },
        }
        self.assertIsNone(ohmydebn_colors.derive_theme_colors_from_alacritty(palette),
                          'no normal.blue means no accent can be derived, so this must fail closed')


class TestColorHelpers(unittest.TestCase):
    def test_hex_to_rgb_and_back(self):
        self.assertEqual(ohmydebn_colors._hex_to_rgb('#5c7a9d'), (0x5c, 0x7a, 0x9d))
        self.assertEqual(ohmydebn_colors._rgb_to_hex(0x5c, 0x7a, 0x9d), '#5c7a9d')

    def test_mix_endpoints(self):
        self.assertEqual(ohmydebn_colors._mix('#000000', '#ffffff', 0), '#000000')
        self.assertEqual(ohmydebn_colors._mix('#000000', '#ffffff', 1), '#ffffff')
        self.assertEqual(ohmydebn_colors._mix('#000000', '#ffffff', 0.5), '#808080')


class TestEnsureMinContrast(unittest.TestCase):
    def test_already_sufficient_contrast_returned_unchanged(self):
        result = ohmydebn_colors._ensure_min_contrast('#595d62', '#000617', '#FCE7A1')
        self.assertEqual(result, '#595d62')

    def test_low_contrast_candidate_is_nudged_toward_foreground(self):
        """REGRESSION: a real installed theme (amberbyte) derives
        text-muted from a near-monochrome palette where bright-black sits
        almost exactly on top of the background (#1b1112 vs #2B1818,
        ~1.1:1 real contrast) - must be nudged to an actually legible
        contrast ratio, not just a slightly-less-bad one (a first
        luminance-gap-based attempt at this only reached ~1.6:1, still far
        below legible)."""
        background = '#1b1112'
        candidate = '#2B1818'
        foreground = '#F2E8E8'
        result = ohmydebn_colors._ensure_min_contrast(candidate, background, foreground)
        self.assertNotEqual(result, candidate)
        ratio = ohmydebn_colors._contrast_ratio(result, background)
        self.assertGreaterEqual(ratio, ohmydebn_colors.MIN_TEXT_CONTRAST_RATIO - 0.05)

    def test_zero_contrast_candidate_is_nudged(self):
        """REGRESSION: a real installed theme (solarized) has zero
        luminance difference between candidate and background at all."""
        result = ohmydebn_colors._ensure_min_contrast('#123456', '#123456', '#ffffff')
        self.assertNotEqual(result, '#123456')
        ratio = ohmydebn_colors._contrast_ratio(result, '#123456')
        self.assertGreaterEqual(ratio, ohmydebn_colors.MIN_TEXT_CONTRAST_RATIO - 0.05)

    def test_foreground_same_luminance_as_candidate_returns_unchanged(self):
        """Nothing to nudge toward if foreground can't move the luminance
        anywhere - must not divide by zero or raise."""
        result = ohmydebn_colors._ensure_min_contrast('#808080', '#808080', '#808080')
        self.assertEqual(result, '#808080')


class TestContrastAppliesToAccentAndTagColors(unittest.TestCase):
    def test_real_red_monarch_theme_accent_and_tags_meet_contrast(self):
        """REGRESSION: a real installed theme (red-monarch) has no
        [colors.bright] table at all, and every [colors.normal] color
        except black/white is the identical saturated red (#BF1111) -
        against its near-black background (#10090B) that only reaches
        ~1.54:1 real WCAG contrast (a fully-saturated red's WCAG luminance
        is much lower than its apparent brightness suggests, a well-known
        accessibility gotcha). Before --accent/--tag-*-text got the same
        contrast-safety nudge as --text-muted, this theme's accent color
        and every tag color were all near-invisible against its background,
        not just its muted/gray text."""
        palette = {
            'colors': {
                'primary': {'background': '#10090B', 'foreground': '#EDEDED'},
                'normal': {
                    'black': '#120B0D', 'red': '#BF1111', 'green': '#BF1111', 'yellow': '#BF1111',
                    'blue': '#BF1111', 'magenta': '#BF1111', 'cyan': '#BF1111', 'white': '#EDEDED',
                },
                'bright': {},
            },
        }
        result = ohmydebn_colors.derive_theme_colors_from_alacritty(palette)
        self.assertIsNotNone(result)
        for var in ('--accent', '--tag-red-text', '--tag-green-text', '--tag-blue-text',
                    '--tag-purple-text', '--tag-orange-text'):
            ratio = ohmydebn_colors._contrast_ratio(result[var], result['--bg-primary'])
            self.assertGreaterEqual(ratio, ohmydebn_colors.MIN_TEXT_CONTRAST_RATIO - 0.05, var)


if __name__ == '__main__':
    unittest.main()
