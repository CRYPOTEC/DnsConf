import { Camera } from './Camera.js';

// Владеет WebGL2-контекстом, камерой, ресайзом и циклом отрисовки.
export class Renderer {
  constructor(canvas) {
    const gl = canvas.getContext('webgl2', {
      alpha: false,
      antialias: false,
      premultipliedAlpha: false,
    });
    if (!gl) {
      throw new Error('WebGL2 не поддерживается этим браузером.');
    }

    this.canvas = canvas;
    this.gl = gl;
    this.camera = new Camera();
    this.dpr = clampDpr();

    gl.enable(gl.BLEND);
    gl.blendFuncSeparate(
      gl.SRC_ALPHA,
      gl.ONE_MINUS_SRC_ALPHA,
      gl.ONE,
      gl.ONE_MINUS_SRC_ALPHA
    );

    this.resize();
    const ro = new ResizeObserver(() => this.resize());
    ro.observe(canvas);
  }

  resize() {
    this.dpr = clampDpr();
    const w = Math.max(1, Math.round(this.canvas.clientWidth * this.dpr));
    const h = Math.max(1, Math.round(this.canvas.clientHeight * this.dpr));
    if (this.canvas.width !== w || this.canvas.height !== h) {
      this.canvas.width = w;
      this.canvas.height = h;
    }
    this.gl.viewport(0, 0, w, h);
    this.camera.resize(w, h);
  }

  clear(r, g, b, a = 1) {
    const gl = this.gl;
    gl.clearColor(r, g, b, a);
    gl.clear(gl.COLOR_BUFFER_BIT);
  }

  run(frame) {
    const loop = (t) => {
      frame(t);
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }
}

function clampDpr() {
  // Ограничиваем DPR, чтобы на retina не плодить лишние пиксели.
  return Math.min(Math.max(window.devicePixelRatio || 1, 1), 2);
}
