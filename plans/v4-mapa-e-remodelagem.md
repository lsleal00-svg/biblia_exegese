# v4 — Mapa por versículo, colunas recolhíveis e remodelagem

## Pedidos (Wilson, 26/10/2026)
1. Lápis acima de cada palavra em português da coluna Texto Bíblico (edição manual).
2. Lápis no título "Texto Bíblico" para renomear a coluna.
3. Olho no canto superior direito de Hebraico, Strong Hebraico, LXX e Strong Grego: recolhe a coluna para a esquerda (fica oculta numa faixa estreita) e reabre.
4. Mapa (recorte Egito–Mesopotâmia, imagem de satélite em alta definição, zoom livre):
   - zoom/posição salvos por versículo;
   - aba "Elementos": localização (com nome acima), texto livre (com cor), X (sempre por cima), cidade fortificada (com nome), acampamento/tenda (com nome), seta reta e seta pontilhada (com cor), linha pontilhada livre desenhada à mão;
   - tudo salvo no versículo.
5. Remodelagem visual do site, principalmente a tabela.

## Decisões técnicas
- Leaflet 1.9.4 (cdnjs). Imagens: Esri World Imagery (alta definição, com atribuição) e NASA GIBS Blue Marble (domínio público) como reserva. Limites: lat 22–42, lon 20–56; zoom 4–18.
- Tabela nova `mapas` (por usuário e versículo, vista + elementos em jsonb) e `preferencias` (título da coluna, colunas recolhidas). Ambas com RLS.
- Setas: polyline + ponta (divIcon SVG girado pelo ângulo projetado). X numa pane própria acima das demais.
- Linha livre: arrastar com dedo/mouse com o mapa travado durante o desenho.
- Salvamento com debounce de 600ms + indicador "Salvo".
- GSAP 3.12.5 (cdnjs) para modais, recolher colunas e painel; respeita prefers-reduced-motion.

## Verificação
- Playwright (Chromium) em modo demonstração: desktop 1400px e celular 390px. Tiles não carregam no container (sem internet), então é testada a interface; o carregamento das imagens fica para o navegador do usuário.
