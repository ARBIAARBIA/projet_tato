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
logger = logging.getLogger(__name__)

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