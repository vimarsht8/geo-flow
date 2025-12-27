// content.js
(() => {
  if (window.__GEOFLOW__) return;
  window.__GEOFLOW__ = true;

  const page = location.hostname;
  if (
    !page ||
    page.startsWith("chrome") ||
    page.includes("localhost") ||
    page.includes("127.0.0.1")
  ) return;

  // collect resource domains (MV3-legal)
  const scripts = [...document.scripts]
    .map(s => {
      try { return new URL(s.src).hostname } catch { return null }
    })
    .filter(Boolean);

  const links = [...document.querySelectorAll("link[href]")]
    .map(l => {
      try { return new URL(l.href).hostname } catch { return null }
    })
    .filter(Boolean);

  const images = [...document.images]
    .map(i => {
      try { return new URL(i.src).hostname } catch { return null }
    })
    .filter(Boolean);

  const resources = [...new Set([...scripts, ...links, ...images])];

  chrome.runtime.sendMessage({
    type: "PAGE_SIGNAL",
    page,
    resources
  });
})();
