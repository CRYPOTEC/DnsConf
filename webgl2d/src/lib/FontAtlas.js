// Генератор SDF-атласа шрифта на лету (без внешних зависимостей).
//
// Идея: каждый глиф рендерится в 2D-canvas, по альфе строится знаковое поле
// расстояний (signed distance field) алгоритмом Felzenszwalb & Huttenlocher.
// SDF упаковывается в один R8-атлас. Благодаря этому текст остаётся чётким
// на любом зуме — резкость даёт smoothstep по полю расстояний в шейдере.
//
// Метрики глифа хранятся в долях кегля (em), относительно опорной точки на
// базовой линии, ось Y вниз. Это позволяет раскладывать строку в мире любым
// размером.

const INF = 1e20;

export class FontAtlas {
  constructor({
    fontSize = 46,
    padding = 8,
    fontFamily = 'system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif',
    fontWeight = 600,
    atlasWidth = 1024,
  } = {}) {
    this.fontSize = fontSize;
    this.padding = padding;
    this.atlasWidth = atlasWidth;
    this.font = `${fontWeight} ${fontSize}px ${fontFamily}`;

    this.glyphs = new Map();
    this.width = 0;
    this.height = 0;
    this.data = null;

    this.canvas = document.createElement('canvas');
    this.canvas.width = fontSize * 2 + padding * 2 + 8;
    this.canvas.height = fontSize * 2 + padding * 2 + 8;
    this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
    this._applyFont();
  }

  _applyFont() {
    const ctx = this.ctx;
    ctx.font = this.font;
    ctx.textBaseline = 'alphabetic';
    ctx.textAlign = 'left';
    ctx.fillStyle = '#fff';
  }

  // Построить атлас для набора символов (строка). Дубликаты игнорируются.
  build(chars) {
    this._applyFont();

    const entries = [];
    const seen = new Set();
    for (const ch of chars) {
      if (seen.has(ch)) continue;
      seen.add(ch);
      entries.push(this._renderGlyph(ch));
    }

    // Полочная упаковка: сортируем по высоте, кладём слева направо.
    const spacing = 2;
    const aw = this.atlasWidth;
    const sorted = entries.filter((g) => g.hasQuad).sort((a, b) => b.H - a.H);

    let x = spacing;
    let y = spacing;
    let rowH = 0;
    for (const g of sorted) {
      if (x + g.W + spacing > aw) {
        x = spacing;
        y += rowH + spacing;
        rowH = 0;
      }
      g.ax = x;
      g.ay = y;
      x += g.W + spacing;
      if (g.H > rowH) rowH = g.H;
    }

    const ah = nextPow2(y + rowH + spacing);
    const atlas = new Uint8Array(aw * ah);

    for (const g of sorted) {
      for (let row = 0; row < g.H; row++) {
        const src = g.sdf.subarray(row * g.W, row * g.W + g.W);
        atlas.set(src, (g.ay + row) * aw + g.ax);
      }
      g.u0 = g.ax / aw;
      g.v0 = g.ay / ah;
      g.u1 = (g.ax + g.W) / aw;
      g.v1 = (g.ay + g.H) / ah;
      g.sdf = null; // освобождаем временные данные
    }

    this.width = aw;
    this.height = ah;
    this.data = atlas;
    for (const g of entries) this.glyphs.set(g.char, g);
    return this;
  }

  glyph(ch) {
    return this.glyphs.get(ch) || this.glyphs.get('?') || this.glyphs.get(' ');
  }

  // Ширина строки в мировых единицах при заданном размере.
  measure(str, size) {
    let w = 0;
    for (const ch of str) {
      const g = this.glyph(ch);
      if (g) w += g.advance * size;
    }
    return w;
  }

