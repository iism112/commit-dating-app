const CACHE_NAME = 'commit-pwa-v1';
const ASSETS = [
    '/',
    '/index.html',
    '/login.html',
    '/signup.html',
    '/app.js',
    '/datastore.js',
    '/auth.js',
    '/mockData.js'
];

// Install Event
self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            // Try to cache core assets, but don't fail if some missing
            return cache.addAll(ASSETS).catch(err => console.log('SW Cache Error:', err));
        })
    );
});

// Fetch Event
self.addEventListener('fetch', (e) => {
    // Simple Strategy: Network first, fall back to cache for Pages/JS
    // For API (starts with /api), alway Network
    const url = new URL(e.request.url);

    if (url.pathname.startsWith('/api')) {
        e.respondWith(fetch(e.request));
        return;
    }

    e.respondWith(
        fetch(e.request).catch(() => {
            return caches.match(e.request);
        })
    );
});
