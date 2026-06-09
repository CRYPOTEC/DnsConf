import { ShapeBatch } from './ShapeBatch.js';
import { TextBatch } from './TextBatch.js';

// Сцена связывает фигуры и их текстовые подписи, умеет в пикинг и перемещение.
// Сборка идёт в обычные JS-массивы, затем upload() заливает всё в GPU.
export class Scene {
  constructor(renderer, atlas) {
    this.renderer = renderer;
    this.gl = renderer.gl;
    this.atlas = atlas;

    this.shapes = new ShapeBatch(this.gl);
    this.text = new TextBatch(this.gl, atlas);

    this.records = [];
    this._shapeArr = [];
    this._textArr = [];
    this._shapeData = null;
    this._textData = null;
  }

  // Добавить фигуру (опционально с подписью по центру).
  addShape({
    x, y, w, h,
    rotation = 0,
    shape = 0,
    color = [1, 1, 1, 1],
    label = null,
    labelSize = 0,
    labelColor = [1, 1, 1, 1],
    pickable = true,
  }) {
    const index = this.records.length;
    const rec = { x, y, w, h, rot: rotation, shape, pickable, textStart: -1, textCount: 0 };
    this._shapeArr.push(x, y, w, h, color[0], color[1], color[2], color[3], rotation, shape);

    if (label && labelSize > 0) {
      const r = this._layoutText(x, y, label, labelSize, labelColor, 'center', true);
      rec.textStart = r.start;
      rec.textCount = r.count;
    }
    this.records.push(rec);
    return index;
  }

  // Свободная надпись в мире (не привязана к фигуре, не таскается).
  addText(x, y, str, size, color = [1, 1, 1, 1], align = 'center') {
    this._layoutText(x, y, str, size, color, align, true);
  }

  _layoutText(anchorX, anchorY, str, size, color, align, centerY) {
    const atlas = this.atlas;
    const start = this._textArr.length / 12;
    const width = atlas.measure(str, size);
    let penX =
      align === 'center' ? anchorX - width / 2 :
      align === 'right' ? anchorX - width :
      anchorX;
    // Базовая линия чуть ниже центра, чтобы текст визуально центрировался.
    const baseY = centerY ? anchorY + 0.33 * size : anchorY;

    let count = 0;
    for (const ch of str) {
      const g = atlas.glyph(ch);
      if (!g) continue;
      if (g.hasQuad) {
        const x0 = penX + g.planeLeft * size;
        const x1 = penX + g.planeRight * size;
        const y0 = baseY + g.planeTop * size;
        const y1 = baseY + g.planeBottom * size;
        this._textArr.push(
          (x0 + x1) / 2, (y0 + y1) / 2,
          x1 - x0, y1 - y0,
          g.u0, g.v0, g.u1, g.v1,
          color[0], color[1], color[2], color[3]
        );
        count++;
      }
      penX += g.advance * size;
    }
    return { start, count };
  }

  upload() {
    this._shapeData = new Float32Array(this._shapeArr);
    this._textData = new Float32Array(this._textArr);
    this.shapes.setData(this._shapeData, this.records.length);
    this.text.setData(this._textData, this._textData.length / 12);
    this._shapeArr = null;
    this._textArr = null;
  }

  get glyphCount() {
    return this.text.count;
  }

  // Вернуть индекс верхней фигуры под точкой (мировые координаты) или -1.
  pick(wx, wy) {
    const recs = this.records;
    for (let i = recs.length - 1; i >= 0; i--) {
      const r = recs[i];
      if (!r.pickable) continue;
      let lx = wx - r.x;
      let ly = wy - r.y;
      if (r.rot) {
        const c = Math.cos(-r.rot);
        const s = Math.sin(-r.rot);
        const nx = lx * c - ly * s;
        const ny = lx * s + ly * c;
        lx = nx;
        ly = ny;
      }
      const hw = r.w / 2;
      const hh = r.h / 2;
      if (r.shape > 0.5) {
        if ((lx * lx) / (hw * hw) + (ly * ly) / (hh * hh) <= 1) return i;
      } else if (lx >= -hw && lx <= hw && ly >= -hh && ly <= hh) {
        return i;
      }
    }
    return -1;
  }

  // Сдвинуть фигуру (и её подпись) на (dx, dy) и перезалить только их.
  moveShape(i, dx, dy) {
    const r = this.records[i];
    r.x += dx;
    r.y += dy;

    const so = i * 10;
    this._shapeData[so] += dx;
    this._shapeData[so + 1] += dy;
    this.shapes.updateInstance(i);

    if (r.textCount > 0) {
      const td = this._textData;
      const base = r.textStart * 12;
      for (let g = 0; g < r.textCount; g++) {
        td[base + g * 12] += dx;
        td[base + g * 12 + 1] += dy;
      }
      this.text.updateRange(r.textStart, r.textCount);
    }
  }

  draw(matrix) {
    this.shapes.draw(matrix);
    this.text.draw(matrix);
  }
}
