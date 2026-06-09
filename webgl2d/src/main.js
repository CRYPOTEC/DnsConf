import { Renderer, Scene, Controls, FontAtlas } from './lib/index.js';

// --- параметры демо ---
const OBJECT_COUNT = 3000;
const FIELD_W = 6400;
const FIELD_H = 4200;

const canvas = document.getElementById('view');
const loading = document.getElementById('loading');
const renderer = new Renderer(canvas);

// Тяжёлую работу (генерация SDF-атласа + сцены) запускаем после первой
// отрисовки, чтобы успел показаться экран загрузки.
requestAnimationFrame(() => requestAnimationFrame(start));

let fitZoom = 1;

function start() {
  // 1. Набор символов: латиница, цифры, пунктуация и кириллица.
  let charset = '';
  for (let i = 32; i < 127; i++) charset += String.fromCharCode(i);
  for (let i = 0x0410; i <= 0x044f; i++) charset += String.fromCharCode(i);
  charset += 'Ёё·•—–…«»№°×→';

  // 2. SDF-атлас шрифта.
  const atlas = new FontAtlas({ fontSize: 46, padding: 8, fontWeight: 600 }).build(charset);

  // 3. Сцена.
  const scene = new Scene(renderer, atlas);

  // Крупные заголовки прямо в мире (резкие на любом зуме благодаря SDF).
  scene.addText(0, -FIELD_H / 2 - 230, 'WebGL · 2D', 360, [0.86, 0.93, 1.0, 1], 'center');
  scene.addText(
    0, -FIELD_H / 2 + 30,
    'зум · drag-n-drop · SDF-текст · 3000 объектов',
    92, [0.46, 0.66, 1.0, 0.9], 'center'
  );

  const WORDS = ['узел', 'граф', 'point', 'node', 'данные', 'WebGL', 'ось', 'pixel', 'вектор', 'mesh'];

  const rng = mulberry32(20260609);
  for (let i = 0; i < OBJECT_COUNT; i++) {
    const x = (rng() - 0.5) * FIELD_W;
    const y = (rng() - 0.5) * FIELD_H;
    const isCircle = rng() < 0.35;
    const base = 34 + rng() * 54;
    const w = isCircle ? base : base * (0.7 + rng() * 1.1);
    const h = isCircle ? base : base * (0.7 + rng() * 1.1);
    const hue = (i * 137.50776) % 360; // золотой угол — равномерные оттенки
    const rgb = hslToRgb(hue / 360, 0.62, 0.58);
    const rotation = isCircle ? 0 : (rng() - 0.5) * 0.6;
    const label = i % 6 === 0 ? WORDS[((i / 6) | 0) % WORDS.length] : '#' + i;

    scene.addShape({
      x, y, w, h, rotation,
      shape: isCircle ? 1 : 0,
      color: [rgb[0], rgb[1], rgb[2], 0.92],
      label,
      labelSize: Math.max(11, base * 0.34),
      labelColor: [1, 1, 1, 0.92],
    });
  }

  scene.upload();

  // 4. Камера: вписываем всё поле в экран.
  const cam = renderer.camera;
  const vw = cam.width > 2 ? cam.width : window.innerWidth * renderer.dpr;
  const vh = cam.height > 2 ? cam.height : window.innerHeight * renderer.dpr;
  fitZoom = Math.min(vw / (FIELD_W * 1.12), vh / (FIELD_H * 1.5));
  resetView();

  function resetView() {
    cam.x = 0;
    cam.y = 0;
    cam.zoom = fitZoom;
    cam.clampZoom();
  }

  // 5. Управление.
  new Controls(renderer, scene);
  window.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R' || e.key === 'к' || e.key === 'К') resetView();
  });

  // 6. HUD.
  const el = {
    fps: document.getElementById('st-fps'),
    obj: document.getElementById('st-obj'),
    glyph: document.getElementById('st-glyph'),
    zoom: document.getElementById('st-zoom'),
  };
  el.obj.textContent = OBJECT_COUNT.toLocaleString('ru-RU');
  el.glyph.textContent = scene.glyphCount.toLocaleString('ru-RU');

  loading.classList.add('hidden');

  // 7. Цикл отрисовки + счётчик FPS.
  let frames = 0;
  let lastT = performance.now();
  renderer.run((t) => {
    renderer.clear(0.043, 0.05, 0.07, 1);
    cam.updateMatrix();
    scene.draw(cam.matrix);

    frames++;
    if (t - lastT >= 500) {
      el.fps.textContent = Math.round((frames * 1000) / (t - lastT));
      el.zoom.textContent =
        cam.zoom >= 1 ? cam.zoom.toFixed(1) + '×' : cam.zoom.toFixed(2) + '×';
      frames = 0;
      lastT = t;
    }
  });
}

// HSL -> RGB (компоненты 0..1).
function hslToRgb(h, s, l) {
  const k = (n) => (n + h * 12) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  return [f(0), f(8), f(4)];
}

// Детерминированный ГПСЧ — стабильная картинка между перезагрузками.
function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
