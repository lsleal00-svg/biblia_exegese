/* Mapa do versículo: imagem de satélite do Crescente Fértil + elementos desenhados pelo usuário.
   Uso: const m = MapaExegese.montar(elemento, { vista, elementos, salvar(estado) }); m.destruir(); */
(function () {
  'use strict';
  const REGIAO = [[26.4, 25.2], [38.7, 51.2]];          // Egito → Mesopotâmia (recorte do Google Maps enviado)
  const LIMITES = [[20, 16], [44, 60]];
  const CORES = ['#2a1c10', '#b3261e', '#f2c14e', '#ffffff', '#1f5fa8', '#2e7d4f', '#7b3fa0', '#e8742a'];
  const h = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const uid = () => Math.random().toString(36).slice(2, 10);
  const reduzir = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------------------------------------------------------------- ícones (SVG desenhados)
  const SVG = {
    local: '<svg viewBox="0 0 32 40" class="svg-pin"><path d="M16 39s13-13.6 13-23.5C29 7.5 23.2 1.5 16 1.5S3 7.5 3 15.5C3 25.4 16 39 16 39z" fill="#b3261e" stroke="#fff" stroke-width="2.5"/><circle cx="16" cy="15.5" r="5" fill="#fff"/></svg>',
    cidade: `<svg viewBox="0 0 64 52" class="svg-cidade">
      <path d="M4 50V22h6v-6h5v6h6V12h6V6h10v6h6v10h6v-6h5v6h6v28z" fill="#e9d3a6" stroke="#4a3017" stroke-width="2.4" stroke-linejoin="round"/>
      <path d="M21 12h4V8h4v4h6V8h4v4h4" fill="none" stroke="#4a3017" stroke-width="2.4"/>
      <path d="M4 22h4v-4M60 22h-4v-4M10 16h1M53 16h1" stroke="#4a3017" stroke-width="2.4" fill="none"/>
      <path d="M26 50V38a6 6 0 0 1 12 0v12" fill="#4a3017"/>
      <rect x="11" y="28" width="4" height="6" rx="1" fill="#4a3017"/><rect x="49" y="28" width="4" height="6" rx="1" fill="#4a3017"/>
      <rect x="29" y="18" width="6" height="7" rx="1" fill="#4a3017"/>
      <path d="M2 50h60" stroke="#4a3017" stroke-width="3" stroke-linecap="round"/></svg>`,
    tenda: `<svg viewBox="0 0 64 48" class="svg-tenda">
      <path d="M6 44 30 8l26 36z" fill="#c9a26a" stroke="#4a3017" stroke-width="2.4" stroke-linejoin="round"/>
      <path d="M30 8l8 36" stroke="#4a3017" stroke-width="2" fill="none"/>
      <path d="M24 44l6-16 6 16z" fill="#4a3017"/>
      <path d="M30 8V3M14 32l-8-4M48 32l9-4" stroke="#4a3017" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M2 45h60" stroke="#4a3017" stroke-width="3" stroke-linecap="round"/></svg>`,
    monte: `<svg viewBox="0 0 72 50" class="svg-monte">
      <path d="M2 48 22 18l7 9 13-23 28 44z" fill="#a7825a" stroke="#4a3017" stroke-width="2.4" stroke-linejoin="round"/>
      <path d="M42 4 50 16l-4-1-4 4-3-3-4 2z" fill="#fbf6ea" stroke="#4a3017" stroke-width="1.6" stroke-linejoin="round"/>
      <path d="M22 18l4 6-3-1-3 3-2-2z" fill="#fbf6ea" stroke="#4a3017" stroke-width="1.4" stroke-linejoin="round"/>
      <path d="M42 4c-2 12-8 22-6 44M29 27c-3 7-5 13-4 21" stroke="#6e4b27" stroke-width="1.8" fill="none" stroke-linecap="round"/>
      <path d="M1 49h70" stroke="#4a3017" stroke-width="3" stroke-linecap="round"/></svg>`,
    x: (cor) => `<svg viewBox="0 0 40 40" class="svg-x"><path d="M8 8l24 24M32 8 8 32" stroke="#fff" stroke-width="11" stroke-linecap="round"/><path d="M8 8l24 24M32 8 8 32" stroke="${cor}" stroke-width="6.5" stroke-linecap="round"/></svg>`
  };
  const DICA_SELECAO = 'Toque num elemento para editar, mudar a cor ou apagar. Arraste o elemento para mudá-lo de lugar, ou arraste o mapa para movê-lo.';
  const FERRAMENTAS = [
    { id: 'selecao', nome: 'Seleção', dica: DICA_SELECAO, ico: '<svg viewBox="0 0 24 24"><path d="M5 3l14 8-6 1.6L10 19z"/><path d="M13 12.6 17.5 19"/></svg>' },
    { id: 'local', nome: 'Localização', dica: 'Toque no mapa para marcar o local.', ico: '<svg viewBox="0 0 24 24"><path d="M12 22s7-7.2 7-12.5A7 7 0 0 0 5 9.5C5 14.8 12 22 12 22z"/><circle cx="12" cy="9.5" r="2.5"/></svg>' },
    { id: 'texto', nome: 'Texto', dica: 'Toque no mapa onde o texto deve ficar.', ico: '<svg viewBox="0 0 24 24"><path d="M5 6V4h14v2M12 4v16M9 20h6"/></svg>' },
    { id: 'x', nome: 'Marcar com X', dica: 'Toque no mapa para colocar o X. Ele fica sempre por cima.', ico: '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg>' },
    { id: 'cidade', nome: 'Cidade fortificada', dica: 'Toque no mapa para colocar a cidade.', ico: '<svg viewBox="0 0 24 24"><path d="M3 21V10h3V7h3v3h2V5h2v5h2V7h3v3h3v11z"/><path d="M10 21v-4a2 2 0 0 1 4 0v4"/></svg>' },
    { id: 'monte', nome: 'Monte', dica: 'Toque no mapa para colocar o monte.', ico: '<svg viewBox="0 0 24 24"><path d="M2 20 9 9l3 4 4-8 6 15z"/><path d="M14.2 8.6 16 10l1.4-1"/></svg>' },
    { id: 'tenda', nome: 'Acampamento', dica: 'Toque no mapa para colocar a tenda.', ico: '<svg viewBox="0 0 24 24"><path d="M2 20 12 4l10 16z"/><path d="M12 4l3 16M9.5 20 12 13l2.5 7"/></svg>' },
    { id: 'seta', nome: 'Seta', dica: 'Toque no ponto de partida e depois no ponto para onde a seta aponta.', ico: '<svg viewBox="0 0 24 24"><path d="M4 20 19 5M10 5h9v9"/></svg>' },
    { id: 'seta-tracejada', nome: 'Seta pontilhada', dica: 'Toque no ponto de partida e depois no destino.', ico: '<svg viewBox="0 0 24 24"><path d="M4 20l2-2m3-3 2-2m3-3 2-2" /><path d="M11 5h8v8"/></svg>' },
    { id: 'pincel', nome: 'Pincel', dica: 'Pinte por cima do mapa para destacar uma região. O traço é largo e transparente. Toque nele depois para mudar a cor ou a espessura.', ico: '<svg viewBox="0 0 24 24"><path d="M14.5 4.5l5 5-8.2 8.2-5-5z"/><path d="M6.3 12.7 4 20l7.3-2.3"/><path d="M17 2l5 5"/></svg>' },
    { id: 'linha', nome: 'Linha livre', dica: 'Arraste o dedo (ou o mouse) para desenhar. Solte para terminar.', ico: '<svg viewBox="0 0 24 24"><path d="M3 17c3-6 5 2 8-3s4-7 7-5 2 6 3 7" stroke-dasharray="2 3.2"/></svg>' }
  ];

  const PINCEL = { p: 14, m: 26, g: 44 };
  const PINCEL_OPAC = 0.38;
  const desenhoLivre = (f) => f === 'linha' || f === 'pincel';

  function montar(el, opcoes) {
    if (!window.L) {
      el.innerHTML = '<div class="mapa-erro">Não foi possível carregar o mapa. Verifique a conexão e recarregue a página.</div>';
      return { destruir() {} };
    }
    const estado = {
      vista: opcoes.vista || null,
      elementos: (opcoes.elementos || []).map(e => ({ ...e })),
      ferramenta: 'selecao',
      selecionado: null,
      cor: localStorage_get('mapa-cor') || CORES[1]
    };
    el.innerHTML = `
      <div class="mapa-casca">
        <aside class="mapa-painel" aria-label="Elementos do mapa">
          <h3 class="mapa-painel-titulo">Elementos</h3>
          <div class="mapa-ferramentas" role="toolbar">
            ${FERRAMENTAS.map(f => `<button type="button" class="mapa-ferr" data-ferr="${f.id}" aria-pressed="false">${f.ico}<span>${f.nome}</span></button>`).join('')}
          </div>
          <div class="mapa-cores" role="group" aria-label="Cor">
            ${CORES.map(c => `<button type="button" class="mapa-cor ${c === estado.cor ? 'ativa' : ''}" data-cor="${c}" style="--c:${c}" aria-label="Cor ${c}"></button>`).join('')}
            <label class="mapa-cor-livre" title="Outra cor"><input type="color" value="${estado.cor}" aria-label="Escolher outra cor"></label>
          </div>
          <p class="mapa-dica" aria-live="polite">${DICA_SELECAO}</p>
          <button type="button" class="mapa-limpar" data-acao="limpar"><svg viewBox="0 0 24 24"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/></svg>Limpar tudo</button>
        </aside>
        <div class="mapa-area">
          <div class="mapa-leaflet"></div>
          <div class="mapa-acoes">
            <button type="button" class="mapa-btn" data-acao="recorte" title="Voltar ao recorte inteiro" aria-label="Voltar ao recorte inteiro"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/><circle cx="12" cy="12" r="2"/></svg></button>
            <button type="button" class="mapa-btn" data-acao="png" title="Salvar o mapa como imagem (PNG)" aria-label="Salvar o mapa como imagem PNG"><svg viewBox="0 0 24 24"><path d="M12 3v11M7.5 9.5 12 14l4.5-4.5"/><path d="M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/></svg></button>
            <button type="button" class="mapa-btn" data-acao="tela" title="Tela cheia" aria-label="Tela cheia"><svg viewBox="0 0 24 24"><path d="M8 3H3v5M16 3h5v5M8 21H3v-5M16 21h5v-5"/></svg></button>
          </div>
          <span class="mapa-status" aria-live="polite"></span>
          <div class="mapa-confirma" role="alertdialog" aria-modal="false" aria-labelledby="mapa-confirma-txt" hidden>
            <div class="mapa-confirma-cartao">
              <p id="mapa-confirma-txt"></p>
              <div class="mapa-confirma-acoes"><button type="button" class="ed-ok" data-conf="nao">Cancelar</button><button type="button" class="ed-excluir" data-conf="sim">Apagar tudo</button></div>
            </div>
          </div>
        </div>
      </div>`;
    const $mapa = el.querySelector('.mapa-leaflet');
    const $dica = el.querySelector('.mapa-dica');
    const $status = el.querySelector('.mapa-status');
    const casca = el.querySelector('.mapa-casca');

    const map = L.map($mapa, {
      maxBounds: LIMITES, maxBoundsViscosity: 0.8, minZoom: 4, maxZoom: 18,
      zoomSnap: 0.25, zoomDelta: 0.5, wheelPxPerZoomLevel: 90, attributionControl: true, zoomControl: true
    });
    map.attributionControl.setPrefix(false);
    const esri = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 18, maxNativeZoom: 18, crossOrigin: 'anonymous', attribution: 'Imagens © Esri, Maxar, Earthstar Geographics'
    });
    const nasa = L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg', {
      maxZoom: 18, maxNativeZoom: 8, crossOrigin: 'anonymous', attribution: 'Imagens: NASA Blue Marble (domínio público)'
    });
    let falhas = 0;
    esri.on('tileerror', () => { if (++falhas === 12 && map.hasLayer(esri)) { map.removeLayer(esri); nasa.addTo(map); } });
    esri.addTo(map);
    L.control.layers({ 'Satélite (alta definição)': esri, 'Relevo (NASA)': nasa }, null, { position: 'topright' }).addTo(map);
    map.createPane('panelX'); map.getPane('panelX').style.zIndex = 680;   // o X fica acima de tudo (popups: 700)
    if (estado.vista) map.setView([estado.vista.lat, estado.vista.lng], estado.vista.zoom);
    else map.fitBounds(REGIAO);

    // ------------------------------------------------------------ salvar
    let timer = null, arrastouEm = 0;
    function marcar(txt) { $status.textContent = txt; $status.classList.toggle('visivel', !!txt); }
    function salvarJa() {
      const c = map.getCenter();
      estado.vista = { lat: +c.lat.toFixed(5), lng: +c.lng.toFixed(5), zoom: map.getZoom() };
      marcar('Salvando…');
      Promise.resolve(opcoes.salvar({ vista: estado.vista, elementos: estado.elementos }))
        .then(() => { marcar('Salvo'); setTimeout(() => marcar(''), 1400); })
        .catch(e => marcar('Não salvou: ' + (e && e.message || 'erro')));
    }
    const salvar = () => { clearTimeout(timer); timer = setTimeout(salvarJa, 600); };
    map.on('moveend zoomend', salvar);

    // ------------------------------------------------------------ desenho dos elementos
    const camadas = new Map();   // id -> [layers]
    function remover(id) { (camadas.get(id) || []).forEach(l => map.removeLayer(l)); camadas.delete(id); }

    function iconeRotulado(svg, nome, cls, w, hgt, ancoraY) {
      return L.divIcon({
        className: 'mk ' + cls,
        html: `<div class="mk-corpo">${nome ? `<span class="mk-nome">${h(nome)}</span>` : ''}${svg}</div>`,
        iconSize: [w, hgt], iconAnchor: [w / 2, ancoraY]
      });
    }
    function anguloSeta(a, b) {
      const p1 = map.project(a, 10), p2 = map.project(b, 10);
      return Math.atan2(p2.y - p1.y, p2.x - p1.x) * 180 / Math.PI;
    }
    function desenhar(e) {
      remover(e.id);
      const ls = [];
      // com uma ferramenta ativa, tocar num elemento conta como tocar no mapa (ex.: seta que sai de uma cidade)
      const clicavel = (layer) => { layer.on('click', (ev) => {
        L.DomEvent.stop(ev);
        if (Date.now() - arrastouEm < 350) return;   // fim de um arraste, não um toque
        if (estado.ferramenta && estado.ferramenta !== 'selecao') aoClicarMapa(ev.latlng);
        else { selecionar(e.id); editar(e, ev.latlng); }
      }); return layer; };
      const arrastavel = (m) => {
        m.on('dragstart', () => { map.closePopup(); selecionar(e.id); });
        m.on('dragend', () => { const p = m.getLatLng(); e.lat = p.lat; e.lng = p.lng; salvar(); });
        return m;
      };
      if (e.tipo === 'local') ls.push(arrastavel(clicavel(L.marker([e.lat, e.lng], { draggable: true, icon: iconeRotulado(SVG.local, e.nome, 'mk-local', 32, 40, 40) }))));
      if (e.tipo === 'cidade') ls.push(arrastavel(clicavel(L.marker([e.lat, e.lng], { draggable: true, icon: iconeRotulado(SVG.cidade, e.nome, 'mk-cidade', 56, 46, 40) }))));
      if (e.tipo === 'monte') ls.push(arrastavel(clicavel(L.marker([e.lat, e.lng], { draggable: true, icon: iconeRotulado(SVG.monte, e.nome, 'mk-monte', 62, 44, 42) }))));
      if (e.tipo === 'tenda') ls.push(arrastavel(clicavel(L.marker([e.lat, e.lng], { draggable: true, icon: iconeRotulado(SVG.tenda, e.nome, 'mk-tenda', 50, 38, 34) }))));
      if (e.tipo === 'x') ls.push(arrastavel(clicavel(L.marker([e.lat, e.lng], { draggable: true, pane: 'panelX', icon: L.divIcon({ className: 'mk mk-x', html: SVG.x(e.cor || '#b3261e'), iconSize: [40, 40], iconAnchor: [20, 20] }) }))));
      if (e.tipo === 'texto') {
        ls.push(arrastavel(clicavel(L.marker([e.lat, e.lng], { draggable: true, icon: L.divIcon({
          className: 'mk mk-texto', iconSize: null, iconAnchor: [0, 0],
          html: `<span class="mk-texto-corpo tam-${e.tam || 'm'}" style="--c:${h(e.cor || '#ffffff')}">${h(e.texto || 'Texto')}</span>` }) }))));
      }
      if (e.tipo === 'seta' || e.tipo === 'seta-tracejada') {
        const a = L.latLng(e.pontos[0]), b = L.latLng(e.pontos[1]);
        const cor = e.cor || '#b3261e';
        ls.push(clicavel(L.polyline([a, b], { color: '#ffffff', weight: 8, opacity: 0.55, lineCap: 'round', dashArray: e.tipo === 'seta-tracejada' ? '12 10' : null, interactive: false })));
        ls.push(clicavel(L.polyline([a, b], { color: cor, weight: 4.5, lineCap: 'round', dashArray: e.tipo === 'seta-tracejada' ? '12 10' : null })));
        ls.push(clicavel(L.marker(b, { interactive: true, icon: L.divIcon({ className: 'mk mk-ponta', iconSize: [26, 26], iconAnchor: [13, 13],
          html: `<svg viewBox="0 0 26 26" style="transform:rotate(${anguloSeta(a, b)}deg)"><path d="M4 4 23 13 4 22 9 13z" fill="${h(cor)}" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>` }) })));
      }
      if (e.tipo === 'pincel') {
        ls.push(clicavel(L.polyline(e.pontos, { color: e.cor || '#f2c14e', weight: PINCEL[e.tam || 'm'], opacity: PINCEL_OPAC, lineCap: 'round', lineJoin: 'round', className: 'traco-pincel' })));
      }
      if (e.tipo === 'linha') {
        ls.push(L.polyline(e.pontos, { color: '#ffffff', weight: 7, opacity: 0.5, lineCap: 'round', dashArray: '1 11', interactive: false }));
        ls.push(clicavel(L.polyline(e.pontos, { color: e.cor || '#f2c14e', weight: 4.5, lineCap: 'round', lineJoin: 'round', dashArray: '1 11' })));
      }
      ls.forEach(l => l.addTo(map));
      camadas.set(e.id, ls);
      if (estado.selecionado === e.id) marcarSelecao(e.id, true);
      return ls;
    }
    // ------------------------------------------------------------ seleção
    function elementosDe(id) {
      return (camadas.get(id) || []).map(l => (l.getElement ? l.getElement() : l._path)).filter(Boolean);
    }
    function marcarSelecao(id, on) { elementosDe(id).forEach(n => n.classList.toggle('selecionado', on)); }
    function selecionar(id) {
      if (estado.selecionado && estado.selecionado !== id) marcarSelecao(estado.selecionado, false);
      estado.selecionado = id || null;
      if (id) marcarSelecao(id, true);
    }
    function apagarElemento(id) {
      estado.elementos = estado.elementos.filter(x => x.id !== id); remover(id);
      if (estado.selecionado === id) estado.selecionado = null;
      map.closePopup(); salvar();
    }
    estado.elementos.forEach(desenhar);

    // ------------------------------------------------------------ editor (popup)
    function editar(e, onde) {
      const temNome = ['local', 'cidade', 'tenda', 'monte'].includes(e.tipo);
      const temCor = ['texto', 'x', 'seta', 'seta-tracejada', 'linha', 'pincel'].includes(e.tipo);
      const titulo = (FERRAMENTAS.find(f => f.id === e.tipo) || {}).nome;
      const div = L.DomUtil.create('div', 'mapa-editor');
      div.innerHTML = `
        <p class="mapa-editor-titulo">${h(titulo)}</p>
        ${temNome ? `<label>Nome<input class="ed-nome" value="${h(e.nome || '')}" placeholder="${e.tipo === 'monte' ? 'Ex.: Monte Moriá' : 'Ex.: Ur dos Caldeus'}" maxlength="60"></label>` : ''}
        ${e.tipo === 'texto' ? `<label>Texto<textarea class="ed-texto" rows="2" maxlength="140">${h(e.texto || '')}</textarea></label>
          <div class="ed-tams" role="group" aria-label="Tamanho">${['p', 'm', 'g'].map(t => `<button type="button" data-tam="${t}" class="${(e.tam || 'm') === t ? 'ativo' : ''}">${{ p: 'Pequeno', m: 'Médio', g: 'Grande' }[t]}</button>`).join('')}</div>` : ''}
        ${e.tipo === 'pincel' ? `<div class="ed-tams" role="group" aria-label="Espessura">${['p', 'm', 'g'].map(t => `<button type="button" data-tam="${t}" class="${(e.tam || 'm') === t ? 'ativo' : ''}">${{ p: 'Fino', m: 'Médio', g: 'Largo' }[t]}</button>`).join('')}</div>` : ''}
        ${temCor ? `<div class="ed-cores">${CORES.map(c => `<button type="button" data-cor="${c}" style="--c:${c}" class="${(e.cor || '') === c ? 'ativa' : ''}" aria-label="Cor ${c}"></button>`).join('')}<label class="mapa-cor-livre"><input type="color" value="${h(e.cor || '#b3261e')}"></label></div>` : ''}
        <div class="ed-acoes"><button type="button" class="ed-excluir">Excluir</button><button type="button" class="ed-ok">Pronto</button></div>`;
      L.DomEvent.disableClickPropagation(div); L.DomEvent.disableScrollPropagation(div);
      const pos = onde || (e.pontos ? L.latLng(e.pontos[e.pontos.length - 1]) : L.latLng(e.lat, e.lng));
      const pop = L.popup({ className: 'mapa-popup', closeButton: true, autoPanPadding: [24, 24], offset: [0, temNome ? -30 : -6], minWidth: 220 })
        .setLatLng(pos).setContent(div).openOn(map);
      const aplicar = () => {
        const n = div.querySelector('.ed-nome'); if (n) e.nome = n.value.trim();
        const t = div.querySelector('.ed-texto'); if (t) e.texto = t.value.trim() || 'Texto';
        desenhar(e); salvar();
      };
      div.addEventListener('input', aplicar);
      div.querySelectorAll('[data-cor]').forEach(b => b.onclick = () => {
        e.cor = b.dataset.cor; div.querySelectorAll('[data-cor]').forEach(x => x.classList.toggle('ativa', x === b)); aplicar();
      });
      const livre = div.querySelector('input[type=color]'); if (livre) livre.oninput = () => { e.cor = livre.value; aplicar(); };
      div.querySelectorAll('[data-tam]').forEach(b => b.onclick = () => {
        e.tam = b.dataset.tam; div.querySelectorAll('[data-tam]').forEach(x => x.classList.toggle('ativo', x === b)); aplicar();
      });
      div.querySelector('.ed-excluir').onclick = () => apagarElemento(e.id);
      pop.on('remove', () => { if (estado.selecionado === e.id) selecionar(null); });
      div.querySelector('.ed-ok').onclick = () => map.closePopup(pop);
      div.addEventListener('keydown', ev => { if (ev.key === 'Enter' && !ev.shiftKey && ev.target.tagName === 'INPUT') { ev.preventDefault(); map.closePopup(pop); } });
      const foco = div.querySelector('.ed-nome, .ed-texto'); if (foco) setTimeout(() => { foco.focus(); foco.select(); }, 60);
    }

    // ------------------------------------------------------------ ferramentas
    let inicioSeta = null, previa = null, tracando = null;
    function escolher(id) {
      // a Seleção é o modo de repouso: sair de outra ferramenta volta para ela
      estado.ferramenta = (!id || estado.ferramenta === id) ? 'selecao' : id;
      if (estado.ferramenta !== 'selecao') { selecionar(null); map.closePopup(); }
      el.querySelectorAll('.mapa-ferr').forEach(b => {
        const on = b.dataset.ferr === estado.ferramenta;
        b.classList.toggle('ativa', on); b.setAttribute('aria-pressed', on);
      });
      cancelarSeta();
      const f = FERRAMENTAS.find(x => x.id === estado.ferramenta);
      $dica.textContent = f.dica;
      casca.classList.toggle('desenhando', desenhoLivre(estado.ferramenta));
      casca.classList.toggle('com-ferramenta', estado.ferramenta !== 'selecao');
      if (desenhoLivre(estado.ferramenta)) { map.dragging.disable(); } else { map.dragging.enable(); }
      // com uma ferramenta de desenho, dois toques rápidos não devem dar zoom
      if (estado.ferramenta === 'selecao') map.doubleClickZoom.enable(); else map.doubleClickZoom.disable();
      if (window.gsap && !reduzir) gsap.fromTo($dica, { autoAlpha: 0, y: 4 }, { autoAlpha: 1, y: 0, duration: 0.25, ease: 'power3.out' });
    }
    function cancelarSeta() { inicioSeta = null; if (previa) { map.removeLayer(previa); previa = null; } }
    function novo(e) { estado.elementos.push(e); desenhar(e); salvar(); return e; }

    el.querySelectorAll('.mapa-ferr').forEach(b => b.onclick = () => escolher(b.dataset.ferr));
    el.querySelectorAll('.mapa-painel [data-cor]').forEach(b => b.onclick = () => {
      estado.cor = b.dataset.cor; localStorage_set('mapa-cor', estado.cor);
      el.querySelectorAll('.mapa-painel [data-cor]').forEach(x => x.classList.toggle('ativa', x === b));
    });
    el.querySelector('.mapa-painel input[type=color]').oninput = (ev) => {
      estado.cor = ev.target.value; localStorage_set('mapa-cor', estado.cor);
      el.querySelectorAll('.mapa-painel [data-cor]').forEach(x => x.classList.remove('ativa'));
    };
    const $conf = el.querySelector('.mapa-confirma');
    function fecharConfirma() { $conf.hidden = true; }
    el.querySelector('[data-acao="limpar"]').onclick = () => {
      const n = estado.elementos.length;
      if (!n) { marcar('O mapa já está vazio'); setTimeout(() => marcar(''), 1400); return; }
      escolher(null); map.closePopup();
      $conf.querySelector('p').textContent = `Apagar ${n === 1 ? 'o elemento' : 'todos os ' + n + ' elementos'} deste versículo? A posição e o zoom do mapa continuam.`;
      $conf.hidden = false;
      if (window.gsap && !reduzir) gsap.fromTo($conf.firstElementChild, { autoAlpha: 0, y: 10, scale: 0.97 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.24, ease: 'power3.out' });
      $conf.querySelector('[data-conf="nao"]').focus();
    };
    $conf.onclick = (ev) => {
      const b = ev.target.closest('[data-conf]');
      if (!b && ev.target !== $conf) return;
      if (b && b.dataset.conf === 'sim') {
        estado.elementos.forEach(e => remover(e.id));
        estado.elementos = []; estado.selecionado = null;
        clearTimeout(timer); salvarJa();
      }
      fecharConfirma();
    };
    L.DomEvent.disableClickPropagation($conf);
    el.querySelector('[data-acao="recorte"]').onclick = () => map.flyToBounds(REGIAO, { duration: reduzir ? 0 : 0.8 });
    el.querySelector('[data-acao="png"]').onclick = () => exportarPNG();
    el.querySelector('[data-acao="tela"]').onclick = () => {
      casca.classList.toggle('tela-cheia');
      document.body.classList.toggle('mapa-tela-cheia', casca.classList.contains('tela-cheia'));
      setTimeout(() => map.invalidateSize(), 60);
    };

    map.on('click', (ev) => { if (Date.now() - arrastouEm > 350) aoClicarMapa(ev.latlng); });
    function aoClicarMapa(ll) {
      const ev = { latlng: ll };
      const f = estado.ferramenta;
      if (f === 'selecao') { selecionar(null); return; }
      if (!f || desenhoLivre(f)) return;
      const { lat, lng } = ll;
      if (['local', 'cidade', 'tenda', 'monte'].includes(f)) { const e = novo({ id: uid(), tipo: f, lat, lng, nome: '' }); escolher(null); selecionar(e.id); editar(e); }
      else if (f === 'texto') { const e = novo({ id: uid(), tipo: 'texto', lat, lng, texto: 'Texto', cor: estado.cor === '#2a1c10' ? '#ffffff' : estado.cor, tam: 'm' }); escolher(null); selecionar(e.id); editar(e); }
      else if (f === 'x') { novo({ id: uid(), tipo: 'x', lat, lng, cor: estado.cor }); }
      else if (f === 'seta' || f === 'seta-tracejada') {
        if (!inicioSeta) {
          inicioSeta = ev.latlng;
          previa = L.polyline([inicioSeta, inicioSeta], { color: estado.cor, weight: 3, dashArray: '4 6', opacity: 0.8, interactive: false }).addTo(map);
          $dica.textContent = 'Agora toque no ponto para onde a seta aponta.';
        } else {
          novo({ id: uid(), tipo: f, pontos: [[inicioSeta.lat, inicioSeta.lng], [lat, lng]], cor: estado.cor });
          cancelarSeta();
          $dica.textContent = (FERRAMENTAS.find(x => x.id === f) || {}).dica;
        }
      }
    }
    map.on('mousemove', (ev) => { if (previa && inicioSeta) previa.setLatLngs([inicioSeta, ev.latlng]); });

    // linha livre: desenhar com ponteiro (dedo ou mouse)
    const cont = map.getContainer();
    function ptDe(ev) { const r = cont.getBoundingClientRect(); return map.containerPointToLatLng([ev.clientX - r.left, ev.clientY - r.top]); }
    function aoDescer(ev) {
      if (!desenhoLivre(estado.ferramenta) || ev.button > 0) return;
      if (ev.target.closest('.leaflet-control, .leaflet-popup')) return;
      ev.preventDefault();
      cont.setPointerCapture && cont.setPointerCapture(ev.pointerId);
      const p = ptDe(ev);
      const pincel = estado.ferramenta === 'pincel';
      const estilo = pincel
        ? { color: estado.cor, weight: PINCEL.m, opacity: PINCEL_OPAC, lineCap: 'round', lineJoin: 'round', interactive: false }
        : { color: estado.cor, weight: 4.5, lineCap: 'round', dashArray: '1 11', interactive: false };
      tracando = { tipo: estado.ferramenta, pts: [p], ultimo: [ev.clientX, ev.clientY], layer: L.polyline([p, p], estilo).addTo(map) };
    }
    function aoMover(ev) {
      if (!tracando) return;
      const [x0, y0] = tracando.ultimo;
      if (Math.hypot(ev.clientX - x0, ev.clientY - y0) < 4) return;
      tracando.ultimo = [ev.clientX, ev.clientY];
      tracando.pts.push(ptDe(ev)); tracando.layer.setLatLngs(tracando.pts);
    }
    function aoSubir() {
      if (!tracando) return;
      map.removeLayer(tracando.layer);
      const pts = tracando.pts.length > 1 ? tracando.pts : (tracando.tipo === 'pincel' ? [tracando.pts[0], tracando.pts[0]] : null);   // um toque com o pincel faz um ponto
      if (pts) {
        const e = { id: uid(), tipo: tracando.tipo, cor: estado.cor, pontos: pts.map(p => [+p.lat.toFixed(5), +p.lng.toFixed(5)]) };
        if (tracando.tipo === 'pincel') e.tam = 'm';
        novo(e);
      }
      tracando = null;
    }
    // Seleção: arrastar uma seta ou linha selecionada muda o desenho de lugar (o mapa não se move junto)
    let movendo = null;
    function aoDescerSelecao(ev) {
      if (estado.ferramenta !== 'selecao' || !estado.selecionado || ev.button > 0) return;
      const e = estado.elementos.find(x => x.id === estado.selecionado);
      if (!e || !e.pontos || !elementosDe(e.id).some(n => n.contains(ev.target))) return;
      ev.stopPropagation(); ev.preventDefault();
      map.closePopup(); selecionar(e.id); map.dragging.disable();
      movendo = { e, ini: map.mouseEventToLatLng(ev), orig: e.pontos.map(p => p.slice()), mexeu: false, id: ev.pointerId };
      cont.setPointerCapture && cont.setPointerCapture(ev.pointerId);
    }
    function aoMoverSelecao(ev) {
      if (!movendo || ev.pointerId !== movendo.id) return;
      const p = map.mouseEventToLatLng(ev), dLat = p.lat - movendo.ini.lat, dLng = p.lng - movendo.ini.lng;
      movendo.e.pontos = movendo.orig.map(([a, b]) => [+(a + dLat).toFixed(5), +(b + dLng).toFixed(5)]);
      movendo.mexeu = true;
      desenhar(movendo.e);
    }
    function aoSubirSelecao(ev) {
      if (!movendo || ev.pointerId !== movendo.id) return;
      const { e, mexeu } = movendo; movendo = null;
      map.dragging.enable();
      if (mexeu) { arrastouEm = Date.now(); salvar(); }
    }
    cont.addEventListener('pointerdown', aoDescerSelecao, true);
    window.addEventListener('pointermove', aoMoverSelecao);
    window.addEventListener('pointerup', aoSubirSelecao);
    window.addEventListener('pointercancel', aoSubirSelecao);
    cont.addEventListener('pointerdown', aoDescer);
    cont.addEventListener('pointermove', aoMover);
    cont.addEventListener('pointerup', aoSubir);
    cont.addEventListener('pointercancel', aoSubir);
    const aoTecla = (ev) => {
      if (ev.key === 'Escape') {
        if (!$conf.hidden) return fecharConfirma();
        if (estado.ferramenta !== 'selecao') return escolher(null);
        selecionar(null); map.closePopup();
      }
      // Delete apaga o elemento selecionado (fora de campos de texto)
      if ((ev.key === 'Delete' || ev.key === 'Backspace') && estado.selecionado && !/INPUT|TEXTAREA/.test((ev.target && ev.target.tagName) || '')) {
        ev.preventDefault(); apagarElemento(estado.selecionado);
      }
    };
    document.addEventListener('keydown', aoTecla);
    escolher('selecao');

    // ------------------------------------------------------------ exportar PNG (exatamente o que está na tela)
    const carregarImg = (src) => new Promise((ok, falha) => { const i = new Image(); i.onload = () => ok(i); i.onerror = falha; i.src = src; });
    const svgParaImg = (svg, w, hgt) => {
      const c = svg.cloneNode(true);
      c.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      c.setAttribute('width', w); c.setAttribute('height', hgt);
      c.removeAttribute('style'); c.classList.remove('selecionado');
      c.querySelectorAll('.selecionado').forEach(n => n.classList.remove('selecionado'));
      return carregarImg('data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(c)));
    };
    function rotaRet(ctx, x, y, w, hgt, r) {
      ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + hgt, r); ctx.arcTo(x + w, y + hgt, x, y + hgt, r);
      ctx.arcTo(x, y + hgt, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
    }
    async function compor(comMapa) {
      const tam = map.getSize(), escala = Math.max(2, Math.min(3, window.devicePixelRatio || 1));
      const cv = document.createElement('canvas');
      cv.width = Math.round(tam.x * escala); cv.height = Math.round(tam.y * escala);
      const ctx = cv.getContext('2d'); ctx.scale(escala, escala);
      ctx.fillStyle = '#0f1d2c'; ctx.fillRect(0, 0, tam.x, tam.y);
      const o = cont.getBoundingClientRect();
      const rel = (n) => { const r = n.getBoundingClientRect(); return { x: r.left - o.left, y: r.top - o.top, w: r.width, h: r.height }; };
      if (comMapa) {
        cont.querySelectorAll('.leaflet-tile-pane .leaflet-layer').forEach(camada => {
          const op = parseFloat(getComputedStyle(camada).opacity) || 1;
          camada.querySelectorAll('img.leaflet-tile-loaded').forEach(img => {
            const r = rel(img); ctx.globalAlpha = op;
            ctx.drawImage(img, r.x, r.y, r.w, r.h);
          });
        });
        ctx.globalAlpha = 1;
      }
      // traços (setas, linhas, pincel)
      for (const svg of cont.querySelectorAll('.leaflet-overlay-pane svg')) {
        const r = rel(svg); if (!r.w) continue;
        const img = await svgParaImg(svg, r.w, r.h);
        ctx.drawImage(img, r.x, r.y, r.w, r.h);
      }
      // marcadores, na ordem das camadas (o X fica por cima)
      const icones = [...cont.querySelectorAll('.leaflet-marker-pane .leaflet-marker-icon'), ...cont.querySelectorAll('.leaflet-panelX-pane .leaflet-marker-icon')];
      for (const ic of icones) {
        const svg = ic.querySelector('svg');
        if (svg) {
          const caixa = svg.parentElement === ic ? ic : svg.parentElement;
          const w = caixa.offsetWidth, hgt = caixa.offsetHeight, r = rel(caixa);
          const img = await svgParaImg(svg, w, hgt);
          const giro = (svg.style.transform.match(/rotate\(([-\d.]+)deg\)/) || [])[1];
          ctx.save();
          ctx.shadowColor = 'rgba(0,0,0,.45)'; ctx.shadowBlur = 4; ctx.shadowOffsetY = 2;
          ctx.translate(r.x + r.w / 2, r.y + r.h / 2);
          if (giro) ctx.rotate(parseFloat(giro) * Math.PI / 180);
          ctx.drawImage(img, -w / 2, -hgt / 2, w, hgt);
          ctx.restore();
        }
        const nome = ic.querySelector('.mk-nome');
        if (nome) {
          const r = rel(nome), cs = getComputedStyle(nome);
          ctx.save();
          ctx.shadowColor = 'rgba(0,0,0,.35)'; ctx.shadowBlur = 6; ctx.shadowOffsetY = 2;
          ctx.fillStyle = cs.backgroundColor; rotaRet(ctx, r.x, r.y, r.w, r.h, 6); ctx.fill();
          ctx.restore();
          ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`; ctx.fillStyle = cs.color;
          ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.fillText(nome.textContent, r.x + r.w / 2, r.y + r.h / 2 + 0.5);
        }
        const txt = ic.querySelector('.mk-texto-corpo');
        if (txt) {
          const r = rel(txt), cs = getComputedStyle(txt);
          const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
          const linhas = txt.textContent.split('\n');
          ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
          ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
          linhas.forEach((l, i) => {
            const y = r.y + lh * (i + 0.5);
            ctx.save();
            ctx.shadowColor = 'rgba(0,0,0,.9)';
            [[0, 3], [1, 3], [0, 10]].forEach(([dy, blur]) => { ctx.shadowOffsetY = dy; ctx.shadowBlur = blur; ctx.fillStyle = cs.color; ctx.fillText(l, r.x, y); });
            ctx.restore();
            ctx.fillStyle = cs.color; ctx.fillText(l, r.x, y);
          });
        }
      }
      // créditos das imagens (exigidos pelos provedores)
      const cred = (cont.querySelector('.leaflet-control-attribution') || {}).textContent || '';
      if (cred) {
        ctx.font = '500 10px "Source Sans 3", sans-serif'; ctx.textAlign = 'right'; ctx.textBaseline = 'bottom';
        const w = ctx.measureText(cred).width + 10;
        ctx.fillStyle = 'rgba(255,255,255,.75)'; ctx.fillRect(tam.x - w, tam.y - 15, w, 15);
        ctx.fillStyle = '#333'; ctx.fillText(cred, tam.x - 5, tam.y - 2);
      }
      return cv;
    }
    let exportando = false;
    async function exportarPNG() {
      if (exportando) return; exportando = true;
      const btn = el.querySelector('[data-acao="png"]'); btn.classList.add('ocupado');
      map.closePopup();
      marcar('Gerando a imagem…');
      try {
        if (document.fonts && document.fonts.ready) await document.fonts.ready;
        let cv = await compor(true), blob = null, semMapa = false;
        try { blob = await new Promise((ok, falha) => { try { cv.toBlob(ok, 'image/png'); } catch (e) { falha(e); } }); }
        catch (e) { semMapa = true; }
        if (!blob) { semMapa = true; cv = await compor(false); blob = await new Promise(ok => cv.toBlob(ok, 'image/png')); }
        const nome = (opcoes.nomeArquivo || 'mapa') + '.png';
        const arq = typeof File === 'function' ? new File([blob], nome, { type: 'image/png' }) : null;
        const toque = matchMedia('(pointer: coarse)').matches;
        if (toque && arq && navigator.canShare && navigator.canShare({ files: [arq] })) {
          try { await navigator.share({ files: [arq], title: nome }); } catch (e) { /* cancelado */ }
        } else {
          const url = URL.createObjectURL(blob), a = document.createElement('a');
          a.href = url; a.download = nome; document.body.appendChild(a); a.click(); a.remove();
          setTimeout(() => URL.revokeObjectURL(url), 4000);
        }
        marcar(semMapa ? 'Imagem salva sem o fundo de satélite (o servidor não liberou)' : 'Imagem salva');
        setTimeout(() => marcar(''), semMapa ? 4000 : 1600);
      } catch (e) {
        marcar('Não foi possível gerar a imagem'); setTimeout(() => marcar(''), 3000);
      } finally { exportando = false; btn.classList.remove('ocupado'); }
    }

    // o mapa acompanha o tamanho da área (painel mais alto, tela cheia, girar o celular)
    const ro = window.ResizeObserver ? new ResizeObserver(() => map.invalidateSize({ pan: false })) : null;
    if (ro) ro.observe($mapa);
    setTimeout(() => map.invalidateSize(), 50);
    if (window.gsap && !reduzir) gsap.from(el.querySelectorAll('.mapa-ferr'), { autoAlpha: 0, y: 6, duration: 0.3, stagger: 0.025, ease: 'power3.out', clearProps: 'all' });

    return {
      map,
      destruir() {
        if (timer) { clearTimeout(timer); salvarJa(); }
        document.removeEventListener('keydown', aoTecla);
        if (ro) ro.disconnect();
        window.removeEventListener('pointermove', aoMoverSelecao);
        window.removeEventListener('pointerup', aoSubirSelecao);
        window.removeEventListener('pointercancel', aoSubirSelecao);
        document.body.classList.remove('mapa-tela-cheia');
        map.remove();
      }
    };
  }

  function localStorage_get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function localStorage_set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* sem armazenamento */ } }

  window.MapaExegese = { montar };
})();
