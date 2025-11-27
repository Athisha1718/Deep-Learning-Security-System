import cv2
import numpy as np
import os

def compare_faces(saved_face_path, new_face):
    saved_face = cv2.imread(saved_face_path)
    saved_face = cv2.resize(saved_face, (new_face.shape[1], new_face.shape[0]))
    difference = cv2.absdiff(saved_face, new_face)
    b, g, r = cv2.split(difference)
    total_diff = cv2.countNonZero(b) + cv2.countNonZero(g) + cv2.countNonZero(r)
    return total_diff

def delete_saved_face():
    face_path = "saved_passenger/passenger_face.jpg"
    if os.path.exists(face_path):
        os.remove(face_path)
        print("✅ Saved face image deleted after unlock.")
    else:
        print("⚠️ No saved face found to delete.")

# --- Main program starts here ---

saved_face_path = "saved_passenger/passenger_face.jpg"

# Start webcam
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("Press 'o' to scan and open locker")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow('Face Verification', frame)

    key = cv2.waitKey(1)
    if key == ord('o'):
        for (x, y, w, h) in faces:
            new_face = frame[y:y+h, x:x+w]

            diff = compare_faces(saved_face_path, new_face)

            if diff < 10000:  # threshold
                print("✅ Face Matched - Unlock Locker")
                delete_saved_face()
            else:
                print("❌ Invalid Face - Trigger Buzzer and Send Email")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
