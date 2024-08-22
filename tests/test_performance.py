import unittest
import time
from app import app

class PerformanceTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_homepage_performance(self):
        start_time = time.time()
        response = self.app.get('/')
        end_time = time.time()

        duration = end_time - start_time
        print(f"Homepage load time: {duration:.4f} seconds")

        self.assertLess(duration, 1.0, "Homepage load time is too slow")  # Expecting load time under 1 second
        self.assertEqual(response.status_code, 200)

    def test_upload_video_performance(self):
        with open('test_data/test_video.mp4', 'rb') as video_file:
            data = {'video': (video_file, 'test_video.mp4')}
            start_time = time.time()
            response = self.app.post('/upload_video', data=data, content_type='multipart/form-data')
            end_time = time.time()

        duration = end_time - start_time
        print(f"Video upload processing time: {duration:.4f} seconds")

        self.assertLess(duration, 5.0, "Video processing time is too slow")  # Expecting processing time under 5 seconds
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
