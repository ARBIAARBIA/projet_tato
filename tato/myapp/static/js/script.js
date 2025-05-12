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