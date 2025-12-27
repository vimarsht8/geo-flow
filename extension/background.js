// background.js
console.log("GEO FLOW service worker running");

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type !== "PAGE_SIGNAL") return;

  // 🔔 Notification
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icon.png",
    title: "Data Flow Detected",
    message: msg.page
  });

  // 🌍 Send to backend
  fetch("http://127.0.0.1:8000/track", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      page: msg.page,
      resources: msg.resources,
      timestamp: Date.now()
    })
  }).catch(() => {});
});

// click notification → dashboard
chrome.notifications.onClicked.addListener(() => {
  chrome.tabs.create({
    url: "http://127.0.0.1:8000/dashboard"
  });
});
