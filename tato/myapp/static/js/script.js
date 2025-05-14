document.addEventListener('DOMContentLoaded', function() {
    // Mise à jour de la date et l'heure en temps réel
    function updateDateTime() {
        const now = new Date();
        const dateElement = document.getElementById('current-date');
        const timeElement = document.getElementById('current-time');
        
        // Formatage de la date (JJ/MM/AAAA)
        const day = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = now.getFullYear();
        dateElement.textContent = `${day}/${month}/${year}`;
        
        // Formatage de l'heure (HH:MM:SS)
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        timeElement.textContent = `${hours}:${minutes}:${seconds}`;
    }
    
    // Mise à jour initiale et toutes les secondes
    updateDateTime();
    setInterval(updateDateTime, 1000);
    
    // Mise à jour des timestamps des caméras
    function updateCameraTimestamps() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const timestamp = `${hours}:${minutes}:${seconds}`;
        
        document.querySelectorAll('.timestamp').forEach(el => {
            el.textContent = timestamp;
        });
    }
    
    setInterval(updateCameraTimestamps, 1000);
    
    // Simulation de détection de mouvement aléatoire
    function simulateMotionDetection() {
        const cameras = document.querySelectorAll('.camera-view:not(.large)');
        cameras.forEach(camera => {
            // 5% de chance de détection de mouvement
            if (Math.random() < 0.05) {
                camera.classList.add('motion-detected');
                setTimeout(() => {
                    camera.classList.remove('motion-detected');
                }, 3000);
                
                // Ajouter une alerte si c'est la caméra de parking
                if (camera.querySelector('span').textContent === 'Parking') {
                    addAlert('Mouvement détecté - Parking', 'fas fa-exclamation-triangle', true);
                }
            }
        });
    }
    
    setInterval(simulateMotionDetection, 10000);
    
    // Ajouter une alerte
    function addAlert(message, icon, isNew = false) {
        const alertsList = document.querySelector('.alerts-list');
        const alertItem = document.createElement('div');
        alertItem.className = `alert-item ${isNew ? 'new' : ''}`;
        
        const now = new Date();
        const minutesAgo = Math.floor(Math.random() * 30) + 1;
        
        alertItem.innerHTML = `
            <i class="${icon}"></i>
            <div class="alert-info">
                <span>${message}</span>
                <small>Il y a ${minutesAgo} minute${minutesAgo > 1 ? 's' : ''}</small>
            </div>
        `;
        
        alertsList.insertBefore(alertItem, alertsList.firstChild);
        
        // Limiter à 10 alertes
        if (alertsList.children.length > 10) {
            alertsList.removeChild(alertsList.lastChild);
        }
    }
    
    // Gestion du mode de surveillance
    const surveillanceMode = document.getElementById('surveillance-mode');
    surveillanceMode.addEventListener('change', function() {
        const body = document.body;
        
        // Retirer toutes les classes de mode précédentes
        body.classList.remove('normal-mode', 'high-alert-mode', 'night-mode');
        
        // Ajouter la classe correspondante au mode sélectionné
        if (this.value === 'high-alert') {
            body.classList.add('high-alert-mode');
            addAlert('Mode Haute Alerte activé', 'fas fa-shield-alt');
        } else if (this.value === 'night') {
            body.classList.add('night-mode');
            addAlert('Mode Nuit activé', 'fas fa-moon');
        } else {
            body.classList.add('normal-mode');
        }
    });
    
    // Gestion de l'interrupteur d'enregistrement
    const recordingToggle = document.getElementById('recording-toggle');
    recordingToggle.addEventListener('change', function() {
        const recordingIndicator = document.querySelector('.recording-indicator');
        if (this.checked) {
            recordingIndicator.style.display = 'flex';
            addAlert('Enregistrement repris', 'fas fa-video');
        } else {
            recordingIndicator.style.display = 'none';
            addAlert('Enregistrement suspendu', 'fas fa-video-slash');
        }
    });
    
    // Gestion de l'interrupteur de détection de mouvement
    const motionToggle = document.getElementById('motion-toggle');
    motionToggle.addEventListener('change', function() {
        if (this.checked) {
            addAlert('Détection de mouvement activée', 'fas fa-running');
        } else {
            addAlert('Détection de mouvement désactivée', 'fas fa-running');
        }
    });
    
    // Gestion du bouton Voir l'historique
    document.getElementById('view-history').addEventListener('click', function() {
        const date = document.getElementById('history-date').value;
        const camera = document.getElementById('history-camera').value;
        
        if (!date) {
            alert('Veuillez sélectionner une date');
            return;
        }
        
        addAlert(`Historique consulté pour ${camera} (${date})`, 'fas fa-history');
    });
    
    // Simulation de clignotement pour les caméras avec mouvement détecté
    setInterval(() => {
        document.querySelectorAll('.motion-detected .camera-feed').forEach(feed => {
            feed.style.boxShadow = feed.style.boxShadow === '0 0 15px rgba(244, 67, 54, 0.7)' 
                ? 'none' 
                : '0 0 15px rgba(244, 67, 54, 0.7)';
        });
    }, 500);
    
    // Définir la date d'aujourd'hui comme valeur par défaut pour l'historique
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('history-date').value = today;
});
// Inside script.js
function updateWebcamFeed() {
    fetch('/webcam/')
        .then(response => response.json())
        .then(data => {
            if (data.image) {
                document.getElementById('webcam-feed').src = `data:image/jpeg;base64,${data.image}`;
            }
        })
        .catch(error => console.error("Error fetching webcam:", error));

    setTimeout(updateWebcamFeed, 100);  // Update every 0.1s (adjust FPS)
}

