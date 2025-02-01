document.addEventListener('DOMContentLoaded', function(){
  document.getElementById('requestCamera').addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({video: true})
      .then(function(stream) {
        const videoElement = document.getElementById('camera');
        videoElement.srcObject = stream;
        document.getElementById('status').innerText = "Camera on. Ready for posture analysis!";
      })
      .catch(function(error) {
        console.error('Error accessing the camera: ', error);
        document.getElementById('status').innerText = "Camera access denied";
      });
  });
  
  document.getElementById('start').addEventListener('click', async () => {
    const video = document.getElementById('camera');
    if (!video.srcObject) {
      document.getElementById('status').innerText = "Please enable camera access first.";
      return;
    }
  
    // Simulate posture analysis
    document.getElementById('status').innerText = "Camera on. Analyzing posture...";
  
    // Placeholder for AI-based posture analysis
    setTimeout(() => {
      document.getElementById('status').innerText = "Posture looks good!";
    }, 3000);
  });

});


/*document.getElementById("start").addEventListener("click", async () => {
    const video = document.getElementById("camera");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      document.getElementById("status").innerText = "Camera on. Analyzing posture...";
      // Placeholder for AI-based posture analysis
      setTimeout(() => {
        document.getElementById("status").innerText = "Posture looks good!";
      }, 3000);
    } catch (error) {
      document.getElementById("status").innerText = "Camera access denied!";
    }
  });*/