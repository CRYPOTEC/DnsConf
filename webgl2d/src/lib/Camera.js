// Ортографическая 2D-камера. Все размеры — в пикселях буфера (device px).
// Хранит позицию (центр обзора в мировых координатах) и зум.
// Мир: ось Y направлена вниз (как у экрана).

export class Camera {
  constructor() {
    this.x = 0;
    this.y = 0;
    this.zoom = 1;
    this.width = 1;
    this.height = 1;
    this.minZoom = 0.02;
    this.maxZoom = 60;
    this.matrix = new Float32Array(9);
  }

  resize(width, height) {
    this.width = width;
    this.height = height;
  }

  clampZoom() {
    if (this.zoom < this.minZoom) this.zoom = this.minZoom;
    else if (this.zoom > this.maxZoom) this.zoom = this.maxZoom;
  }

  // Экранные пиксели (от левого-верхнего угла буфера) -> мировые координаты.
  screenToWorld(sx, sy, out = { x: 0, y: 0 }) {
    out.x = this.x + (sx - this.width / 2) / this.zoom;
    out.y = this.y + (sy - this.height / 2) / this.zoom;
    return out;
  }

  // Мировые координаты -> экранные пиксели.
  worldToScreen(wx, wy, out = { x: 0, y: 0 }) {
    out.x = (wx - this.x) * this.zoom + this.width / 2;
    out.y = (wy - this.y) * this.zoom + this.height / 2;
    return out;
  }

  // 3x3 матрица world -> clip space, column-major (как ждёт uniformMatrix3fv).
  updateMatrix() {
    const a = (2 * this.zoom) / this.width;
    const b = (2 * this.zoom) / this.height;
    const m = this.matrix;
    m[0] = a;            m[1] = 0;           m[2] = 0;
    m[3] = 0;            m[4] = -b;          m[5] = 0;
    m[6] = -a * this.x;  m[7] = b * this.y;  m[8] = 1;
    return m;
  }
}
