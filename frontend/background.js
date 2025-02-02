chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create("postureReminder", { periodInMinutes: 20 });
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "postureReminder") {
      chrome.notifications.create("postureReminderNotification", {
          type: "basic",
          iconUrl: chrome.runtime.getURL("frontend/warning_icon.png"), // Ensure the icon is correctly referenced
          title: "Posture Check!",
          message: "Time to check your posture! Open the extension to verify.",
          priority: 2
      }, (notificationId) => {
          if (chrome.runtime.lastError) {
              console.error(chrome.runtime.lastError);
          } else {
              console.log("Notification sent!", notificationId);
          }
      });
  }
});

