# This is the same as the main.py, just implemented as Flask instead.

import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, render_template, Response
import sys


# Initialize Flask app
app = Flask(__name__)

# Initialize Mediapipe Pose and FaceMesh
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

i = 0
total_bad_ear_z = 0
bad_ear_count = 0

total_good_ear_z = 0
good_ear_count = 0

total_bad_nose_z = 0
bad_nose_count = 0

total_good_nose_z = 0
good_nose_count = 0

good_angle = 0
bad_angle = 0
bad_ear_angle = 0
good_ear_angle = 0
ear_ang = 0

# Load Pose and FaceMesh models
pose = mp_pose.Pose()
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)  # Refine landmarks for better eye detection


should_diff = []

def addToWindow(arr, value):
    arr.append(value)
    if len(arr) > 50:
        arr.pop(0)
    return arr

posture_status = "Good Posture"
color = (0, 255, 0)

# Open webcam
cap = cv2.VideoCapture(0)

# Define generator for video streaming
def generate():
    i = 0
    total_bad_ear_z = 0
    bad_ear_count = 0

    total_good_ear_z = 0
    good_ear_count = 0

    total_bad_nose_z = 0
    bad_nose_count = 0

    total_good_nose_z = 0
    good_nose_count = 0

    good_angle = 0
    bad_angle = 0
    bad_ear_angle = 0
    good_ear_angle = 0
    ear_ang = 0
    posture_status = "Good Posture"
    color = (0, 255, 0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        i += 1
        # Convert frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process pose and face landmarks separately
        pose_results = pose.process(rgb_frame)
        face_results = face_mesh.process(rgb_frame)

        if (i % 10 == 0):
            # Draw pose landmarks
            if pose_results.pose_landmarks:

                #mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                pose_landmarks = pose_results.pose_landmarks.landmark
                
                right_shoulder = pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                right_elbow = pose_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
                right_wrist = pose_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                right_hip = pose_landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
                right_knee = pose_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
                right_ankle = pose_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

                left_shoulder = pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                left_elbow = pose_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                left_wrist = pose_landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
                left_hip = pose_landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                left_knee = pose_landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                left_ankle = pose_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

                # Normalize shoulder y-coordinates using z (depth)
                norm_right_sh_y = right_shoulder.y / right_shoulder.z
                norm_left_sh_y = left_shoulder.y / left_shoulder.z

                # Compute difference in normalized shoulder y-coordinates
                should_diff = abs(norm_right_sh_y - norm_left_sh_y)

                threshold = 1.5
                app.logger.info(should_diff)
                if should_diff > threshold:
                    posture_status = "Bad Posture (Shoulders Tilted)"
                    color = (0, 0, 255)  # Red
                else:
                    posture_status = "Good Posture"
                    color = (0, 255, 0)  # Green

                # Display Result
                # cv2.putText(frame, posture_status, (50, 50),
                #             cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            
            # Draw face landmarks
            if face_results.multi_face_landmarks and not posture_status == "Bad Posture (Shoulders Tilted)":
                app.logger.info("Bye")
                for face_landmarks in face_results.multi_face_landmarks:
                    # Extract key points
                    nose_tip = face_landmarks.landmark[1]   # Nose Tip
                    chin = face_landmarks.landmark[152]     # Chin
                    left_ear = face_landmarks.landmark[234]  # Left Ear
                    right_ear = face_landmarks.landmark[454] # Right Ear

                    # Get z-coordinates (depth)
                    nose_z = nose_tip.z
                    chin_z = chin.z
                    left_ear_z = left_ear.z
                    right_ear_z = right_ear.z

                    # Compute depth differences
                    ear_avg_z = (left_ear_z + right_ear_z) / 2
                    nose_chin_avg_z = (nose_z + chin_z) / 2

                    #Compute depth difference angle
                    avg_ear_z = (left_ear.z + right_ear.z) / 2
                    avg_ear_y = (left_ear.y + right_ear.y) / 2

                    avg_nose_z = (nose_tip.z + chin.z) / 2
                    avg_nose_y = (nose_tip.y + chin.y) / 2

                    head_neck_angle = np.arctan2(avg_ear_z - avg_nose_z, avg_ear_y - avg_nose_y)
                    ears_angle = np.arctan2(left_ear.z - right_ear.z, left_ear.x - right_ear.x)
                    ear_ang += ears_angle


                    # Check if head is tilted forward (bad posture)
                    if (head_neck_angle > 2.50 or head_neck_angle < 2.10):  # Adjust threshold as needed
                        total_bad_ear_z += ear_avg_z
                        bad_ear_count += 1

                        total_bad_nose_z += nose_chin_avg_z
                        bad_nose_count += 1

                        bad_angle += head_neck_angle
                        bad_ear_angle += ears_angle

                        posture_status = "Bad Posture (Head Tilted)"
                        color = (0, 0, 255)  # Red

                    else:
                        posture_status = "Good Posture"

                        total_good_ear_z += ear_avg_z
                        good_ear_count += 1

                        good_angle += head_neck_angle
                        good_ear_angle += ears_angle

                        total_good_nose_z += nose_chin_avg_z
                        good_nose_count += 1

                        color = (0, 255, 0)  # Green
            # Encode image as JPEG for web display
        # Display Result
        cv2.putText(frame, posture_status, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        # Yield image as byte stream for Flask to send to browser
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

# Flask route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to stream video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, threaded=True)
