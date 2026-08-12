#!/usr/bin/env python3
"""Tests for exif_analyzer.py."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import exif_analyzer


class TestDetermineCategory(unittest.TestCase):
    def test_jpeg_is_image_not_pe(self):
        """REGRESSION: 'jpeg'.lower() contains the substring 'pe' (j-PE-g),
        which used to make the PE-executable heuristic match before the
        image mime-type check ever ran - every JPEG lost all of its image
        EXIF fields (GPS/Make/Model/dimensions) as a result."""
        self.assertEqual(exif_analyzer._determine_category('image/jpeg', 'JPEG'), 'image')

    def test_other_image_types_are_image(self):
        for file_type in ('PNG', 'GIF', 'BMP', 'TIFF', 'WEBP'):
            with self.subTest(file_type=file_type):
                self.assertEqual(exif_analyzer._determine_category(f'image/{file_type.lower()}', file_type), 'image')

    def test_pe_executable(self):
        self.assertEqual(exif_analyzer._determine_category('application/x-dosexec', 'Win32 EXE'), 'pe')
        self.assertEqual(
            exif_analyzer._determine_category('application/vnd.microsoft.portable-executable', 'Win64 EXE'), 'pe')

    def test_pdf(self):
        self.assertEqual(exif_analyzer._determine_category('application/pdf', 'PDF document'), 'pdf')

    def test_office_document(self):
        self.assertEqual(exif_analyzer._determine_category('application/msword', 'Composite Document File'), 'office')
        self.assertEqual(
            exif_analyzer._determine_category(
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Microsoft Word 2007+'),
            'office')

    def test_unrecognized_mime_returns_none(self):
        self.assertIsNone(exif_analyzer._determine_category('application/octet-stream', 'data'))

    def test_no_mime_type_returns_none(self):
        self.assertIsNone(exif_analyzer._determine_category('', 'JPEG'))


if __name__ == '__main__':
    unittest.main()
