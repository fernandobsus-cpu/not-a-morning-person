-- Not a Morning Person · Assignment 2: partidas en la nube
-- Correr UNA vez en Supabase → SQL Editor → New query → Run.
-- Cada fila = una partida terminada (ganada o perdida) por un usuario con sesión.
-- Las reglas del schema JSON acordado viven aquí como CHECK constraints:
-- si el juego manda algo fuera de rango, la base de datos lo rechaza.

create table if not exists public.partidas (
  id                   bigint generated always as identity primary key,
  user_id              uuid not null default auth.uid() references auth.users (id) on delete cascade,
  fecha                timestamptz not null default now(),
  dificultad           text not null check (dificultad in ('normal', 'hard')),
  gano                 boolean not null,
  causa                text check (causa in ('vidas', 'tiempo')),
  misiones_completadas int not null check (misiones_completadas between 0 and 9),
  vidas_perdidas       int not null check (vidas_perdidas between 0 and 3),
  vidas_restantes      int not null check (vidas_restantes between 0 and 3),
  segundos_restantes   int not null check (segundos_restantes between 0 and 180),
  uso_snooze           boolean not null,
  emboscadas           int not null check (emboscadas >= 0),
  emboscadas_ganadas   int not null check (emboscadas_ganadas >= 0),
  vida_perdida_por     text[] not null default '{}',

  constraint emboscadas_coherentes check (emboscadas_ganadas <= emboscadas),
  -- Si ganó: sin causa y 9 misiones. Si perdió: causa obligatoria.
  -- (Perder con 9 misiones es posible: el tiempo puede acabarse en la animación final.)
  constraint resultado_coherente check (
    (gano and causa is null and misiones_completadas = 9)
    or (not gano and causa is not null)
  ),
  -- Perder por vidas = 0 vidas restantes.
  constraint vidas_coherentes check (causa is distinct from 'vidas' or vidas_restantes = 0),
  -- Un culpable por cada vida perdida, y solo culpables conocidos.
  constraint culpables_validos check (
    vida_perdida_por <@ array['shrum', 'ishmun', 'shmane', 'baba', 'torpeza']::text[]
    and coalesce(array_length(vida_perdida_por, 1), 0) = vidas_perdidas
  )
);

create index if not exists partidas_user_dif_idx on public.partidas (user_id, dificultad, fecha desc);

-- RLS: cada usuario solo inserta y lee SUS partidas. Nadie edita ni borra (no hay políticas para eso).
alter table public.partidas enable row level security;

drop policy if exists "insertar mis partidas" on public.partidas;
create policy "insertar mis partidas" on public.partidas
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "leer mis partidas" on public.partidas;
create policy "leer mis partidas" on public.partidas
  for select to authenticated
  using ((select auth.uid()) = user_id);

-- Permisos explícitos. Supabase da ALL por defecto a anon y authenticated en tablas nuevas;
-- se quitan y se deja solo leer e insertar con sesión (así update/delete fallan con "permission denied").
revoke all on public.partidas from anon, authenticated;
grant select, insert on public.partidas to authenticated;
