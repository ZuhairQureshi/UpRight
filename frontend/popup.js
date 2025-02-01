document.addEventListener('DOMContentLoaded', function() {
  // Request camera access when the page loads
  document.getElementById('requestCamera').addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function(stream) {
        const videoElement = document.getElementById('camera');
        videoElement.srcObject = stream;
        videoElement.play();
        document.getElementById('status').innerText = "Camera on. Ready for posture analysis!";
        document.getElementById('start').disabled = true; // Disable 'start' button, as it's no longer needed
        startPostureAnalysis(); // Start continuous posture analysis when camera is on
      })
      .catch(function(error) {
        console.error('Error accessing the camera:', error);
        document.getElementById('status').innerText = "Camera access denied. Please allow camera access in settings.";
      });
  });

  // Function to analyze posture continuously
  function startPostureAnalysis() {
    const videoElement = document.getElementById('camera');

    // Function to analyze posture from the camera stream
    async function analyzePosture() {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = videoElement.videoWidth;
      canvas.height = videoElement.videoHeight;
      context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

      const imageData = canvas.toDataURL('image/png'); // Convert to image data for analysis

      try {
        const response = await fetch('http://127.0.0.1:5000/analyze_posture', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: imageData })
        });

        if (!response.ok) throw new Error('Failed to fetch posture analysis');

        const result = await response.json();
        document.getElementById('status').innerText = result.status || 'No status received from backend';
      } catch (error) {
        console.error('Error during posture analysis:', error);
        document.getElementById('status').innerText = 'Error during posture analysis. Please try again.';
      }
    }

    // Analyze posture every 1000ms (1 second)
    setInterval(analyzePosture, 1000);
  }
});


/*document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('requestCamera').addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function(stream) {
        const videoElement = document.getElementById('camera');
        videoElement.srcObject = stream;
        videoElement.play();
        document.getElementById('status').innerText = "Camera on. Ready for posture analysis!";
        document.getElementById('start').disabled = false;
      })
      .catch(function(error) {
        console.error('Error accessing the camera:', error);
        document.getElementById('status').innerText = "Camera access denied. Please allow camera access in settings.";
      });
  });

  document.getElementById('start').addEventListener('click', async () => {
    const videoElement = document.getElementById('camera');
    document.getElementById('status').innerText = "Camera on. Analyzing posture...";

    // Function to analyze posture from the camera stream
    async function analyzePosture() {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = videoElement.videoWidth;
      canvas.height = videoElement.videoHeight;
      context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

      const imageData = canvas.toDataURL('image/png'); // Convert to image data for analysis

      try {
        const response = await fetch('http://127.0.0.1:5000/analyze_posture', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: imageData })
        });

        if (!response.ok) throw new Error('Failed to fetch posture analysis');

        const result = await response.json();
        document.getElementById('status').innerText = result.status || 'No status received from backend';
      } catch (error) {
        console.error('Error during posture analysis:', error);
        document.getElementById('status').innerText = 'Error during posture analysis. Please try again.';
      }
    }

    if (videoElement.readyState >= videoElement.HAVE_ENOUGH_DATA) {
      analyzePosture(); // Analyze when enough data is available
    } else {
      videoElement.onplaying = analyzePosture; // Wait for video to start playing
    }
  });
});*/
