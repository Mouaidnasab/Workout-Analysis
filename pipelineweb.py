import math
import numpy as np
import mediapipe as mp
import pandas as pd
import logging
import time
import cv2
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(filename='pose_mistakes.log', level=logging.INFO, format='%(asctime)s - %(message)s')

counter = 0
current_position = 'None'
stage = 'Start'

# Load optimal angle ranges
ranges_df = pd.read_csv("optimal_joint_angle_ranges.csv")

# Convert the ranges to a dictionary
angle_ranges = {}
for index, row in ranges_df.iterrows():
    angle_ranges[row['joint']] = {
        "range1": (row['optimal_min_range1'], row['optimal_max_range1']),
        "range2": (row['optimal_min_range2'], row['optimal_max_range2']) if pd.notnull(row['optimal_min_range2']) else None
    }

# Load pre-calculated angles
angles_data = pd.read_csv("angles_data.csv")

# Time
time_ = 0

# Initializing mediapipe pose class.
mp_pose = mp.solutions.pose
mp_drawing_styles = mp.solutions.drawing_styles
mp_drawing = mp.solutions.drawing_utils 

# Define a dictionary to map landmark indices to names
POSE_LANDMARKS = {
    0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: "", 9: "", 10: "",
    11: "", 12: "RIGHT_SHOULDER", 13: "", 14: "RIGHT_ELBOW", 15: "", 16: "RIGHT_WRIST",
    17: "", 18: "", 19: "", 20: "RIGHT_INDEX", 21: "", 22: "", 23: "", 24: "RIGHT_HIP",
    25: "", 26: "RIGHT_KNEE", 27: "", 28: "RIGHT_ANKLE", 29: "", 30: "", 31: "",
    32: "RIGHT_FOOT_INDEX"
}

right_elbow_angle = 0
right_shoulder_angle = 0
right_wrist_angle = 0
right_ankle_angle = 0
right_hip_angle = 0

right_elbow_angle_previous = 0
right_shoulder_angle_previous = 0
right_wrist_angle_previous = 0
right_ankle_angle_previous = 0
right_hip_angle_previous = 0

right_elbow_angle_diff = 0
right_shoulder_angle_diff = 0
right_wrist_angle_diff = 0
right_ankle_angle_diff = 0
right_hip_angle_diff = 0

Angle_previous = []
Angle_diff = []

def log_mistake(reason):
    logging.info(reason)

def reset_pipeline():
    global counter, stage, current_position
    counter = 0
    stage = 'Start'
    current_position = 'None'


