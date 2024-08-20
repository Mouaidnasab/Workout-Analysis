import unittest
from pipelineweb import classifyPose, detectPose, reset_pipeline
import numpy as np
import cv2

class PipelineWebTests(unittest.TestCase):

    def test_classify_pose(self):
        # Example test for classifyPose
        # Assume `pose_landmarks` and `image` are the expected input values
        pose_landmarks = None  # Replace with a valid pose_landmarks value for your test
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # You can replace None with proper mock data
        output_image, data = classifyPose(pose_landmarks, image, display=False)
        
        # Test the output data structure
        self.assertIn('label', data)
        self.assertIn('counter', data)
        self.assertIn('stage', data)
        self.assertIn('angles_status', data)
        self.assertIn('detailed_feedback', data)

    def test_reset_pipeline(self):
        # Test reset_pipeline function
        reset_pipeline()  # Ensure this runs without error


if __name__ == '__main__':
    unittest.main()