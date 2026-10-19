/* نمط التطبيق — Service Worker
 * يخزّن الغلاف فقط (الواجهة والأيقونات) عشان التطبيق يفتح بسرعة ويعرض شاشة «لا يوجد اتصال».
 * لا يخزّن أي بيانات من Google Apps Script — البيانات دائماً مباشرة من السيرفر.
 * عند أي تعديل على ملفات الغلاف: زِد رقم VERSION.
 */
'use strict';
var VERSION = 'naqaa-v1.0.2';
var SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './apple-touch-icon.png',
  './favicon-32.png'
];

self.addEventListener('install', function (e) {
  // كل ملف لحاله: لو ملف واحد ناقص (مثلاً أيقونة) ما يفشل تثبيت الـ Service Worker كله
  e.waitUntil(
    caches.open(VERSION).then(function (c) {
      return Promise.all(SHELL.map(function (u) { return c.add(u).catch(function () {}); }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== VERSION; }).map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // Google وغيره: بدون تدخل

  // صفحة الغلاف: الشبكة أولاً (عشان التحديثات توصل) ثم النسخة المخزنة
  if (req.mode === 'navigate') {
    e.respondWith(
      // no-cache: يتجاوز كاش المتصفح (GitHub Pages يخزّن الصفحات 10 دقائق) فيوصل أي تعديل فوراً
      fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' }).then(function (res) {
        if (!res || !res.ok) throw new Error('bad');
        var copy = res.clone();
        caches.open(VERSION).then(function (c) { c.put('./index.html', copy); });
        return res;
      }).catch(function () {
        return caches.match('./index.html').then(function (r) { return r || caches.match('./'); });
      })
    );
    return;
  }

  // الأيقونات والملفات الثابتة: المخزن أولاً
  e.respondWith(
    caches.match(req).then(function (hit) {
      return hit || fetch(req).then(function (res) {
        if (res && res.ok) {
          var copy = res.clone();
          caches.open(VERSION).then(function (c) { c.put(req, copy); });
        }
        return res;
      });
    })
  );
});
