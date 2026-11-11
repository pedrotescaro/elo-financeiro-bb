"use strict";
// Micro-interações em Lottie, desenhadas para o Elo (sem arquivos de terceiros).
// Usa o player lottie_light (sem eval); se ele não carregar, nada quebra.
(function(){
  const NAVY = [0.075, 0.173, 0.361, 1];
  const GREEN = [0.063, 0.545, 0.388, 1];
  const WHITE = [1, 1, 1, 1];
  const transform = () => ({ty: "tr", p: {a: 0, k: [0, 0]}, a: {a: 0, k: [0, 0]}, s: {a: 0, k: [100, 100]}, r: {a: 0, k: 0}, o: {a: 0, k: 100}});
  const ease = {o: {x: [0.2], y: [0]}, i: {x: [0.1], y: [1]}};
  const layer = (ind, name, shapes, ks) => ({ddd: 0, ind, ty: 4, nm: name, sr: 1, ao: 0, ip: 0, op: 600, st: 0, bm: 0,
    ks: Object.assign({o: {a: 0, k: 100}, r: {a: 0, k: 0}, p: {a: 0, k: [32, 32, 0]}, a: {a: 0, k: [0, 0, 0]}, s: {a: 0, k: [100, 100, 100]}}, ks || {}),
    shapes});

  // Confirmação: o disco cresce e o traço do check se desenha.
  const check = {v: "5.7.4", fr: 60, ip: 0, op: 46, w: 64, h: 64, nm: "elo-check", ddd: 0, assets: [], layers: [
    layer(1, "check", [{ty: "gr", it: [
      {ty: "sh", ks: {a: 0, k: {i: [[0, 0], [0, 0], [0, 0]], o: [[0, 0], [0, 0], [0, 0]], v: [[-10, 1], [-3, 8], [11, -7]], c: false}}},
      {ty: "tm", s: {a: 0, k: 0}, e: {a: 1, k: [Object.assign({t: 12, s: [0]}, ease), {t: 34, s: [100]}]}, o: {a: 0, k: 0}, m: 1},
      {ty: "st", c: {a: 0, k: WHITE}, o: {a: 0, k: 100}, w: {a: 0, k: 4.5}, lc: 2, lj: 2},
      transform()]}]),
    layer(2, "disco", [{ty: "gr", it: [
      {ty: "el", p: {a: 0, k: [0, 0]}, s: {a: 0, k: [44, 44]}},
      {ty: "fl", c: {a: 0, k: GREEN}, o: {a: 0, k: 100}},
      transform()]}], {s: {a: 1, k: [Object.assign({t: 0, s: [40, 40, 100]}, ease), {t: 16, s: [100, 100, 100]}]}}),
  ]};

  // Pensando: três pontos que sobem em sequência, em laço.
  const dot = (ind, x, delay) => layer(ind, "ponto" + ind, [{ty: "gr", it: [
    {ty: "el", p: {a: 0, k: [0, 0]}, s: {a: 0, k: [9, 9]}},
    {ty: "fl", c: {a: 0, k: NAVY}, o: {a: 0, k: 100}},
    transform()]}], {
    p: {a: 1, k: [Object.assign({t: delay, s: [x, 34, 0]}, ease), Object.assign({t: delay + 12, s: [x, 26, 0]}, ease), {t: delay + 24, s: [x, 34, 0]}]},
    o: {a: 1, k: [Object.assign({t: delay, s: [35]}, ease), Object.assign({t: delay + 12, s: [100]}, ease), {t: delay + 24, s: [35]}]},
  });
  const dots = {v: "5.7.4", fr: 60, ip: 0, op: 60, w: 64, h: 64, nm: "elo-dots", ddd: 0, assets: [],
    layers: [dot(1, 18, 0), dot(2, 32, 8), dot(3, 46, 16)]};

  const DATA = {check, dots};
  const playing = new WeakMap();

  window.EloAnim = {
    // Toca a animação no contêiner; devolve false quando o player não existe.
    play(container, name, loop){
      if(!container || typeof window.lottie === "undefined" || !DATA[name]) return false;
      const previous = playing.get(container);
      if(previous) previous.destroy();
      const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const animation = window.lottie.loadAnimation({container, renderer: "svg", loop: !!loop && !reduce,
        autoplay: !reduce, animationData: JSON.parse(JSON.stringify(DATA[name]))});
      if(reduce) animation.goToAndStop(animation.totalFrames - 1, true);
      playing.set(container, animation);
      return true;
    },
    stop(container){
      const previous = container && playing.get(container);
      if(previous){ previous.destroy(); playing.delete(container); }
    },
  };
})();