// Start the feed when the page loads
window.onload = updateWebcamFeed;

function updateCameraMode(mode) {
    fetch('/update_camera_mode/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}',  // Django CSRF token
        },
        body: JSON.stringify({ mode: mode }),
    })
    .then(response => response.json())
    .then(data => console.log("Success:", data))
    .catch(error => console.error("Error:", error));
}
document.addEventListener('DOMContentLoaded', function() {
    // Show/hide custom source input
    const sourceSelect = document.getElementById('id_source');
    const customSource = document.getElementById('id_custom_source');
    
    sourceSelect.addEventListener('change', function() {
        if (this.value === 'rtsp://' || this.value === 'http://') {
            customSource.style.display = 'block';
            customSource.value = this.value;
        } else {
            customSource.style.display = 'none';
            customSource.value = '';
        }
    });
    
    // Test camera connection
    const testBtn = document.getElementById('test-camera');
    const statusIndicator = document.getElementById('connection-status');
    
    testBtn.addEventListener('click', function() {
        const source = sourceSelect.value === 'rtsp://' || sourceSelect.value === 'http://' 
            ? customSource.value 
            : sourceSelect.value;
        
        if (!source) {
            alert('Please select or enter a camera source');
            return;
        }
        
        // Simulate connection test (replace with actual AJAX call)
        statusIndicator.className = 'status-online';
        statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Connecting...';
        
        // This would be replaced with actual fetch request to your backend
        setTimeout(() => {
            statusIndicator.className = 'status-online';
            statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Connection successful!';
            
            // In a real app, you would show the actual camera feed here
            document.getElementById('camera-preview').innerHTML = `
                <div class="preview-placeholder">
                    <i class="fas fa-check-circle"></i>
                    <p>Camera connected successfully</p>
                    <small>Source: ${source}</small>
                </div>
            `;
        }, 1500);
    });
});
document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('webcam-preview');
    const captureBtn = document.getElementById('start-enrollment-btn');
    const statusMessage = document.getElementById('status-message');
    const progressBar = document.getElementById('capture-progress-bar');
    const captureCount = document.getElementById('capture-count');
    
    let stream = null;
    let captureInterval = null;
    let imagesCaptured = 0;
    const totalImages = 20;
    
    // Start webcam
    async function startWebcam() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.addEventListener('loadedmetadata', () => {
    captureBtn.disabled = false;
});

        } catch (err) {
            showError('Could not access webcam: ' + err.message);
        }
    }
    
    // Capture image
    async function captureImage() {
        if (imagesCaptured >= totalImages) return;
        
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        
        const imageData = canvas.toDataURL('image/jpeg');
        const blob = await (await fetch(imageData)).blob();
        
        const formData = new FormData();
        formData.append('username', document.getElementById('username').value);
        formData.append('image', blob, 'capture.jpg');
        
        try {
            const response = await fetch('/api/enroll/', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                imagesCaptured++;
                updateProgress();
                
                if (imagesCaptured >= totalImages) {
                    completeEnrollment();
                }
            } else {
                showError(data.message);
            }
        } catch (err) {
            showError('Capture failed: ' + err.message);
        }
    }
    
    // Update progress
    function updateProgress() {
        progressBar.value = imagesCaptured;
        captureCount.textContent = `${imagesCaptured}/${totalImages}`;
    }
    
    // Complete enrollment
    function completeEnrollment() {
        clearInterval(captureInterval);
        statusMessage.textContent = 'Enrollment complete! Training model...';
        statusMessage.classList.add('status-success');
        
        // Call retraining endpoint
        fetch('/api/retrain/', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                statusMessage.textContent = 'Enrollment and training completed successfully!';
            } else {
                showError('Training failed: ' + data.message);
            }
        })
        .catch(err => {
            showError('Training request failed: ' + err.message);
        });
    }
    
    // Show error
    function showError(message) {
        statusMessage.textContent = message;
        statusMessage.classList.add('status-error');
        clearInterval(captureInterval);
        captureBtn.disabled = false;
    }
    
    // Start enrollment
    captureBtn.addEventListener('click', () => {
        if (!stream) {
            showError('Webcam not ready');
            return;
        }
        
        captureBtn.disabled = true;
        imagesCaptured = 0;
        updateProgress();
        
        statusMessage.textContent = 'Starting enrollment...';
        statusMessage.classList.remove('status-error', 'status-success');
        
        // Capture every 500ms until we have enough images
        captureInterval = setInterval(captureImage, 500);
    });
    
    // Initialize
    startWebcam();
});

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const video = document.getElementById('video-feed');
    const canvas = document.getElementById('face-canvas');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const confidenceBar = document.getElementById('confidence-bar');
    const confidenceValue = document.getElementById('confidence-value');
    const identityValue = document.getElementById('identity-value');
    const confidenceDisplay = document.getElementById('confidence-value-display');
    const accessValue = document.getElementById('access-value');
    
    // Variables
    let stream = null;
    let recognitionInterval = null;
    let faceBox = null;
    let faceLabel = null;
    
    // Send captured frame to server for recognition
    async function sendFrameForRecognition(blob) {
        const formData = new FormData();
        formData.append('frame', blob);
        
        try {
            const response = await fetch('/recognize/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Recognition error:', error);
            return {
                error: error.message,
                face_detected: false
            };
        }
    }
    
    // Create face detection elements
    function createDetectionElements() {
        // Only create if they don't already exist
        if (!faceBox) {
            faceBox = document.createElement('div');
            faceBox.className = 'face-box';
            document.querySelector('.video-container').appendChild(faceBox);
        }
        
        if (!faceLabel) {
            faceLabel = document.createElement('div');
            faceLabel.className = 'face-label';
            document.querySelector('.video-container').appendChild(faceLabel);
        }
    }
    
    // Update face detection box
    function updateFaceBox(x, y, width, height, label, confidence, isRecognized) {
        const videoContainer = document.querySelector('.video-container');
        
        faceBox.style.display = 'block';
        faceBox.style.left = `${x}px`;
        faceBox.style.top = `${y}px`;
        faceBox.style.width = `${width}px`;
        faceBox.style.height = `${height}px`;
        faceBox.className = isRecognized ? 'face-box recognized' : 'face-box unknown';
        
        faceLabel.style.display = 'block';
        faceLabel.style.left = `${x}px`;
        faceLabel.style.top = `${y + height}px`;
        faceLabel.textContent = `${label} (${Math.round(confidence * 100)}%)`;
        faceLabel.className = isRecognized ? 'face-label recognized' : 'face-label unknown';
    }
    
    // Hide face detection elements
    function hideDetectionElements() {
        if (faceBox) faceBox.style.display = 'none';
        if (faceLabel) faceLabel.style.display = 'none';
    }
    
    // Start video stream
    async function startVideoStream() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user' 
                } 
            });
            video.srcObject = stream;
            
            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusIndicator.className = 'status-indicator active';
            statusText.textContent = 'Reconnaissance active';
            
            createDetectionElements();
            startRecognition();
        } catch (error) {
            console.error('Error accessing camera:', error);
            statusIndicator.className = 'status-indicator error';
            statusText.textContent = 'Erreur de caméra';
        }
    }
    
    // Stop video stream
    function stopVideoStream() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        
        if (recognitionInterval) {
            clearInterval(recognitionInterval);
            recognitionInterval = null;
        }
        
        startBtn.disabled = false;
        stopBtn.disabled = true;
        statusIndicator.className = 'status-indicator inactive';
        statusText.textContent = 'En veille';
        
        hideDetectionElements();
        resetResults();
    }
    
    // Reset result displays
    function resetResults() {
        confidenceBar.style.width = '0%';
        confidenceValue.textContent = '0%';
        confidenceDisplay.textContent = '0%';
        identityValue.textContent = 'Inconnu';
        accessValue.textContent = 'En attente...';
        accessValue.className = 'value';
    }
    
    // Start face recognition
    function startRecognition() {
        recognitionInterval = setInterval(async () => {
            if (!stream) return;
            
            try {
                // Capture frame from video
                const context = canvas.getContext('2d');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                // Convert to blob and send to server
                canvas.toBlob(async (blob) => {
                    const result = await sendFrameForRecognition(blob);
                    updateRecognitionResult(result);
                }, 'image/jpeg', 0.8);
            } catch (error) {
                console.error('Frame processing error:', error);
            }
        }, 500); // Process every 500ms - adjust for performance
    }
    
    // Update UI with recognition results
    function updateRecognitionResult(result) {
        if (result.error) {
            statusIndicator.className = 'status-indicator error';
            statusText.textContent = 'Erreur de reconnaissance';
            hideDetectionElements();
            return;
        }

        const confidence = result.confidence || 0;
        const confidencePercent = Math.round(confidence * 100);
        
        // Update confidence indicators
        confidenceBar.style.width = `${confidencePercent}%`;
        confidenceValue.textContent = `${confidencePercent}%`;
        confidenceDisplay.textContent = `${confidencePercent}%`;
        
        // Color coding based on confidence
        if (confidence < 0.3) {
            confidenceBar.className = 'confidence-bar low';
        } else if (confidence < 0.6) {
            confidenceBar.className = 'confidence-bar medium';
        } else {
            confidenceBar.className = 'confidence-bar high';
        }
        
        // Update identity and access status
        identityValue.textContent = result.identity || 'Inconnu';
        accessValue.textContent = result.access || 'Accès non déterminé';
        
        // Set access status styling
        if (result.access === "Accès autorisé") {
            accessValue.className = 'value access-granted';
        } else if (result.access === "Accès refusé") {
            accessValue.className = 'value access-denied';
        } else {
            accessValue.className = 'value';
        }
        
        // Update face detection box if face detected
        if (result.face_detected) {
            // Calculate relative coordinates for the video container
            const videoContainer = document.querySelector('.video-container');
            const videoRect = videoContainer.getBoundingClientRect();
            const scaleX = videoRect.width / video.videoWidth;
            const scaleY = videoRect.height / video.videoHeight;
            
            updateFaceBox(
                result.face_x * scaleX,
                result.face_y * scaleY,
                result.face_width * scaleX,
                result.face_height * scaleY,
                result.identity || 'Inconnu',
                confidence,
                confidence > 0.3
            );
            
            // Update status indicator
            statusIndicator.className = 'status-indicator active';
            statusText.textContent = confidence > 0.3 ? 'Visage reconnu' : 'Visage non reconnu';
        } else {
            hideDetectionElements();
            statusIndicator.className = 'status-indicator scanning';
            statusText.textContent = 'Recherche de visage...';
        }
    }
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Event listeners
    startBtn.addEventListener('click', startVideoStream);
    stopBtn.addEventListener('click', stopVideoStream);
    
    // Clean up on page exit
    window.addEventListener('beforeunload', stopVideoStream);
    
    // Initialize UI state
    statusIndicator.className = 'status-indicator inactive';
    statusText.textContent = 'En veille';
    resetResults();
});