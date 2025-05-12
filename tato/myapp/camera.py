import cv2
import threading
import numpy as np
from django.core.cache import cache

class CameraStream:
    def __init__(self, source):
        self.source = source
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.thread = None
        self.current_mode = 'normal'

    def start(self):
        """Start the camera capture thread"""
        if not self.running:
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                raise RuntimeError(f"Could not open camera source: {self.source}")
            
            self.running = True
            self.thread = threading.Thread(target=self._update_frame, daemon=True)
            self.thread.start()

    def _update_frame(self):
        """Thread function to continuously capture frames"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = self._process_frame(frame)
            else:
                break

    def _process_frame(self, frame):
        """Apply processing based on current mode"""
        mode = cache.get('global_camera_mode', 'normal')
        
        if mode == 'high-alert':
            frame = cv2.Canny(frame, 100, 200)
        elif mode == 'night':
            frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=20)
        
        # Add timestamp overlay
        cv2.putText(frame, f"Mode: {mode}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return frame

    def get_frame(self):
        """Get the latest processed frame"""
        with self.lock:
            if self.frame is not None:
                _, jpeg = cv2.imencode('.jpg', self.frame)
                return jpeg.tobytes()
        return None

    def stop(self):
        """Stop the camera stream"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            if self.cap:
                self.cap.release()

class CameraManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.streams = {}
            cls._instance.lock = threading.Lock()
        return cls._instance
    
    def get_stream(self, source):
        """Get or create a camera stream"""
        with self.lock:
            if source not in self.streams:
                stream = CameraStream(source)
                stream.start()
                self.streams[source] = stream
            return self.streams[source]
    
    def cleanup(self):
        """Clean up all camera resources"""
        with self.lock:
            for source, stream in self.streams.items():
                stream.stop()
            self.streams.clear()

# Global camera manager instance
camera_manager = CameraManager()