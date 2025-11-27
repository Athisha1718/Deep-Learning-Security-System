from email.mime.image import MIMEImage
import cv2
import os
import numpy as np
import time
from flask import Flask, render_template, Response, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

# Email configuration - UPDATED WITH SECURE APPROACH
EMAIL_ENABLED = True
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USERNAME = "kalpana25k2006@gmail.com"
# Never hardcode passwords - use environment variables or config files
ADMIN_EMAIL = "kalpana25k2006@gmail.com"

# Global camera object
camera = None

def send_alert_email(confidence=None, image_path=None):
    """Send an email alert about unauthorized access attempt"""
    if not EMAIL_ENABLED:
        return
        
    try:
        # Get password securely - you should set this as an environment variable
        email_password = os.getenv('GMAIL_APP_PASSWORD')  # Recommended approach
        if not email_password:
            raise ValueError("Email password not configured")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = "🚨 Unauthorized Access Attempt Detected"
        
        body = f"""
        <h2>Security Alert</h2>
        <p>An unauthorized access attempt was detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        if confidence is not None:
            body += f"<p>Confidence level: {confidence:.2f}</p>"
            
        if image_path and os.path.exists(image_path):
            body += "<p>Attempt image attached.</p>"
            with open(image_path, 'rb') as f:
                img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(image_path))
            msg.attach(image)
        
        msg.attach(MIMEText(body, 'html'))
        
        # Secure email sending with context manager
        with smtplib.SMTP(SMTP_SERVER, 465) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USERNAME, email_password)
            server.send_message(msg)
            
        print("✅ Security alert email sent successfully")
        
    except Exception as e:
        print(f"❌ Failed to send alert email: {str(e)}")
        # Add more detailed error logging if needed
        import traceback
        traceback.print_exc()

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# LBPH Face Recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Saving path
save_path = os.path.join("static", "saved_passenger")
if not os.path.exists(save_path):
    os.makedirs(save_path)
    print(f"Created directory: {save_path}")

# Camera initialization and check
def initialize_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("❌ Camera not available!")
            return False
        else:
            print("✅ Camera is ready!")
            return True
    return True

def release_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None

# Initialize the camera
try:
    initialize_camera()
except RuntimeError as e:
    print(e)

# Face scanning function
def generate_frames():
    global camera
    while True:
        try:
            if camera is None:
                if not initialize_camera():
                    time.sleep(0.1)
                    continue

            success, frame = camera.read()
            if not success:
                print("❌ Lost connection with camera. Reinitializing...")
                release_camera()
                time.sleep(0.5)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5, minSize=(80, 80))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("❌ Error encoding frame.")
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error in generate_frames: {str(e)}")
            release_camera()
            time.sleep(1)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_scan')
def start_scan():
    global camera
    try:
        if camera is None:
            if not initialize_camera():
                return "❌ Camera initialization failed!"

        ret, frame = camera.read()
        if not ret:
            return "❌ Failed to grab frame from camera!"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5, minSize=(80, 80))

        if len(faces) == 0:
            return "❌ No face detected! Please come closer."

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            face = cv2.resize(face, (150, 150))

            # Save the face with proper path handling
            save_file_path = os.path.join(save_path, "passenger_face.jpg").replace("\\", "/")
            cv2.imwrite(save_file_path, face)
            time.sleep(0.3)  # Ensure file is written
            
            if not os.path.exists(save_file_path):
                return "❌ Error: Face image failed to save!"

            # Train the recognizer
            gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            recognizer.update([gray_face], np.array([0]))

            relative_path = "saved_passenger/passenger_face.jpg"
            return render_template('show_face.html', image_path=relative_path)

    except Exception as e:
        print(f"Error in start_scan: {str(e)}")
        return render_template('access_denied.html', error_message=str(e))

    return render_template('access_denied.html', error_message="Face scan failed")

@app.route('/open_locker')
def open_locker():
    global camera
    try:
        if camera is None:
            if not initialize_camera():
                return render_template('access_denied.html', error_message="Camera initialization failed")

        saved_face_path = os.path.join(save_path, "passenger_face.jpg").replace("\\", "/")
        if not os.path.exists(saved_face_path):
            return render_template('access_denied.html', error_message="No saved face found. Please scan first.")

        ret, frame = camera.read()
        if not ret:
            return render_template('access_denied.html', error_message="Failed to capture image.")

        # Save the attempt image for email
        attempt_path = os.path.join(save_path, "attempt_face.jpg").replace("\\", "/")
        cv2.imwrite(attempt_path, frame)
        
        saved_face = cv2.imread(saved_face_path, cv2.IMREAD_GRAYSCALE)
        saved_face = cv2.resize(saved_face, (150, 150))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5, minSize=(80, 80))

        if len(faces) == 0:
            send_alert_email(image_path=attempt_path)
            return render_template('access_denied.html', error_message="No face detected! Please come closer.")

        for (x, y, w, h) in faces:
            new_face = gray[y:y+h, x:x+w]
            new_face = cv2.resize(new_face, (150, 150))

            label, confidence = recognizer.predict(new_face)
            print(f"Label: {label}, Confidence: {confidence}")

            if confidence < 70:
                print("✅ Face Matched! Access Granted.")
                os.remove(saved_face_path)
                if os.path.exists(attempt_path):
                    os.remove(attempt_path)
                return render_template('authorized.html')
            else:
                print("❌ Face Not Matched! Access Denied.")
                send_alert_email(confidence=confidence, image_path=attempt_path)
                return render_template('access_denied.html', error_message="Face doesn't match. Confidence: {:.2f}".format(confidence))

    except Exception as e:
        print(f"Error in open_locker: {str(e)}")
        send_alert_email()
        return render_template('access_denied.html', error_message=str(e))

    send_alert_email()
    return render_template('access_denied.html', error_message="Face comparison failed")

@app.route('/')
def index():
    return render_template('indexs.html')

@app.route('/authorized')
def authorized():
    return render_template('authorized.html')

@app.route('/access_denied')
def access_denied():
    return render_template('access_denied.html')

@app.route('/check_env')
def check_env():
    return {
        'EMAIL_USERNAME': os.getenv('EMAIL_USERNAME'),
        'GMAIL_APP_PASSWORD': 'Exists' if os.getenv('GMAIL_APP_PASSWORD') else 'MISSING',
        'ADMIN_EMAIL': os.getenv('ADMIN_EMAIL')
    }
@app.route('/test_email')
def test_email():
    # Test with a dummy image path
    test_image = os.path.join(save_path, "passenger_face.jpg")
    if os.path.exists(test_image):
        send_alert_email(confidence=95.0, image_path=test_image)
    else:
        send_alert_email(confidence=95.0)  # Test without image
    return "Test email sent - check your inbox and spam folder"


@app.teardown_appcontext
def teardown_appcontext(exception):
    release_camera()


# [Rest of your existing code remains the same...]

if __name__ == "__main__":
    # Load environment variables if using .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    app.run(debug=True, host='0.0.0.0')