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

# OpenCV video capture (0 = default webcam)
cap = cv2.VideoCapture(0)

def generate_frames():
    """ Continuously capture frames from the webcam and yield them as MJPEG """
    while True:
        success, frame = cap.read()
        if not success:
            break  # Stop if no frame is read

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
