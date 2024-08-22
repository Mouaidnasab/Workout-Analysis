import unittest
from unittest.mock import patch, MagicMock
from app import app, process_frame, process_video_file
import base64
import numpy as np
import cv2

class UnitTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.process_frame')
    def test_process_frame_with_valid_data(self, mock_process_frame):
        # Simulate valid frame processing
        mock_process_frame.return_value = ("processed_image_string", {"label": "push-up", "counter": 5, "stage": "up", "angles_status": {}, "detailed_feedback": ""})
        
        # Create a dummy image frame (a white square)
        dummy_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode('.jpg', dummy_frame)
        img_str = base64.b64encode(buffer).decode('utf-8')
        img_data = {'frame': f'data:image/jpeg;base64,{img_str}'}
        
        # Correctly send the data as JSON
        response = self.app.post('/process_camera', json=img_data)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('image', response_data)
        self.assertEqual(response_data['label'], "push-up")
        self.assertEqual(response_data['counter'], 5)
        self.assertEqual(response_data['stage'], "up")
        mock_process_frame.assert_called_once()

    @patch('app.process_frame')
    def test_process_frame_with_invalid_data(self, mock_process_frame):
        # Simulate an exception during frame processing
        mock_process_frame.side_effect = Exception("Processing Error")
        
        # Send an invalid base64 encoded image
        invalid_frame = b'invalid_frame_data'
        img_str = base64.b64encode(invalid_frame).decode('utf-8')
        img_data = {'frame': f'data:image/jpeg;base64,{img_str}'}
        
        # Correctly send the data as JSON
        response = self.app.post('/process_camera', json=img_data)
        
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Failed to process camera frame', response.data)
        mock_process_frame.assert_called_once()

    @patch('app.process_video_file')
    def test_process_video_file_success(self, mock_process_video_file):
        # Simulate successful video file processing
        mock_process_video_file.return_value = [{'image': 'processed_image', 'label': 'squat', 'counter': 10, "stage": "up", "angles_status": {}, "detailed_feedback": ""}]
        
        with open('test_data/test_video.mp4', 'rb') as video_file:
            data = {'video': (video_file, 'test_video.mp4')}
            response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertTrue(len(response_data) > 0)
        self.assertEqual(response_data[0]['label'], 'squat')
        self.assertEqual(response_data[0]['counter'], 10)
        mock_process_video_file.assert_called_once()

    @patch('app.process_video_file')
    def test_process_video_file_failure(self, mock_process_video_file):
        # Simulate a failure during video file processing
        mock_process_video_file.side_effect = ValueError("Invalid video format")
        
        with open('test_data/test_video.mp4', 'rb') as video_file:
            data = {'video': (video_file, 'test_video.mp4')}
            response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid video format', response.data)
        mock_process_video_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()
