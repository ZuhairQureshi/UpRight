import base64
import cv2
import mediapipe as mp
from flask import Flask, Response, jsonify, request
import numpy as np
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)  # Refine landmarks for better eye detection

mp_drawing = mp.solutions.drawing_utils

# OpenCV video capture (0 = default webcam)
cap = cv2.VideoCapture(0)

def generate_frames():
    """ Continuously capture frames from the webcam and yield them as MJPEG with posture analysis """
    while True:
        success, frame = cap.read()
        if not success:
            break  # Stop if no frame is read

        # Analyze posture in the current frame
        posture_status, color = analyze_posture(frame)

        # Overlay posture status on the frame
        cv2.putText(frame, posture_status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

        # Convert the frame to JPEG format
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Video stream route for frontend
@app.route('/video_feed')
def video_feed():
    """ Route to provide real-time video streaming """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Analyze posture function
def analyze_posture(frame):
    """ Analyze posture using MediaPipe Pose detection """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_results = pose.process(rgb_frame)
    face_results = face_mesh.process(rgb_frame)

    posture_status = "Good Posture"
    color = (0, 255, 0)  # Green

    if pose_results.pose_landmarks:
        pose_landmarks = pose_results.pose_landmarks.landmark
        right_shoulder = pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_shoulder = pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]

        norm_right_sh_y = right_shoulder.y / right_shoulder.z
        norm_left_sh_y = left_shoulder.y / left_shoulder.z

        should_diff = abs(norm_right_sh_y - norm_left_sh_y)

        threshold = 1.5
        if should_diff > threshold:
            posture_status = "Bad Posture (Shoulders Tilted)"
            color = (0, 0, 255)  # Red


    # Draw face landmarks
    if face_results.multi_face_landmarks and not posture_status == "Bad Posture (Shoulders Tilted)":
        for face_landmarks in face_results.multi_face_landmarks:
            #mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION)

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

            # Check if head is tilted forward (bad posture)
            if (head_neck_angle > 2.50 or head_neck_angle < 2.10):  # Adjust threshold as needed
                posture_status = "Bad Posture (Head Tilted)"
                color = (0, 0, 255)  # Red

            else:
                posture_status = "Good Posture"
                color = (0, 255, 0)  # Green

    return posture_status, color

# Flask route to analyze posture (for frontend interaction)
@app.route('/analyze_posture', methods=['POST'])
def analyze_posture_route():
    try:
        # Get the base64-encoded image data from the request
        data = request.get_json()
        image_data = data['image']

        # Remove the "data:image/png;base64," prefix
        img_data = base64.b64decode(image_data.split(',')[1])

        # Convert the image data to a NumPy array
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Analyze posture on the decoded image
        posture_status, color = analyze_posture(frame)

        return jsonify({'status': posture_status})

    except Exception as e:
        print(f"Error during posture analysis: {e}")
        return jsonify({'status': 'Error during posture analysis. Please try again.'})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
