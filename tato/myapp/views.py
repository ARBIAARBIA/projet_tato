from django.shortcuts import render , HttpResponse
from .models import user
import cv2
import base64
from django.http import JsonResponse , StreamingHttpResponse
from django.views.decorators import gzip
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Camera, CameraLog
from .forms import CameraForm
import cv2
import logging
from django.core.cache import cache
from .camera import camera_manager
import numpy as np 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import cv2
import numpy as np
from datetime import datetime
import uuid
from django.views.decorators.http import require_POST
logger = logging.getLogger(__name__)
from .models import RecognitionHistory, UserProfile

@csrf_exempt
def update_camera_mode(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mode = data.get('mode', 'normal')
            if mode not in ['normal', 'high-alert', 'night']:
                return JsonResponse({'status': 'error', 'message': 'Invalid mode'}, status=400)
            
            cache.set('global_camera_mode', mode, timeout=None)
            return JsonResponse({'status': 'success', 'mode': mode})
        except Exception as e:
            logger.error(f"Mode update error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)






def generate_frames(source=0):
    """Generate frames for streaming response"""
    try:
        stream = camera_manager.get_stream(source)
        while True:
            frame = stream.get_frame()
            if frame:
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + 
                      get_error_frame() + b'\r\n')
    except Exception as e:
        logger.error(f"Stream generation error: {str(e)}")
        yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + 
              get_error_frame() + b'\r\n')



