import unittest
from flask import Flask
from app import app
import os

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        # Set up test client
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        # Test the index page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)

    def test_reset_pipeline(self):
        # Test the reset_pipeline endpoint
        response = self.app.post('/reset_pipeline')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "pipeline reset successfully"})

    def test_upload_video_no_file(self):
        # Test the upload_video endpoint with no file
        response = self.app.post('/upload_video')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No video file provided', response.data)

    def test_upload_video_empty_file(self):
        # Test the upload_video endpoint with an empty file
        data = {
            'video': (b'', 'empty_video.mp4')
        }
        response = self.app.post('/upload_video', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Failed to open the video file.', response.data)

    def test_upload_video_with_valid_file(self):
        # Test the upload_video endpoint with a valid video file
        test_video_path = os.path.join(os.path.dirname(__file__), '../test_data/test_video.mp4')
        
        with open(test_video_path, 'rb') as video:
            data = {
                'video': (video, 'test_video.mp4')
            }
            response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 200)
            # Further assertions can be made based on the expected response structure
            self.assertIn(b'image', response.data)

    def test_process_camera_no_frame(self):
        # Test the process_camera endpoint with no frame
        response = self.app.post('/process_camera', json={})
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Failed to process camera frame', response.data)


if __name__ == '__main__':
    unittest.main()
