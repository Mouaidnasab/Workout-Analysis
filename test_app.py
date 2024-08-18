import unittest
import json
from app import app

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        # Test the index page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Index Page', response.data)  # Ensure the index page contains specific text

    def test_reset_pipeline(self):
        # Test the reset_pipeline endpoint
        response = self.app.post('/reset_pipeline')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'pipeline reset successfully')

    def test_upload_video_no_file(self):
        # Test upload video endpoint without a file
        response = self.app.post('/upload_video')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'No video file provided')

    def test_upload_video_empty_file(self):
        # Test upload video endpoint with an empty file
        response = self.app.post('/upload_video', data={'video': (None, '')})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'No selected file')

    def test_process_camera_no_frame(self):
        # Test process camera endpoint with no frame
        response = self.app.post('/process_camera', json={})
        self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()
