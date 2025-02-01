chrome.alarms.create("postureReminder", { periodInMinutes: 20 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "postureReminder") {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icon.png",
      title: "Posture Check!",
      message: "Time to check your posture! Open the extension to verify."
    });
  }
});