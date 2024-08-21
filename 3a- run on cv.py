import os
import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
from piplinecv import *

# Choose between "correct" and "incorrect" folders.
folder_choice = "incorrect"  # Change this to "incorrect" as needed

# Path to the video directories.
video_directories = {
    "correct": "correct/",
    "incorrect": "incorrect/"
}


# Get the list of all video files in the selected directory.
video_files = [os.path.join(video_directories[folder_choice], f) for f in os.listdir(video_directories[folder_choice]) if f.endswith('.mp4')]

# Initialize the mediapipe pose class.
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    for video_file in video_files:
        cap = cv2.VideoCapture(video_file)
        
        frame_count = 0
        while cap.isOpened():
            # Read a frame.
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Perform pose detection.
            output_image, landmarks = detectPose(frame, pose, display=False)
            
            # Classify the pose based on the detected landmarks.
            output_image, label = classifyPose(landmarks, output_image, display=False)
            
            # Display the frame.
            cv2.imshow('Pose Classification', output_image)
            
            frame_count += 1

            # Check if the 'q' key is pressed.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Release the video capture object.
        cap.release()

# Close all OpenCV windows.
cv2.destroyAllWindows()
