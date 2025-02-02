import cv2
import mediapipe as mp
import numpy as np

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
# Open webcam
cap = cv2.VideoCapture(0)

def addToWindow(arr, value):
    arr.append(value)
    if len(arr) > 50:
        arr.pop(0)
    return arr

posture_status = "Good Posture"
color = (0, 255, 0)

while cap.isOpened():
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
        posture_status = "Good Posture"
        color = (0, 255, 0)

        # Draw pose landmarks
        if pose_results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
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

    # Display Result
    cv2.putText(frame, posture_status, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
    # Display the frame
    cv2.imshow("Pose and Face Detection", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
