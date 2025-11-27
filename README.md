# Deep-Learning-Security-System

A face-recognition based security system that uses deep-learning to detect, verify, and respond to unauthorized access attempts. Integrating face capture, face-matching, and alert functionality (e.g. telegram alerts + buzzer).

**Motivation & Purpose**

The aim of this project is to build an accessible security solution leveraging deep learning and computer vision:

Automate identification of people for face detection/recognition.
Provide real-time security checks for restricted entry or sensitive areas.
Offer a reference implementation for users wanting to build AI based monitoring systems.
This project is especially relevant given growing demand for AI-powered surveillance and security automation.

**Setup & Usage
**
Clone the repository - git clone https://github.com/Kalpana-25-hello/deep-learning-security-system.git - cd deep-learning-security-system

Install dependencies - Python 3.x
- OpenCV

Run the main application: - python app.py - Use capture_and_save_face.py to register authorized users’ face images. - On detection of unknown/unregistered face, the system will use compare_faces.py, and trigger alert (e.g. buzzer and telegram message) using final_email_test.py.
