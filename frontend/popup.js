document.getElementById("start").addEventListener("click", async () => {
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
  });