@require_http_methods(["GET"])
def webcam_stream(request):
    source = request.GET.get('source', '0')  # récupère "source" depuis l'URL
    try:
        source = int(source)  # tente de le convertir en int
    except ValueError:
        pass  # sinon c'est une URL ou chemin
    return StreamingHttpResponse(
        generate_frames(source),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


def webcam_view(request):
    return render(request, 'camera.html')

def add_camera(request):
    if request.method == 'POST':
        form = CameraForm(request.POST)
        if form.is_valid():
            try:
                camera = form.save()
                if test_camera_connection(camera.source):
                    CameraLog.objects.create(camera=camera, status='online')
                    messages.success(request, "Camera added successfully!")
                else:
                    CameraLog.objects.create(camera=camera, status='offline')
                    messages.warning(request, "Camera added but connection failed")
                return redirect('webcam_stream')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                logger.error(f"Camera addition failed: {str(e)}")
    else:
        form = CameraForm()
    return render(request, 'addcamera.html', {'form': form})

def test_camera_connection(source):
    """Test if camera source is accessible"""
    cap = None
    try:
        cap = cv2.VideoCapture(source)
        if cap.isOpened():
            # Test actual frame capture
            ret, _ = cap.read()
            return ret
        return False
    except Exception as e:
        logger.error(f"Camera test failed: {str(e)}")
        return False
    finally:
        if cap is not None:
            cap.release()
def get_error_frame():
    """Generate an error frame when camera fails"""
    try:
        # Try to load error image if exists
        frame = cv2.imread('static/images/camera_error.jpg')
        if frame is None:
            raise FileNotFoundError
    except:
        # Create blank error frame if no image found
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "CAMERA ERROR", (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()
def camera_preview(request):
    """Endpoint for live camera preview during setup"""
    source = request.GET.get('source', '0')
    
    def generate_preview():
        cap = cv2.VideoCapture(source)
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        finally:
            cap.release()
    
    return StreamingHttpResponse(
        generate_preview(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def enrollment_view(request):
    access_options = [
        {'value': 'main', 'label': 'Entrée Principale'},
        {'value': 'hr', 'label': 'Ressources Humaines'},
        {'value': 'it', 'label': 'Informatique'},
        {'value': 'finance', 'label': 'Finance'},
        {'value': 'legal', 'label': 'Service Juridique'},
    ]
    
    consent_options = [
        {'value': 'read', 'label': 'J\'ai lu et compris les conditions'},
        {'value': 'data', 'label': 'Je consens à l\'utilisation de mes données pour authentification'},
        {'value': 'delete', 'label': 'Je comprends mon droit à la suppression des données'},
    ]
    
    return render(request, 'enrollment.html', {
        'access_options': access_options,
        'consent_options': consent_options,
    })

@csrf_exempt
def enroll_api(request):
    if request.method == 'POST':
        try:
            # Get data from request
            username = request.POST.get('username')
            image_data = request.FILES.get('image')
            
            # Create unique directory for user
            user_dir = os.path.join('dataset', username)
            os.makedirs(user_dir, exist_ok=True)
            
            # Process image
            img_array = np.fromstring(image_data.read(), np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) > 0:
                x, y, w, h = [int(i) for i in faces[0]]
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (64, 64))
                face = cv2.equalizeHist(face)
                
                # Save image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{username}_{timestamp}_{str(uuid.uuid4())[:8]}.jpg"
                cv2.imwrite(os.path.join(user_dir, filename), face)
                
                return JsonResponse({'status': 'success', 'message': 'Face captured successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No face detected'}, status=400)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def retrain_api(request):
    if request.method == 'POST':
        try:
            # Call your training script
            from myapp.scripts.Train_Model_SVM import main

            main()
            
            return JsonResponse({'status': 'success', 'message': 'Model retrained successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


import cv2
import numpy as np
import joblib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from skimage.feature import hog
import tempfile
import joblib



model = joblib.load(os.path.join(settings.BASE_DIR, 'models', 'face_recognition_model.pkl'))
label_dict = joblib.load(os.path.join(settings.BASE_DIR, 'models','label_dict.pkl'))

print("Model path:", os.path.join(settings.BASE_DIR, 'models', 'face_recognition_model.pkl'))
def detect_face(image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
        x, y, w, h = [int(i) for i in faces[0]]

        return image[y:y+h, x:x+w], (x, y, w, h)
    return None, None

# Preprocess the face for recognition
def preprocess(face):
    face = cv2.resize(face, (64, 64))
    face = cv2.equalizeHist(face)
    return face / 255.0

# Extract HOG features
def extract_hog_features(image):
    return hog(image, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True)

@csrf_exempt
def recognize_face(request):
    if request.method == 'POST' and request.FILES.get('frame'):
        try:
            # Save uploaded frame to temp file
            frame_file = request.FILES['frame']
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp:
                for chunk in frame_file.chunks():
                    temp.write(chunk)
                temp_path = temp.name

            # Process the image
            image = cv2.imread(temp_path, cv2.IMREAD_GRAYSCALE)
            os.unlink(temp_path)  # Delete temp file
            
            if image is None:
                return JsonResponse({'error': 'Invalid image'}, status=400)

            # Face detection
            face, coords = detect_face(image)
            print("Detected coords:", coords)

            if face is not None and coords is not None:
                # Preprocess and extract features
                face_proc = preprocess(face)
                features = extract_hog_features(face_proc).reshape(1, -1)

                # Predict
                prediction = model.predict(features)
                probabilities = model.predict_proba(features)
                confidence = probabilities.max()
                predicted_label = int(prediction[0])

                if confidence > 0.3:  # Confidence threshold
                    identity = label_dict.get(prediction[0], "Inconnu")
                    access = "Accès autorisé"  
                    print("Prediction:", prediction)
                    print("Prediction type:", type(prediction[0]))

                else:
                    identity = "Inconnu"
                    access = "Accès refusé"
                user_obj = UserProfile.objects.filter(face_label=predicted_label).first() if identity != "Inconnu" else None

                if user_obj or identity == "Inconnu":
                    RecognitionHistory.objects.create(
                        user=user_obj,
                        recognized=(identity != "Inconnu"),
                        confidence=confidence,
                        camera_source="webcam"
                    )


                x, y, w, h = coords
                return JsonResponse({
                    'face_detected': True,
                    'face_x': x,
                    'face_y': y,
                    'face_width': w,
                    'face_height': h,
                    'identity': identity,
                    'confidence': float(confidence),
                    'access': access
                })
            else:
                return JsonResponse({
                    'face_detected': False,
                    'message': 'No face detected'
                })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
 


def get_access_rights(identity):
    """Implement your access rights logic here"""
    # Example: Check database for user access rights
    return "Accès autorisé" if identity != "Inconnu" else "Accès refusé"
def recognition_view(request):
    return render(request, 'recognition.html')

from django.shortcuts import render
from .models import RecognitionHistory

def recognition_history_view(request):
    history = RecognitionHistory.objects.select_related('user').order_by('-timestamp')[:100]  # les 100 derniers
    return render(request, 'recognition_history.html', {'history': history})
