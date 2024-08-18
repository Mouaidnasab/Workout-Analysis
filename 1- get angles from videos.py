import math
import cv2
import numpy as np
import mediapipe as mp
import os
import pandas as pd

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

def calculate_angle(landmark1, landmark2, landmark3):
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360
    return angle

def extract_angles(video_path, pose, video_id):
    cap = cv2.VideoCapture(video_path)
    angles = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        imageRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(imageRGB)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            right_elbow_angle = calculate_angle(
                (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].z)
            )
            right_shoulder_angle = calculate_angle(
                (landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].z)
            )
            right_hip_angle = calculate_angle(
                (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].z)
            )
            right_knee_angle = calculate_angle(
                (landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].z)
            )
            right_ankle_angle = calculate_angle(
                (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].z),
                (landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].z)
            )
            angles.append([video_id, right_elbow_angle, right_shoulder_angle, right_hip_angle, right_knee_angle, right_ankle_angle])

            # Visualize the angles
            cv2.putText(frame, f'Elbow: {right_elbow_angle:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f'Shoulder: {right_shoulder_angle:.2f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f'Hip: {right_hip_angle:.2f}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f'Knee: {right_knee_angle:.2f}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f'Ankle: {right_ankle_angle:.2f}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        cv2.imshow('Pose Estimation', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return angles

def process_videos(directory, label, pose):
    all_angles = []
    for video_file in os.listdir(directory):
        if video_file.endswith(".mp4"):
            video_path = os.path.join(directory, video_file)
            video_id = os.path.splitext(video_file)[0]
            print(f'Processing {video_path}')
            angles = extract_angles(video_path, pose, video_id)
            for angle_set in angles:
                all_angles.append(angle_set + [label])
    return all_angles

correct_angles = process_videos("/Users/mouaidnasab/Downloads/Mediapipe_example-main/correct", 1, pose)
incorrect_angles = process_videos("/Users/mouaidnasab/Downloads/Mediapipe_example-main/incorrect", 0, pose)

# Combine and save the data
all_data = correct_angles + incorrect_angles
df = pd.DataFrame(all_data, columns=["video_id", "right_elbow_angle", "right_shoulder_angle", "right_hip_angle", "right_knee_angle", "right_ankle_angle", "label"])
df.to_csv("angles_data.csv", index=False)

pose.close()