  _renderGlyph(ch) {
    const ctx = this.ctx;
    const pad = this.padding;
    const fs = this.fontSize;

    const m = ctx.measureText(ch);
    const advance = m.width / fs;
    const left = m.actualBoundingBoxLeft || 0;
    const right = m.actualBoundingBoxRight || 0;
    const ascent = m.actualBoundingBoxAscent || 0;
    const descent = m.actualBoundingBoxDescent || 0;

    const inkW = Math.ceil(right + left);
    const inkH = Math.ceil(ascent + descent);

    const glyph = {
      char: ch,
      advance,
      hasQuad: false,
      W: 0, H: 0, ax: 0, ay: 0,
      u0: 0, v0: 0, u1: 0, v1: 0,
      planeLeft: 0, planeTop: 0, planeRight: 0, planeBottom: 0,
      sdf: null,
    };

    // Пробел и непечатные символы — только метрика advance, без квада.
    if (inkW <= 0 || inkH <= 0) return glyph;

    const W = inkW + pad * 2;
    const H = inkH + pad * 2;

    if (this.canvas.width < W || this.canvas.height < H) {
      this.canvas.width = Math.max(this.canvas.width, W);
      this.canvas.height = Math.max(this.canvas.height, H);
      this._applyFont();
    }

    // Рисуем глиф так, чтобы его «чернила» начинались в (pad, pad).
    const originX = pad + left;
    const originY = pad + ascent;
    ctx.clearRect(0, 0, W, H);
    ctx.fillText(ch, originX, originY);
    const img = ctx.getImageData(0, 0, W, H).data;

    const len = W * H;
    const gridOuter = new Float64Array(len);
    const gridInner = new Float64Array(len);
    gridOuter.fill(INF);
    // gridInner по умолчанию заполнен нулями (внешние пиксели — «фичи»).

    let hasInk = false;
    for (let i = 0; i < len; i++) {
      const a = img[i * 4 + 3] / 255;
      if (a === 0) continue;
      hasInk = true;
      if (a === 1) {
        gridOuter[i] = 0;
        gridInner[i] = INF;
      } else {
        const d = 0.5 - a;
        gridOuter[i] = d > 0 ? d * d : 0;
        gridInner[i] = d < 0 ? d * d : 0;
      }
    }
    if (!hasInk) return glyph;

    edt(gridOuter, W, H);
    edt(gridInner, W, H);

    const sdf = new Uint8Array(len);
    const spread = pad;
    for (let i = 0; i < len; i++) {
      // >0 внутри глифа, <0 снаружи.
      const signed = Math.sqrt(gridInner[i]) - Math.sqrt(gridOuter[i]);
      let v = 0.5 + signed / (2 * spread);
      v = v < 0 ? 0 : v > 1 ? 1 : v;
      sdf[i] = (v * 255) | 0;
    }

    glyph.hasQuad = true;
    glyph.W = W;
    glyph.H = H;
    glyph.sdf = sdf;
    glyph.planeLeft = -(pad + left) / fs;
    glyph.planeRight = (inkW + pad - left) / fs;
    glyph.planeTop = -(pad + ascent) / fs;
    glyph.planeBottom = (inkH + pad - ascent) / fs;
    return glyph;
  }
}

function nextPow2(n) {
  let p = 1;
  while (p < n) p <<= 1;
  return p;
}

// 2D-преобразование расстояний (квадраты евклидовых расстояний).
function edt(grid, width, height) {
  const max = Math.max(width, height);
  const f = new Float64Array(max);
  const v = new Int32Array(max);
  const z = new Float64Array(max + 1);
  for (let x = 0; x < width; x++) edt1d(grid, x, width, height, f, v, z);
  for (let y = 0; y < height; y++) edt1d(grid, y * width, 1, width, f, v, z);
}

// 1D-проход (алгоритм нижней огибающей парабол).
function edt1d(grid, offset, stride, length, f, v, z) {
  v[0] = 0;
  z[0] = -INF;
  z[1] = INF;
  f[0] = grid[offset];
  for (let q = 1, k = 0, s = 0; q < length; q++) {
    f[q] = grid[offset + q * stride];
    const q2 = q * q;
    do {
      const r = v[k];
      s = (f[q] - f[r] + q2 - r * r) / (q - r) / 2;
    } while (s <= z[k] && --k > -1);
    k++;
    v[k] = q;
    z[k] = s;
    z[k + 1] = INF;
  }
  for (let q = 0, k = 0; q < length; q++) {
    while (z[k + 1] < q) k++;
    const r = v[k];
    grid[offset + q * stride] = f[r] + (q - r) * (q - r);
  }
}
