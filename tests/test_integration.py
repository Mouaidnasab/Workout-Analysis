import unittest
from flask import Flask
from app import app
import os

class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_upload_video_large_file(self):
        # Test uploading a large video file
        large_dummy_video = b'\x00' * (1024 * 1024 * 50)  # 50MB dummy video data
        data = {
            'video': (large_dummy_video, 'large_video.mp4')
        }
        response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')

        # Ensure the application handles large file uploads correctly
        self.assertEqual(response.status_code, 400)  # Expected failure due to invalid video data
        self.assertIn(b'No video file provided', response.data)

    def test_upload_video_non_standard_format(self):
        # Test uploading a video with a non-standard file format
        non_standard_video = b'\x00\x00\x00\x20'  # Some non-standard format binary data
        data = {
            'video': (non_standard_video, 'non_standard_video.xyz')
        }
        response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')

        # Check how the system responds to a non-standard file format
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No video file provided', response.data)

    def test_upload_video_corrupt_file(self):
        # Test uploading a corrupted video file
        corrupt_video_data = b'\x00\x00\x00\x00\x00'  # Corrupt video data
        data = {
            'video': (corrupt_video_data, 'corrupt_video.mp4')
        }
        response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')

        # Ensure the system identifies and rejects the corrupted video file
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No video file provided', response.data)

    def test_upload_valid_video_file(self):
        # Test uploading a valid video file and processing it
        video_path = os.path.join('test_data', 'test_video.mp4')

        with open(video_path, 'rb') as video_file:
            data = {'video': (video_file, 'test_video.mp4')}
            response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')

        # Check the response from the valid video file upload
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()

        # Validate that the response contains processed data
        self.assertTrue(len(response_data) > 0)
        for frame_data in response_data:
            self.assertIn('image', frame_data)
            self.assertIn('label', frame_data)
            self.assertIn('counter', frame_data)
            self.assertIn('stage', frame_data)
            self.assertIn('angles_status', frame_data)
            self.assertIn('detailed_feedback', frame_data)

if __name__ == '__main__':
    unittest.main()
