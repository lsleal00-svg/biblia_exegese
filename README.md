# Bíblia & Exegese — Pentateuco

Aplicativo web de estudo exegético do Antigo Testamento. Interface no **GitHub Pages**, login e dados do usuário no **Supabase**.

## O que já funciona

- Login com **GitHub** (via Supabase) ou e-mail e senha.
- Estante com os 39 livros do AT na ordem da **Bíblia Hebraica** (Torá, Profetas Anteriores, Profetas Posteriores, Os Doze, Escritos). Todo o Pentateuco (Gênesis a Deuteronômio) está aberto. Cada divisão tem a sua cor na estante.
- Livro → **capítulo** → **versículo**, pela versificação portuguesa (Almeida / Bíblia Livre).
- Tabela por versículo, com uma linha para cada palavra hebraica:
  - **Texto Bíblico**: já vem com a palavra da Bíblia Livre que corresponde a cada termo hebraico (por alinhamento automático), e você pode corrigir. O **+** cria colunas de tradução suas.
  - **Hebraico**: texto original, transliteração, raiz com as traduções possíveis e ocorrências (no livro / no AT).
  - **Strong Hebraico**: número, traduções do termo e morfologia em português.
  - **LXX**: todas as palavras gregas do versículo (Rahlfs), cada uma na linha do termo hebraico que ela verte. A coluna **Strong Grego** mostra o número, as traduções e a morfologia da palavra principal.
  - As traduções possíveis vêm do léxico de Strong vertido para o português (`tools/strong_pt.tsv`), somadas às traduções mais frequentes da Bíblia Livre.
  - **Dicionários e Léxicos / Comentários exegéticos**: começam vazios. Você cadastra as obras, e cada uma vira uma coluna.
- Colunas compactas para celular. Há barra de rolagem horizontal também no topo da tabela, e as duas linhas de cabeçalho ficam congeladas.
- Todas as colunas têm a mesma largura. Texto longo aparece com reticências e abre completo quando você toca nele.
- Citações: na primeira vez, o app pede a obra e a referência completa. Depois disso, a mesma obra só pede **tipo (direta/indireta)** e **página**, e a página entra no fim da referência automaticamente.
- Seção inferior: **Espírito de Profecia**, **Contexto Histórico** (bloco "Ano" já vem pronto, e você pode criar blocos de Rei, Cidade, Região, Tribo, Profetas ou um título seu, além das citações teóricas), **Mapa** e **Aplicação** (seus comentários homiléticos). Cada item tem botões de editar, excluir e copiar.
- **Mapa** do recorte Egito–Mesopotâmia em satélite de alta definição. O zoom e a posição ficam salvos em cada versículo. A aba **Elementos** tem localização com nome, texto com cor e tamanho, X (sempre por cima), cidade fortificada com nome, acampamento com nome, seta reta, seta pontilhada e linha pontilhada livre, pincel transparente para destacar regiões, todos com cor. Ferramenta Seleção para editar, mover ou apagar; Limpar tudo; e botão para salvar o mapa como imagem PNG, exatamente no recorte da tela. Tudo fica salvo no versículo.
- Lápis em cada palavra da coluna Texto Bíblico e no título dela, que pode ser renomeado. O olho nas colunas Hebraico, Strong Hebraico, LXX e Strong Grego recolhe a coluna numa faixa estreita; tocando nela, a coluna volta.
- Modo demonstração sem login: `.../?demo=1`. Os dados ficam só no navegador.

## Como publicar

### 1. Supabase
1. Abra **SQL Editor → New query**, cole o conteúdo de `supabase/schema.sql` e clique em **Run**. Rode de novo a cada versão nova: o script só cria o que falta e não apaga dados. A v4 criou as tabelas `mapas` e `preferencias`.
2. Em **Authentication → URL Configuration**, coloque em **Site URL** o endereço do seu GitHub Pages (ex.: `https://SEU-USUARIO.github.io/biblia-exegese/`) e adicione esse mesmo endereço em **Redirect URLs**.
3. Para entrar com GitHub:
   - No GitHub: **Settings → Developer settings → OAuth Apps → New OAuth App**.
     - Homepage URL: o endereço do Pages.
     - Authorization callback URL: `https://fqesmehjosivwflxpwel.supabase.co/auth/v1/callback`
   - Copie o **Client ID**, gere um **Client secret** e cole os dois no Supabase em **Authentication → Providers → GitHub**. Depois ative o provedor.

### 2. GitHub Pages
1. Crie um repositório (ex.: `biblia-exegese`) e envie **todo o conteúdo desta pasta**.
2. Vá em **Settings → Pages → Branch: main / (root)** e salve.

## Fontes e licenças
- Português: **Bíblia Livre (BLIVRE)**, © Diego Santos, Mario Sérgio e Marco Teles, 2018. Licença CC BY 4.0. A atribuição é obrigatória e já aparece no app.
- Hebraico: Westminster Leningrad Codex (domínio público). Lemas e morfologia da OSHB (CC BY 4.0).
- Septuaginta: Rahlfs 1935, projeto CenterBLC/LXX (MIT). Nos trechos que a LXX põe em outra ordem (Êx 35-40, Nm 1, 6, 10, 26, Dt 5 etc.), a correspondência vem da tabela TVTMS do STEPBible (CC BY) e é conferida pelo alinhamento.
- Versículos da Bíblia Livre que faltavam no corpus eBible (Gn 31:55, Êx 8:29-32, Êx 22:31, Lv 6:24-30, Nm 16:36-50, Nm 29:40, Dt 12:32, 22:30, 29:29): `tools/blivre_faltantes.tsv`, do PorBLivre (scrollmapper/bible_databases).
- Léxico Strong (1890), hebraico e grego: domínio público.
- Mapa: Leaflet 1.9.4 (BSD) e GSAP 3.12.5 em `vendor/`. Imagens © Esri, Maxar, Earthstar Geographics, e NASA Blue Marble (domínio público).

## Para gerar os próximos livros
O arquivo `tools/build_data.py` (requer `text-fabric`, `spacy`, `simplemma` e o modelo `pt_core_news_sm`) gera `data/livros/<abrev>.json`. A pasta de fontes precisa ter também `tvtms.txt` (TVTMS do STEPBible). Exemplo: `python3 tools/build_data.py <fontes> data/livros Josh`.
Antes, ajuste em `js/livros.js` o `arquivo` e o `ativo: true` do livro. Para cada livro novo, confira os versículos que faltam no corpus (sobras de capítulo) e acrescente-os em `tools/blivre_faltantes.tsv`.
