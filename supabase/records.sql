-- Not a Morning Person · Assignment 3: récord global en Supabase (reemplaza Netlify Blobs).
-- Correr UNA vez en Supabase → SQL Editor → New query → Run.
-- Una fila por dificultad. Solo la función de Vercel (api/record.js, con la llave secreta) puede escribir.

create table if not exists public.records (
  dificultad text primary key check (dificultad in ('normal', 'hard')),
  segundos   int  not null check (segundos between 0 and 180),
  nombre     text not null check (char_length(nombre) between 1 and 30),
  fecha      timestamptz not null default now()
);

-- RLS encendido y SIN políticas: anon y authenticated no leen ni escriben nada.
alter table public.records enable row level security;
revoke all on public.records from anon, authenticated;

-- Compara y guarda en un solo paso (atómico): si dos jugadores terminan al mismo tiempo,
-- no se pisan como pasaría con "leer, comparar, escribir" desde la función.
-- Regresa el récord vigente, si hubo récord nuevo y el anterior.
create or replace function public.registrar_record(p_dificultad text, p_segundos int, p_nombre text)
returns jsonb
language plpgsql
security invoker
set search_path = public
as $$
declare
  anterior public.records;
  actual   public.records;
begin
  select * into anterior from public.records where dificultad = p_dificultad for update;

  if found and p_segundos <= anterior.segundos then
    return jsonb_build_object('record', false, 'actual', to_jsonb(anterior) - 'dificultad');
  end if;

  insert into public.records (dificultad, segundos, nombre, fecha)
  values (p_dificultad, p_segundos, p_nombre, now())
  on conflict (dificultad) do update
    set segundos = excluded.segundos, nombre = excluded.nombre, fecha = excluded.fecha
    where public.records.segundos < excluded.segundos  -- cubre el caso de dos "primeros" récords a la vez
  returning * into actual;

  if not found then
    select * into actual from public.records where dificultad = p_dificultad;
    return jsonb_build_object('record', false, 'actual', to_jsonb(actual) - 'dificultad');
  end if;

  return jsonb_build_object(
    'record', true,
    'actual', to_jsonb(actual) - 'dificultad',
    'anterior', case when anterior.dificultad is null then null else to_jsonb(anterior) - 'dificultad' end
  );
end;
$$;

-- Solo el rol del servidor (llave secreta = service_role) puede llamarla.
revoke all on function public.registrar_record(text, int, text) from public, anon, authenticated;
grant execute on function public.registrar_record(text, int, text) to service_role;
