/* Instalar no celular (PWA). Qualquer botão com data-acao="instalar" aparece só quando a instalação é possível. */
(function () {
  'use strict';
  const instalado = () => matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  const ua = navigator.userAgent;
  const ios = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  let pedido = null;

  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
  }
  const atualizar = () => document.body.classList.toggle('pode-instalar', !instalado() && (!!pedido || ios));
  window.addEventListener('beforeinstallprompt', (ev) => { ev.preventDefault(); pedido = ev; atualizar(); });
  window.addEventListener('appinstalled', () => { pedido = null; atualizar(); });
  document.addEventListener('DOMContentLoaded', atualizar);

  const COMPARTILHAR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M8 7l4-4 4 4"/><path d="M6 11H5v10h14V11h-1"/></svg>';
  const MAIS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="M12 8v8M8 12h8"/></svg>';
  function folha(html) {
    const f = document.createElement('div');
    f.className = 'instalar-fundo';
    f.innerHTML = `<div class="instalar-folha" role="dialog" aria-modal="true" aria-labelledby="instalar-tit">${html}<button type="button" class="btn">Entendi</button></div>`;
    const fechar = () => f.remove();
    f.addEventListener('click', ev => { if (ev.target === f || ev.target.closest('button')) fechar(); });
    document.body.appendChild(f);
    if (window.gsap && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      gsap.fromTo(f, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2 });
      gsap.fromTo(f.firstElementChild, { y: 40 }, { y: 0, duration: 0.35, ease: 'power3.out' });
    }
    f.querySelector('button').focus();
  }
  async function instalar() {
    if (pedido) {
      pedido.prompt();
      try { await pedido.userChoice; } catch (e) { /* cancelado */ }
      pedido = null; atualizar();
    } else if (ios) {
      folha(`<h2 id="instalar-tit">Instalar no iPhone</h2>
        <ol><li>Abra esta página no <b>Safari</b>.</li>
        <li>Toque em <b>Compartilhar</b> ${COMPARTILHAR} na barra de baixo.</li>
        <li>Escolha <b>Adicionar à Tela de Início</b> ${MAIS} e toque em <b>Adicionar</b>.</li></ol>`);
    } else {
      folha(`<h2 id="instalar-tit">Instalar no celular</h2>
        <ol><li>Abra o menu do navegador (⋮).</li><li>Toque em <b>Instalar app</b> ou <b>Adicionar à tela inicial</b>.</li></ol>`);
    }
  }
  document.addEventListener('click', (ev) => { if (ev.target.closest('[data-acao="instalar"]')) instalar(); });
  window.INSTALAR = { instalar, atualizar };
})();