def detectPose(image, pose, display=False):
    output_image = image.copy()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(imageRGB)
    height, width, _ = image.shape
    landmarks = []
    
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image=output_image, 
            landmark_list=results.pose_landmarks, 
            connections=mp_pose.POSE_CONNECTIONS, 
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )

        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            landmarks.append((int(landmark.x * width), int(landmark.y * height), (landmark.z * width)))
            cv2.putText(output_image, POSE_LANDMARKS[idx], (int(landmark.x * width), int(landmark.y * height)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    else:
        for i in range(33):
            landmarks.append((0, 0, 0))

    if display:
        plt.figure(figsize=[22,22])
        plt.subplot(121); plt.imshow(image[:,:,::-1]); plt.title("Original Image"); plt.axis('off');
        plt.subplot(122); plt.imshow(output_image[:,:,::-1]); plt.title("Output Image"); plt.axis('off');
        mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
    else:
        return output_image, landmarks

def calculateAngle(landmark1, landmark2, landmark3):
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360
    return angle

def pushup_counter(elbow_angle, counter, stage, current_position, tolerance=20):
    # Check if the elbow_angle is None
    if elbow_angle is None:
        return counter, stage, current_position
    
    position_1 = 165  # Top position (full extension)
    position_2 = 110  # Mid position
    position_3 = 70   # Bottom position (lowest point)

    if position_1 - tolerance <= elbow_angle <= position_1 + tolerance:
        current_position = 'Position 1'
        if stage == 'Half Way Up':
            stage = 'Start'
            counter += 1
        elif stage in ['Start', 'Half Way']:
            stage = 'UP'
    
    elif position_2 - tolerance <= elbow_angle <= position_2 + tolerance:
        current_position = 'Position 2'
        if stage == 'UP':
            stage = 'Half Way'
        elif stage == 'Move Up':
            stage = 'Half Way Up'
    
    elif position_3 - tolerance <= elbow_angle <= position_3 + tolerance:
        current_position = 'Position 3'
        if stage == 'Half Way':
            stage = 'Down'
        elif stage == 'Down':
            stage = 'Move Up'

    if stage == 'Start' and current_position == 'Position 2':
        log_mistake(f"User moved from Position 1 to Position 2 without going down fully. Stage: {stage}")

    if stage == 'Half Way Up' and current_position == 'Position 1':
        log_mistake(f"User moved back to Position 1 from Position 2 without completing the push-up. Stage: {stage}")

    return counter, stage, current_position

def classifyPose(landmarks, output_image, display=False):
    global time_
    global Angle_previous
    global Angle_diff
    global right_elbow_angle
    global right_shoulder_angle
    global right_wrist_angle
    global right_ankle_angle
    global right_hip_angle
    
    global right_elbow_angle_previous
    global right_shoulder_angle_previous
    global right_wrist_angle_previous
    global right_ankle_angle_previous
    global right_hip_angle_previous
    
    global right_elbow_angle_diff
    global right_shoulder_angle_diff
    global right_wrist_angle_diff
    global right_ankle_angle_diff
    global right_hip_angle_diff
    global current_position

    global counter
    global stage

    label = 'Unknown Pose'
    
    # Initialize angles to None or a default value
    right_elbow_angle = None
    right_shoulder_angle = None
    right_knee_angle = None
    right_ankle_angle = None
    right_hip_angle = None
    
    correct_pose = True
    angles_status = []
    detailed_feedback = []
    
    def check_visibility(landmark):
        x, y, z = landmark
        if x <= 0 or y <= 0 or x >= output_image.shape[1] or y >= output_image.shape[0]:
            return False
        return True
    
    
    def check_angle(joint, angle, joint_name, correction_message, visible):
        if not visible or angle is None:
            angles_status.append(f"{joint_name}: Unknown")
            return False
        
        ranges = angle_ranges[joint]
        correct_pose = True
        
        if angle is not None:
            if ranges["range2"] is not None:
                correct = (ranges["range1"][0] <= angle <= ranges["range1"][1]) or (ranges["range2"][0] <= angle <= ranges["range2"][1])
            else:
                correct = ranges["range1"][0] <= angle <= ranges["range1"][1]
            
            if not correct:
                correct_pose = False
                angles_status.append(f"{joint_name}: {angle:.2f} Incorrect")
                detailed_feedback.append(correction_message)
                log_mistake(f"Incorrect {joint_name.lower()} angle: {angle:.2f}")
            else:
                angles_status.append(f"{joint_name}: {angle:.2f} Correct")
        else:
            angles_status.append(f"{joint_name}: Unknown")
        
        return correct_pose

    # Calculate angles based on landmarks
    if landmarks:
        visible_elbow = check_visibility(landmarks[12]) and check_visibility(landmarks[14]) and check_visibility(landmarks[16])
        visible_shoulder = check_visibility(landmarks[14]) and check_visibility(landmarks[12]) and check_visibility(landmarks[24])
        visible_knee = check_visibility(landmarks[28]) and check_visibility(landmarks[26]) and check_visibility(landmarks[24])
        visible_ankle = check_visibility(landmarks[24]) and check_visibility(landmarks[28]) and check_visibility(landmarks[32])
        visible_hip = check_visibility(landmarks[12]) and check_visibility(landmarks[24]) and check_visibility(landmarks[26])
        
        if visible_elbow:
            right_elbow_angle = calculateAngle(landmarks[12], landmarks[14], landmarks[16])
        if visible_shoulder:
            right_shoulder_angle = calculateAngle(landmarks[14], landmarks[12], landmarks[24])
        if visible_knee:
            right_knee_angle = calculateAngle(landmarks[28], landmarks[26], landmarks[24])
        if visible_ankle:
            right_ankle_angle = calculateAngle(landmarks[24], landmarks[28], landmarks[32])
        if visible_hip:
            right_hip_angle = calculateAngle(landmarks[12], landmarks[24], landmarks[26])
        
        correct_pose = check_angle("right_elbow_angle", right_elbow_angle, "Elbow", "Raise your elbow", visible_elbow) and correct_pose
        correct_pose = check_angle("right_shoulder_angle", right_shoulder_angle, "Shoulder", "Adjust your shoulder", visible_shoulder) and correct_pose
        correct_pose = check_angle("right_hip_angle", right_hip_angle, "Hip", "Straighten your hips", visible_hip) and correct_pose
        correct_pose = check_angle("right_knee_angle", right_knee_angle, "Knee", "Raise your knee", visible_knee) and correct_pose
        correct_pose = check_angle("right_ankle_angle", right_ankle_angle, "Ankle", "Straighten your ankle", visible_ankle) and correct_pose
        
        # Check if any angle status is unknown
        if any("Unknown" in status for status in angles_status):
            label = "Move inside the camera"
            detailed_feedback.append("Move inside the camera")
        elif correct_pose:
            label = "Correct Pose"
        else:
            label = "Incorrect Pose"

        counter, stage, current_position = pushup_counter(right_elbow_angle, counter, stage, current_position)
    else:
        label = "No Pose Detected"

    output_data = {
        "counter": counter,
        "stage": stage,
        "angles_status": angles_status,
        "detailed_feedback": detailed_feedback,
        "label": label
    }

    return output_image, output_data
