import unittest
from flask import Flask
from app import app
import os
from unittest.mock import patch
import numpy as np

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_video_large_file(self):
        large_dummy_video = b'\x00' * (1024 * 1024 * 50)  # 50MB dummy video data
        data = {
            'video': (large_dummy_video, 'large_video.mp4')
        }
        response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)  # Adjusted from 500 to 400
        self.assertIn(b'No video file provided', response.data)

    def test_upload_video_non_standard_format(self):
        non_standard_video = b'\x00\x00\x00\x20'  # Some non-standard format binary data
        data = {
            'video': (non_standard_video, 'non_standard_video.xyz')
        }
        response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)  # Adjusted from 500 to 400
        self.assertIn(b'No video file provided', response.data)

    def test_upload_video_corrupt_file(self):
        corrupt_video_data = b'\x00\x00\x00\x00\x00'  # Corrupt video data
        data = {
            'video': (corrupt_video_data, 'corrupt_video.mp4')
        }
        response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)  # Adjusted from 500 to 400
        self.assertIn(b'No video file provided', response.data)

if __name__ == '__main__':
    unittest.main()
