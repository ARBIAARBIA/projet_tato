# -*- coding: utf-8 -*- 
""" Script d'enrôlement d'un nouvel utilisateur (capture webcam + dataset + réentraînement) """

import os
import cv2
import csv
import numpy as np
import subprocess  # Added for running the model training script
from skimage.feature import hog
from datetime import datetime
import Train_Model_SVM  # Keep the existing import

# Paramètres
NUM_IMAGES = 20
DATASET_DIR = "dataset"
CONSENT_FILE = "consentements.csv"
IMG_SIZE = (64, 64)
RETRAIN_SCRIPT = "Train_Model_SVM.py"  # Path to the model training script

def detect_face(image):
    """Détecte un visage dans l'image"""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(image, 1.1, 5)
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        return image[y:y+h, x:x+w]
    return None

def preprocess(face):
    """Prétraite l'image du visage"""
    face = cv2.resize(face, IMG_SIZE)
    face = cv2.equalizeHist(face)
    return face

def get_user_name():
    """Obtient le nom ou l'identifiant de l'utilisateur"""
    name = input("Entrez le nom ou identifiant de l'utilisateur : ").strip()
    return name.replace(" ", "_")

def ask_consent(name):
    """Demande le consentement de l'utilisateur"""
    consent = input(f"L'utilisateur {name} donne-t-il son consentement pour l'utilisation de ses données faciales ? (oui/non) : ")
    return consent.lower() == "oui"

def save_consent(name):
    """Enregistre le consentement dans un fichier CSV"""
    header = ["nom_utilisateur", "date_consentement", "consentement_donne"]
    dir_name = os.path.dirname(CONSENT_FILE)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    file_exists = os.path.isfile(CONSENT_FILE)
    with open(CONSENT_FILE, "a", newline='') as f:
        writer = csv.writer(f, delimiter=';')
        if not file_exists:
            writer.writerow(header)  # ajouter l'en-tête si le fichier est nouveau
        writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "oui"])

def capture_images(name):
    """Capture les images du visage de l'utilisateur"""
    user_path = os.path.join(DATASET_DIR, name)
    os.makedirs(user_path, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    count = 0
    
    print(f"Capturer {NUM_IMAGES} images du visage de {name}...")
    while count < NUM_IMAGES:
        ret, frame = cap.read()
        if not ret:
            print("Erreur de capture caméra.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = detect_face(gray)
        
        if face is not None:
            face = preprocess(face)
            filename = os.path.join(user_path, f"{name}_{count}.jpg")
            cv2.imwrite(filename, face)
            count += 1
            print(f"Image {count}/{NUM_IMAGES} capturée.")
            
            cv2.rectangle(frame, (10, 10), (100, 100), (0, 255, 0), 2)
        
        cv2.imshow("Enrôlement utilisateur", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Capture terminée.")

def retrain_model():
    """Réentraîne automatiquement le modèle de reconnaissance faciale"""
    try:
        # Option 1: If Train_Model_SVM is a module with a main function
        Train_Model_SVM.main()
        print(" Modèle réentraîné avec succès.")
    except AttributeError:
        # Option 2: Run the script as a subprocess
        try:
            result = subprocess.run(['python', RETRAIN_SCRIPT], 
                                    capture_output=True, 
                                    text=True, 
                                    check=True)
            print(" Modèle réentraîné avec succès.")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(" Erreur lors du réentraînement du modèle:")
            print(e.stderr)
        except FileNotFoundError:
            print(f" Impossible de trouver le script de réentraînement : {RETRAIN_SCRIPT}")

if __name__ == "__main__":
    # Main enrollment workflow
    name = get_user_name()
    
    # Check if user already exists
    user_path = os.path.join(DATASET_DIR, name)
    if os.path.exists(user_path):
        print(f" L'utilisateur {name} existe déjà. Voulez-vous ajouter plus d'images ?")
        choice = input("Entrez 'oui' pour continuer, 'non' pour annuler : ").lower()
        if choice != 'oui':
            print("Opération annulée.")
            exit()
    
    if ask_consent(name):
        # Save consent
        save_consent(name)
        
        # Capture images
        capture_images(name)
        
        # Automatically retrain the model
        retrain_model()
        
        print(f"L'utilisateur {name} a été enrôlé avec succès.")
    else:
        print("Consentement non donné. Opération annulée.")