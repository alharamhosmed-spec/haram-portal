/* نمط التطبيق — Service Worker
 * يخزّن الغلاف فقط (الواجهة والأيقونات) عشان التطبيق يفتح بسرعة ويعرض شاشة «لا يوجد اتصال».
 * لا يخزّن أي بيانات من Google Apps Script — البيانات دائماً مباشرة من السيرفر.
 * عند أي تعديل على ملفات الغلاف: زِد رقم VERSION.
 */
'use strict';
var VERSION = 'haram-portal-v1.0.0';
var SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-32.png'
];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(SHELL); }).then(function () { return self.skipWaiting(); }));
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
      fetch(req).then(function (res) {
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
