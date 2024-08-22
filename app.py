from flask import Flask, render_template, Response, request, jsonify
from pipelineweb import classifyPose, detectPose, reset_pipeline
import mediapipe as mp
import cv2
import numpy as np
import base64
import logging
import os
import tempfile

app = Flask(__name__)

mp_pose = mp.solutions.pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

@app.route('/')
def index():

    return render_template('index.html')

# Global variable to store counter state
counter = 0



@app.route('/reset_pipeline', methods=['POST'])
def reset_pipeline_endpoint():
    reset_pipeline()
    return jsonify({"status": "pipeline reset successfully"})


def process_frame(image):
    # Process the frame
    image = np.frombuffer(image, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    output_image, data = classifyPose(detectPose(image, mp_pose)[1], detectPose(image, mp_pose)[0], display=False)
    output_image = cv2.flip(output_image, 1)

    # Convert image to base64 string
    _, buffer = cv2.imencode('.jpg', output_image)
    img_str = base64.b64encode(buffer).decode('utf-8')

    return img_str, data

def process_video_file(video_file_path):
    reset_pipeline()
    logging.debug(f"Processing video file: {video_file_path}")

    cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        logging.error("Failed to open the video file.")
        raise ValueError("Failed to open the video file.")
    
    frames_data = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        output_image, data = classifyPose(detectPose(frame, mp_pose)[1], detectPose(frame, mp_pose)[0], display=False)
        
        _, buffer = cv2.imencode('.jpg', output_image)
        img_str = base64.b64encode(buffer).decode('utf-8')

        frames_data.append({
            'image': img_str,
            'label': data['label'],
            'counter': data['counter'],
            'stage': data['stage'],
            'angles_status': data['angles_status'],
            'detailed_feedback': data['detailed_feedback']
        })

    cap.release()

    return frames_data

@app.route('/upload_video', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            logging.error("No video file in request")
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']

        if video_file.filename == '':
            logging.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        # Save the uploaded video to a temporary file
        temp_dir = tempfile.gettempdir()
        temp_video_path = os.path.join(temp_dir, video_file.filename)
        video_file.save(temp_video_path)
        logging.debug(f"Video file saved temporarily at {temp_video_path}")
        
        # Process the video file
        frames_data = process_video_file(temp_video_path)
        
        # Clean up the temporary file
        os.remove(temp_video_path)
        
        return jsonify(frames_data)
    except ValueError as ve:
        logging.error(f"ValueError during video processing: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging.error(f"Error processing video: {e}")
        return jsonify({'error': 'Failed to process video'}), 500

@app.route('/process_camera', methods=['POST'])
def process_camera():
    try:

        frame = request.json['frame']
        frame = base64.b64decode(frame.split(',')[1])
        img_str, data = process_frame(frame)
        return jsonify({'image': img_str, 'label': data['label'], 'counter': data['counter'], 'stage': data['stage'], 'angles_status': data['angles_status'], 'detailed_feedback': data['detailed_feedback'] })
    except Exception as e:
        print(f"Error processing camera frame: {e}")
        return jsonify({'error': 'Failed to process camera frame'}), 500

if __name__ == '__main__':
    app.run(debug=True,port='3000')
