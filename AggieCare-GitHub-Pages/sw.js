const CACHE = "aggie-care-v22";
const CORE = ["/", "/manifest.webmanifest", "/icon-192.png", "/icon-512.png", "/apple-touch-icon.png", "/campus-map-2021-22.jpg", "/test-poster-1.jpeg"];
self.addEventListener("install", (event) => event.waitUntil(Promise.all([caches.open(CACHE).then((cache) => cache.addAll(CORE)), self.skipWaiting()])));
self.addEventListener("activate", (event) => event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))))));
self.addEventListener("message", (event) => { if (event.data === "SKIP_WAITING") self.skipWaiting(); });
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));
async function trim(cache, limit = 40) { const keys = await cache.keys(); if (keys.length > limit) await Promise.all(keys.slice(0, keys.length - limit).map((key) => cache.delete(key))); }
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET" || new URL(event.request.url).origin !== self.location.origin) return;
  if (event.request.mode === "navigate") { event.respondWith(fetch(event.request).then(async (response) => { if (response.ok) { const cache = await caches.open(CACHE); await cache.put("/app-shell", response.clone()); await trim(cache); } return response; }).catch(async () => (await caches.match("/app-shell")) || new Response("Aggie Care is offline. Reconnect once to open the guide.", { status: 503, headers: { "content-type": "text/plain; charset=utf-8" } }))); return; }
  if (event.request.destination === "script" || event.request.destination === "style") { event.respondWith(fetch(event.request).then(async (response) => { if (response.ok) { const cache = await caches.open(CACHE); await cache.put(event.request, response.clone()); await trim(cache); } return response; }).catch(() => caches.match(event.request))); return; }
  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request).then(async (response) => { if (response.ok) { const cache = await caches.open(CACHE); await cache.put(event.request, response.clone()); await trim(cache); } return response; })));
});
