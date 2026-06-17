import { createProgram } from './gl.js';

// Инстансный батч глифов поверх SDF-атласа. Один draw-call на весь текст.
// Раскладка инстанса (12 float): posX, posY, sizeX, sizeY, u0, v0, u1, v1, r, g, b, a.
// posX/posY — центр глифа в мире, sizeX/sizeY — размер квада в мире.

const STRIDE = 12;

const VERT = `#version 300 es
layout(location = 0) in vec2 a_quad;
layout(location = 1) in vec2 a_uv;
layout(location = 2) in vec2 i_pos;
layout(location = 3) in vec2 i_size;
layout(location = 4) in vec4 i_uvrect;
layout(location = 5) in vec4 i_color;

uniform mat3 u_matrix;

out vec2 v_uv;
out vec4 v_color;

void main() {
  vec2 world = i_pos + a_quad * i_size;
  vec3 clip = u_matrix * vec3(world, 1.0);
  gl_Position = vec4(clip.xy, 0.0, 1.0);
  v_uv = mix(i_uvrect.xy, i_uvrect.zw, a_uv);
  v_color = i_color;
}`;

const FRAG = `#version 300 es
precision highp float;

uniform sampler2D u_atlas;

in vec2 v_uv;
in vec4 v_color;

out vec4 fragColor;

void main() {
  // В SDF значение 0.5 — это контур; >0.5 внутри глифа.
  float dist = texture(u_atlas, v_uv).r;
  float aa = max(fwidth(dist), 0.0001);
  float alpha = smoothstep(0.5 - aa, 0.5 + aa, dist);
  if (alpha < 0.004) discard;
  fragColor = vec4(v_color.rgb, v_color.a * alpha);
}`;

export class TextBatch {
  constructor(gl, atlas) {
    this.gl = gl;
    this.stride = STRIDE;
    this.count = 0;
    this.data = null;

    this.program = createProgram(gl, VERT, FRAG);
    this.u_matrix = gl.getUniformLocation(this.program, 'u_matrix');
    this.u_atlas = gl.getUniformLocation(this.program, 'u_atlas');

    // Текстура SDF-атласа (один канал, R8).
    this.texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.texture);
    gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
    gl.texImage2D(
      gl.TEXTURE_2D, 0, gl.R8,
      atlas.width, atlas.height, 0,
      gl.RED, gl.UNSIGNED_BYTE, atlas.data
    );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

    this.vao = gl.createVertexArray();
    gl.bindVertexArray(this.vao);

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
    gl.vertexAttribPointer(5, 4, gl.FLOAT, false, s, 32);
    gl.vertexAttribDivisor(5, 1);

    gl.bindVertexArray(null);
  }

  setData(data, count) {
    const gl = this.gl;
    this.data = data;
    this.count = count;
    gl.bindBuffer(gl.ARRAY_BUFFER, this.instanceBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW);
  }

  // Перезалить диапазон глифов (например, подпись перетаскиваемого объекта).
  updateRange(start, count) {
    if (count <= 0) return;
    const gl = this.gl;
    const s = this.stride;
    gl.bindBuffer(gl.ARRAY_BUFFER, this.instanceBuffer);
    gl.bufferSubData(
      gl.ARRAY_BUFFER,
      start * s * 4,
      this.data.subarray(start * s, (start + count) * s)
    );
  }

  draw(matrix) {
    if (!this.count) return;
    const gl = this.gl;
    gl.useProgram(this.program);
    gl.uniformMatrix3fv(this.u_matrix, false, matrix);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.texture);
    gl.uniform1i(this.u_atlas, 0);
    gl.bindVertexArray(this.vao);
    gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 4, this.count);
    gl.bindVertexArray(null);
  }
}
