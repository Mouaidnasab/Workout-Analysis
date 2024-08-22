import unittest
import json
import cv2
import numpy as np
import base64
import os
from flask import Flask
from io import BytesIO
from app import app  # Assuming the Flask app is in app.py

class EndToEndTestCase(unittest.TestCase):

    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        # Test the index route
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)  # Assuming the index.html starts with a doctype

    def test_reset_pipeline(self):
        # Test the reset_pipeline route
        response = self.app.post('/reset_pipeline')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'pipeline reset successfully')

    def test_upload_video(self):
        # Path to the sample video
        video_path = os.path.join('test_data', 'test_video.mp4')

        # Open the video file in binary mode
        with open(video_path, 'rb') as video_file:
            # Test the upload_video route with the actual video
            response = self.app.post('/upload_video', content_type='multipart/form-data',
                                     data={'video': (video_file, 'test_video.mp4')})

            self.assertEqual(response.status_code, 200)  # Expect success with valid video
            data = json.loads(response.data)
            self.assertTrue(len(data) > 0)  # Ensure some frames were processed
            # Optional: Check the structure of the data
            for frame_data in data:
                self.assertIn('image', frame_data)
                self.assertIn('label', frame_data)
                self.assertIn('counter', frame_data)
                self.assertIn('stage', frame_data)
                self.assertIn('angles_status', frame_data)
                self.assertIn('detailed_feedback', frame_data)

    def test_process_camera(self):
        # Path to the sample video
        video_path = os.path.join('test_data', 'test_video.mp4')

        # Capture the first frame from the video
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            self.fail("Failed to read a frame from the video.")

        # Encode the frame as JPEG and then to base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode('utf-8')
        img_data = f'data:image/jpeg;base64,{img_str}'

        # Test the process_camera route with the actual frame
        response = self.app.post('/process_camera', json={'frame': img_data})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('image', data)
        self.assertIn('label', data)
        self.assertIn('counter', data)
        self.assertIn('stage', data)
        self.assertIn('angles_status', data)
        self.assertIn('detailed_feedback', data)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
