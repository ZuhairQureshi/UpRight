import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Start Video Capture
cap = cv2.VideoCapture(0)
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

with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        i += 1
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
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

                # Display Result
                cv2.putText(frame, posture_status, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

                # if i % 10 == 0:
                #     print(posture_status)
                #     print("Nose Z:", nose_z)
                #     print("Ear Z:", ear_avg_z)
                #     print()

        # Show Output
        cv2.imshow("Posture Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


print(f"Average Good Ear Z: {total_good_ear_z / good_ear_count:.2f}")
print(f"Average Good Nose Z: {total_good_nose_z / good_nose_count:.2f}")
print()
print(f"Average Good Angle: {good_angle / good_ear_count:.2f}")
print()
print(f"Average Ear Angle: {ear_ang / i:.2f}")

cap.release()
cv2.destroyAllWindows()
