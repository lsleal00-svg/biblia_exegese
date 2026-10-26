-- =====================================================================
-- Bíblia & Exegese — Etapa 1
-- Cole tudo no Supabase: SQL Editor > New query > Run.
-- Pode rodar de novo sem perder dados (usa "if not exists").
-- Cada usuário só enxerga e altera os próprios registros (RLS).
-- =====================================================================

-- 1) Colunas de tradução criadas pelo usuário (ao lado de "Texto Bíblico")
create table if not exists public.traducoes_usuario (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  nome        text not null,
  ordem       int  not null default 0,
  criado_em   timestamptz not null default now()
);

-- 2) Conteúdo das células da tabela (texto bíblico, traduções do usuário,
--    escolha da palavra da LXX). Uma linha = uma célula.
--    coluna: 'pt' | 'trad:<uuid>' | 'lxx'
create table if not exists public.celulas (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null default auth.uid() references auth.users(id) on delete cascade,
  livro         text not null,
  capitulo      int  not null,
  versiculo     int  not null,
  coluna        text not null,
  linha         int  not null,
  valor         text not null default '',
  atualizado_em timestamptz not null default now(),
  unique (user_id, livro, capitulo, versiculo, coluna, linha)
);

-- 3) Léxico pessoal: significado em português de cada número Strong.
--    Escrito uma vez, vale em todos os versículos onde a palavra aparece.
--    campo: 'significado' | 'raiz'
create table if not exists public.lexico_usuario (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null default auth.uid() references auth.users(id) on delete cascade,
  strong        text not null,
  campo         text not null check (campo in ('significado','raiz')),
  valor         text not null default '',
  atualizado_em timestamptz not null default now(),
  unique (user_id, strong, campo)
);

-- 4) Obras (bibliografia). Dicionários/léxicos e comentários exegéticos
--    viram colunas na tabela; obras "gerais" servem às outras citações
--    (Espírito de Profecia, Contexto Histórico etc.).
create table if not exists public.obras (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  titulo      text not null,
  referencia  text not null,
  categoria   text not null default 'geral' check (categoria in ('dicionario','comentario','geral','ep')),
  ordem       int  not null default 0,
  criado_em   timestamptz not null default now()
);

-- 5) Citações. Ficam presas ao versículo.
--    secao: 'celula' (coluna de dicionário/comentário) | 'ep' | 'contexto'
create table if not exists public.citacoes (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  obra_id     uuid not null references public.obras(id) on delete cascade,
  livro       text not null,
  capitulo    int  not null,
  versiculo   int  not null,
  secao       text not null check (secao in ('celula','ep','contexto')),
  linha       int,
  tipo        text not null check (tipo in ('direta','indireta')),
  pagina      text not null,
  texto       text not null,
  criado_em   timestamptz not null default now()
);

-- 6) Blocos de texto do versículo: Contexto Histórico (Ano, Rei, Cidade…)
--    e Aplicação (comentários homiléticos pessoais).
create table if not exists public.blocos (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  livro       text not null,
  capitulo    int  not null,
  versiculo   int  not null,
  secao       text not null check (secao in ('contexto','aplicacao')),
  titulo_tipo text not null default 'personalizado',
  titulo      text not null default '',
  conteudo    text not null default '',
  ordem       int  not null default 0,
  criado_em   timestamptz not null default now()
);

create index if not exists celulas_ref   on public.celulas  (user_id, livro, capitulo, versiculo);
create index if not exists citacoes_ref  on public.citacoes (user_id, livro, capitulo, versiculo);
create index if not exists blocos_ref    on public.blocos   (user_id, livro, capitulo, versiculo);

-- ---------------------------------------------------------------- RLS
do $$
declare t text;
begin
  foreach t in array array['traducoes_usuario','celulas','lexico_usuario','obras','citacoes','blocos'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists "dono le" on public.%I', t);
    execute format('drop policy if exists "dono insere" on public.%I', t);
    execute format('drop policy if exists "dono altera" on public.%I', t);
    execute format('drop policy if exists "dono apaga" on public.%I', t);
    execute format('create policy "dono le" on public.%I for select using (auth.uid() = user_id)', t);
    execute format('create policy "dono insere" on public.%I for insert with check (auth.uid() = user_id)', t);
    execute format('create policy "dono altera" on public.%I for update using (auth.uid() = user_id) with check (auth.uid() = user_id)', t);
    execute format('create policy "dono apaga" on public.%I for delete using (auth.uid() = user_id)', t);
  end loop;
end $$;
