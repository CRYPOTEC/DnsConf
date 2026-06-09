import { createProgram } from './gl.js';

// Инстансный батч прямоугольников и кругов: один draw-call на все фигуры.
// Раскладка инстанса (10 float): posX, posY, sizeX, sizeY, r, g, b, a, rotation, shape.
// shape: 0 — прямоугольник, 1 — круг/эллипс.

const STRIDE = 10;

const VERT = `#version 300 es
layout(location = 0) in vec2 a_quad;
layout(location = 1) in vec2 a_uv;
layout(location = 2) in vec2 i_pos;
layout(location = 3) in vec2 i_size;
layout(location = 4) in vec4 i_color;
layout(location = 5) in float i_rotation;
layout(location = 6) in float i_shape;

uniform mat3 u_matrix;

out vec4 v_color;
out vec2 v_uv;
out float v_shape;

void main() {
  float c = cos(i_rotation);
  float s = sin(i_rotation);
  vec2 local = a_quad * i_size;
  vec2 rotated = vec2(local.x * c - local.y * s, local.x * s + local.y * c);
  vec2 world = i_pos + rotated;
  vec3 clip = u_matrix * vec3(world, 1.0);
  gl_Position = vec4(clip.xy, 0.0, 1.0);
  v_color = i_color;
  v_uv = a_uv;
  v_shape = i_shape;
}`;

const FRAG = `#version 300 es
precision highp float;

in vec4 v_color;
in vec2 v_uv;
in float v_shape;

out vec4 fragColor;

void main() {
  float alpha = 1.0;
  if (v_shape > 0.5) {
    // Сглаженный круг: расстояние от центра, 1.0 на краю.
    float d = length(v_uv - vec2(0.5)) * 2.0;
    float aa = max(fwidth(d), 0.0001);
    alpha = 1.0 - smoothstep(1.0 - aa, 1.0, d);
  }
  if (alpha <= 0.0) discard;
  fragColor = vec4(v_color.rgb, v_color.a * alpha);
}`;

export class ShapeBatch {
  constructor(gl) {
    this.gl = gl;
    this.stride = STRIDE;
    this.count = 0;
    this.data = null;

    this.program = createProgram(gl, VERT, FRAG);
    this.u_matrix = gl.getUniformLocation(this.program, 'u_matrix');

    this.vao = gl.createVertexArray();
    gl.bindVertexArray(this.vao);

    // Геометрия единичного квада (triangle strip) + локальные UV.
    const quad = new Float32Array([
      -0.5, -0.5, 0, 0,
       0.5, -0.5, 1, 0,
      -0.5,  0.5, 0, 1,
       0.5,  0.5, 1, 1,
    ]);
    this.quadBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, quad, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 16, 0);
    gl.enableVertexAttribArray(1);
    gl.vertexAttribPointer(1, 2, gl.FLOAT, false, 16, 8);

    // Буфер инстансов.
    this.instanceBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.instanceBuffer);
    const s = STRIDE * 4;
    gl.enableVertexAttribArray(2);
    gl.vertexAttribPointer(2, 2, gl.FLOAT, false, s, 0);
    gl.vertexAttribDivisor(2, 1);
    gl.enableVertexAttribArray(3);
    gl.vertexAttribPointer(3, 2, gl.FLOAT, false, s, 8);
    gl.vertexAttribDivisor(3, 1);
    gl.enableVertexAttribArray(4);
    gl.vertexAttribPointer(4, 4, gl.FLOAT, false, s, 16);
    gl.vertexAttribDivisor(4, 1);
    gl.enableVertexAttribArray(5);
    gl.vertexAttribPointer(5, 1, gl.FLOAT, false, s, 32);
    gl.vertexAttribDivisor(5, 1);
    gl.enableVertexAttribArray(6);
    gl.vertexAttribPointer(6, 1, gl.FLOAT, false, s, 36);
    gl.vertexAttribDivisor(6, 1);

    gl.bindVertexArray(null);
  }

  setData(data, count) {
    const gl = this.gl;
    this.data = data;
    this.count = count;
    gl.bindBuffer(gl.ARRAY_BUFFER, this.instanceBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW);
  }

  // Перезалить один инстанс (например, при перетаскивании).
  updateInstance(index) {
    const gl = this.gl;
    const off = index * this.stride;
    gl.bindBuffer(gl.ARRAY_BUFFER, this.instanceBuffer);
    gl.bufferSubData(gl.ARRAY_BUFFER, off * 4, this.data.subarray(off, off + this.stride));
  }

  draw(matrix) {
    if (!this.count) return;
    const gl = this.gl;
    gl.useProgram(this.program);
    gl.uniformMatrix3fv(this.u_matrix, false, matrix);
    gl.bindVertexArray(this.vao);
    gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 4, this.count);
    gl.bindVertexArray(null);
  }
}
