/* AggieCare service worker for the GitHub Pages project path. */
const PREFIX = "/AggieCareweb/";
const CACHE = "aggie-care-github-pages-v23";
const SHELL = PREFIX + "index.html";
const CORE = [SHELL, PREFIX + "manifest.webmanifest", PREFIX + "icon-192.png", PREFIX + "icon-512.png", PREFIX + "apple-touch-icon.png", PREFIX + "campus-map-2021-22.jpg", PREFIX + "test-poster-1.jpeg"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith("aggie-care-") && key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener("message", event => { if (event.data === "SKIP_WAITING") self.skipWaiting(); });
async function trim(cache, limit = 80) {
  const keys = await cache.keys();
  if (keys.length > limit) await Promise.all(keys.slice(0, keys.length - limit).map(key => cache.delete(key)));
}
self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin || !url.pathname.startsWith(PREFIX)) return;
  if (request.mode === "navigate") {
    event.respondWith(fetch(request).then(async response => {
      if (response.ok) { const cache = await caches.open(CACHE); await cache.put(SHELL, response.clone()); }
      return response;
    }).catch(async () => (await caches.match(SHELL)) || new Response("Aggie Care is offline. Reconnect once to open the guide.", {status: 503, headers: {"content-type": "text/plain; charset=utf-8"}})));
    return;
  }
  if (request.destination === "script" || request.destination === "style") {
    event.respondWith(fetch(request).then(async response => {
      if (response.ok) {const cache = await caches.open(CACHE); await cache.put(request, response.clone()); await trim(cache);}
      return response;
    }).catch(() => caches.match(request)));
    return;
  }
  event.respondWith(caches.match(request).then(cached => cached || fetch(request).then(async response => {
    if (response.ok) { const cache = await caches.open(CACHE); await cache.put(request, response.clone()); await trim(cache); }
    return response;
  })));
});
