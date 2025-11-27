import cv2
import os

# Create a directory to save passenger images
save_path = "saved_passenger"
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Start webcam
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("Press 's' to scan and save face")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow('Face Scan', frame)

    key = cv2.waitKey(1)
    if key == ord('s'):
        # Save the face
        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            cv2.imwrite(f"{save_path}/passenger_face.jpg", face)
            print("✅ Face saved successfully!")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
