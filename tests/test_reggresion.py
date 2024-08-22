import unittest
from app import app
import os
import cv2
import numpy as np
import base64

class RegressionTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_homepage_regression(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)  # Assuming the index.html starts with a doctype

    def test_upload_video_regression(self):
        video_path = os.path.join('test_data', 'test_video.mp4')

        with open(video_path, 'rb') as video_file:
            data = {'video': (video_file, 'test_video.mp4')}
            response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')

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

    def test_reset_pipeline_regression(self):
        response = self.app.post('/reset_pipeline')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'pipeline reset successfully', response.data)

    def test_process_camera_regression(self):
        # Create a dummy image frame (a white square)
        dummy_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', dummy_frame)
        img_str = base64.b64encode(buffer).decode('utf-8')
        img_data = {'frame': f'data:image/jpeg;base64,{img_str}'}

        response = self.app.post('/process_camera', json=img_data)
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()

        self.assertIn('image', response_data)
        self.assertIn('label', response_data)
        self.assertIn('counter', response_data)
        self.assertIn('stage', response_data)
        self.assertIn('angles_status', response_data)
        self.assertIn('detailed_feedback', response_data)

if __name__ == '__main__':
    unittest.main()
