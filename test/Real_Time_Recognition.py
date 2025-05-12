# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 14:18:56 2025

@author: PC
"""
import cv2
import numpy as np
import joblib
import winsound
from skimage.feature import hog

def detect_face(image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        return image[y:y+h, x:x+w], (x, y, w, h)
    return None, None

def preprocess(face):
    face = cv2.resize(face, (64, 64))
    face = cv2.equalizeHist(face)
    return face / 255.0

def extract_hog_features(image):
    return hog(image, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True)

if __name__ == "__main__":
    model = joblib.load("face_recognition_model.pkl")
    label_dict = joblib.load("label_dict.pkl")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la caméra.")
        exit(1)

    confidence_threshold = 0.3  # Seuil pour une reconnaissance fiable
    beep_threshold = 0.3       # Seuil pour émettre un bip (si inconnu)
    known_person_detected = False

    print("Appuyez sur 'q' pour quitter.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erreur lors de la lecture de la trame vidéo.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face, coords = detect_face(gray)
        if face is not None and coords is not None:
            face_proc = preprocess(face)
            feature = extract_hog_features(face_proc).reshape(1, -1)
            prediction = model.predict(feature)
            probabilities = model.predict_proba(feature)
            confidence = probabilities.max()

            if confidence > confidence_threshold:
                label_text = label_dict[prediction[0]]
                color = (0, 255, 0)  # Vert pour visage reconnu
                known_person_detected = True
            else:
                label_text = "Inconnu"
                color = (0, 0, 255)  # Rouge pour visage inconnu

            x, y, w, h = coords
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{label_text} ({confidence:.2f})", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            if confidence <= beep_threshold:
                try:
                    winsound.Beep(1000, 500)
                except RuntimeError:
                    print("Erreur lors de l'émission du bip.")

        cv2.imshow('Reconnaissance faciale', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if known_person_detected:
        cv2.putText(frame, f"Personne reconnue: {label_text}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow('Reconnaissance', frame)
        cv2.waitKey(0)

    cap.release()
    cv2.destroyAllWindows()
