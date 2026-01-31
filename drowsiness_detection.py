# Drowsiness Detection using Haar Cascades with improved logic
import cv2
import numpy as np
import time
import os

# Load Haar cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Parameters
CONSECUTIVE_FRAMES = 15
FRAME_COUNT = 0
count_sleep = 0

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

def generate_frames():
    global FRAME_COUNT, count_sleep
    cap = cv2.VideoCapture(0)
    assure_path_exists("dataset/")

    print("Starting drowsiness detection...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame
        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        eyes_detected = False

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Detect eyes in the full face region
            eyes = eye_cascade.detectMultiScale(gray[y:y+h, x:x+w], 1.1, 3)

            if len(eyes) > 0:
                eyes_detected = True
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)

        if not eyes_detected:
            FRAME_COUNT += 1
            cv2.putText(frame, "EYES CLOSED", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if FRAME_COUNT >= CONSECUTIVE_FRAMES:
                count_sleep += 1
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                cv2.imwrite(f"dataset/frame_sleep{count_sleep}.jpg", frame)
        else:
            FRAME_COUNT = 0

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # For standalone testing
    for frame in generate_frames():
        pass
