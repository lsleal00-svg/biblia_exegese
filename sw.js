/* Service worker: permite instalar o app e abre mais rápido.
   Páginas, scripts e estilos: rede primeiro (as atualizações chegam logo); dados do livro, imagens e bibliotecas: cache primeiro. */
const VERSAO = 'exegese-v5';
const BASICO = ['./', 'index.html', 'css/app.css', 'js/config.js', 'js/livros.js', 'js/dados.js', 'js/mapa.js', 'js/instalar.js', 'js/app.js',
  'vendor/leaflet/leaflet.css', 'vendor/leaflet/leaflet.js', 'vendor/gsap.min.js', 'img/logo-64.png', 'img/logo-192.png', 'manifest.webmanifest'];

self.addEventListener('install', (ev) => {
  ev.waitUntil(caches.open(VERSAO).then(c => c.addAll(BASICO)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (ev) => {
  ev.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSAO).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (ev) => {
  const req = ev.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;            // Supabase, mapas e fontes vão direto à rede
  const fixo = /\/(data|img|vendor)\//.test(url.pathname);
  if (fixo) {
    ev.respondWith(caches.match(req).then(r => r || fetch(req).then(resp => {
      if (resp.ok) { const copia = resp.clone(); caches.open(VERSAO).then(c => c.put(req, copia)); }
      return resp;
    })));
  } else {
    ev.respondWith(fetch(req).then(resp => {
      if (resp.ok) { const copia = resp.clone(); caches.open(VERSAO).then(c => c.put(req, copia)); }
      return resp;
    }).catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match('index.html'))));
  }
});
