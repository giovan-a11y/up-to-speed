// Offline support: the app shell and all topic content are cached on install.
// Pages and data are fetched fresh when online (so weekly updates arrive) and
// served from the cache when offline.
const VERSION = "5b3d1be3915d";
const CACHE = "uts-" + VERSION;
const SHELL = ["./", "index.html", "data/bundle.json", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL.map((u) => new Request(u, { cache: "reload" })))).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k.startsWith("uts-") && k !== CACHE && k !== "uts-fonts" && k !== "uts-img").map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // Google Fonts: cache-first so the typography also works offline.
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(caches.open("uts-fonts").then(async (c) => {
      const hit = await c.match(req);
      if (hit) return hit;
      try { const res = await fetch(req); if (res.ok || res.type === "opaque") c.put(req, res.clone()); return res; }
      catch { return new Response("", { status: 504 }); }
    }));
    return;
  }
  // Wikimedia pictures: cache-first so pictures you've seen also work offline.
  if (url.hostname === "upload.wikimedia.org") {
    e.respondWith(caches.open("uts-img").then(async (c) => {
      const hit = await c.match(req, { ignoreVary: true }) || await c.match(req.url, { ignoreVary: true });
      if (hit) return hit;
      try { const res = await fetch(req); if (res.ok || res.type === "opaque") c.put(req.url, res.clone()); return res; }
      catch { return new Response("", { status: 504 }); }
    }));
    return;
  }
  if (url.origin !== location.origin) return;

  // Same origin: network first (3s timeout), then cache.
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const key = req.mode === "navigate" ? "index.html" : req;
    try {
      const res = await Promise.race([fetch(req), new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), 3000))]);
      if (res.ok) cache.put(key, res.clone());
      return res;
    } catch {
      return (await cache.match(key, { ignoreSearch: true })) || (await cache.match("index.html")) || new Response("Offline", { status: 503 });
    }
  })());
});
