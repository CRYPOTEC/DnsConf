// Управление мышью/тачем:
//  - колесо — зум к курсору;
//  - тащить пустое место — панорама;
//  - тащить фигуру — перемещение (drag-n-drop).
export class Controls {
  constructor(renderer, scene) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = renderer.camera;
    this.canvas = renderer.canvas;

    this.panning = false;
    this.dragIndex = -1;
    this.last = { x: 0, y: 0 };
    this._a = { x: 0, y: 0 };
    this._b = { x: 0, y: 0 };

    this._attach();
  }

  _pos(e) {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = this.renderer.dpr;
    return {
      x: (e.clientX - rect.left) * dpr,
      y: (e.clientY - rect.top) * dpr,
    };
  }

  _attach() {
    const c = this.canvas;
    c.addEventListener('wheel', (e) => this._wheel(e), { passive: false });
    c.addEventListener('pointerdown', (e) => this._down(e));
    window.addEventListener('pointermove', (e) => this._move(e));
    window.addEventListener('pointerup', () => this._up());
    window.addEventListener('pointercancel', () => this._up());
    c.addEventListener('contextmenu', (e) => e.preventDefault());
  }

  _wheel(e) {
    e.preventDefault();
    const cam = this.camera;
    const p = this._pos(e);
    const before = cam.screenToWorld(p.x, p.y, this._a);
    const factor = Math.exp(-e.deltaY * 0.0016);
    cam.zoom *= factor;
    cam.clampZoom();
    // Удерживаем мировую точку под курсором на месте.
    cam.x = before.x - (p.x - cam.width / 2) / cam.zoom;
    cam.y = before.y - (p.y - cam.height / 2) / cam.zoom;
  }

  _down(e) {
    if (e.button !== 0 && e.button !== 1) return;
    const cam = this.camera;
    const p = this._pos(e);
    const w = cam.screenToWorld(p.x, p.y, this._a);
    const hit = e.button === 0 ? this.scene.pick(w.x, w.y) : -1;
    if (hit >= 0) {
      this.dragIndex = hit;
    } else {
      this.panning = true;
    }
    this.canvas.style.cursor = 'grabbing';
    this.last = p;
  }

  _move(e) {
    const cam = this.camera;
    const p = this._pos(e);
    if (this.dragIndex >= 0) {
      const a = cam.screenToWorld(this.last.x, this.last.y, this._a);
      const b = cam.screenToWorld(p.x, p.y, this._b);
      this.scene.moveShape(this.dragIndex, b.x - a.x, b.y - a.y);
      this.last = p;
    } else if (this.panning) {
      cam.x -= (p.x - this.last.x) / cam.zoom;
      cam.y -= (p.y - this.last.y) / cam.zoom;
      this.last = p;
    } else {
      const w = cam.screenToWorld(p.x, p.y, this._a);
      this.canvas.style.cursor = this.scene.pick(w.x, w.y) >= 0 ? 'grab' : 'default';
    }
  }

  _up() {
    this.dragIndex = -1;
    this.panning = false;
    this.canvas.style.cursor = 'default';
  }
}
