-- Not a Morning Person · prueba de la tabla partidas (RLS + reglas del schema)
-- Correr en Supabase → SQL Editor DESPUÉS de partidas.sql. No pide contraseñas:
-- se hace pasar por los 2 primeros usuarios de auth.users (como lo haría su sesión),
-- prueba qué pueden y qué no pueden hacer, borra sus filas de prueba y muestra una tabla de resultados.
-- Resultado esperado: todas las filas con ok = true.

create temp table if not exists resultados (n int, prueba text, ok boolean, detalle text);
truncate resultados;

do $$
declare
  a uuid; b uuid; n int; err text;
  marca constant timestamptz := '2000-01-01 00:00:00+00';  -- fecha falsa para reconocer y borrar las filas de prueba
begin
  select id into a from auth.users order by created_at limit 1;
  select id into b from auth.users order by created_at offset 1 limit 1;
  if b is null then raise exception 'Se necesitan al menos 2 usuarios en Authentication'; end if;

  -- 1. A inserta una partida ganada válida
  perform set_config('request.jwt.claims', json_build_object('sub', a, 'role', 'authenticated')::text, true);
  set local role authenticated;
  begin
    insert into public.partidas (fecha, dificultad, gano, causa, misiones_completadas, vidas_perdidas, vidas_restantes,
                                 segundos_restantes, uso_snooze, emboscadas, emboscadas_ganadas, vida_perdida_por)
    values (marca, 'normal', true, null, 9, 1, 1, 42, false, 5, 4, '{baba}');
    err := null;
  exception when others then err := sqlerrm;
  end;
  reset role;
  insert into resultados values (1, 'A guarda una partida ganada válida', err is null, coalesce(err, 'insertada'));

  -- 2. A inserta una partida perdida válida (sin enviar user_id: lo pone auth.uid())
  set local role authenticated;
  begin
    insert into public.partidas (fecha, dificultad, gano, causa, misiones_completadas, vidas_perdidas, vidas_restantes,
                                 segundos_restantes, uso_snooze, emboscadas, emboscadas_ganadas, vida_perdida_por)
    values (marca, 'hard', false, 'vidas', 4, 2, 0, 97, false, 3, 1, '{shrum,torpeza}');
    err := null;
  exception when others then err := sqlerrm;
  end;
  reset role;
  insert into resultados values (2, 'A guarda una partida perdida válida', err is null, coalesce(err, 'insertada'));

  -- 3. A lee sus partidas
  set local role authenticated;
  select count(*) into n from public.partidas where fecha = marca;
  reset role;
  insert into resultados values (3, 'A ve sus 2 partidas de prueba', n = 2, n || ' filas visibles');

  -- 4. Datos fuera de las reglas: 999 segundos → la base los rechaza
  set local role authenticated;
  begin
    insert into public.partidas (fecha, dificultad, gano, causa, misiones_completadas, vidas_perdidas, vidas_restantes,
                                 segundos_restantes, uso_snooze, emboscadas, emboscadas_ganadas, vida_perdida_por)
    values (marca, 'normal', true, null, 9, 0, 2, 999, false, 0, 0, '{}');
    err := null;
  exception when others then err := sqlerrm;
  end;
  reset role;
  insert into resultados values (4, 'Rechaza segundos_restantes = 999', err is not null, coalesce(err, 'SE ACEPTÓ (mal)'));

  -- 5. Culpables que no cuadran con las vidas perdidas → rechazado
  set local role authenticated;
  begin
    insert into public.partidas (fecha, dificultad, gano, causa, misiones_completadas, vidas_perdidas, vidas_restantes,
                                 segundos_restantes, uso_snooze, emboscadas, emboscadas_ganadas, vida_perdida_por)
    values (marca, 'normal', false, 'tiempo', 6, 2, 0, 0, false, 4, 2, '{baba}');
    err := null;
  exception when others then err := sqlerrm;
  end;
  reset role;
  insert into resultados values (5, 'Rechaza 2 vidas perdidas con 1 culpable', err is not null, coalesce(err, 'SE ACEPTÓ (mal)'));

  -- 6. B no ve las partidas de A
  perform set_config('request.jwt.claims', json_build_object('sub', b, 'role', 'authenticated')::text, true);
  set local role authenticated;
  select count(*) into n from public.partidas where user_id = a;
  reset role;
  insert into resultados values (6, 'B no ve las partidas de A', n = 0, n || ' filas de A visibles para B');

  -- 7. B no puede guardar una partida a nombre de A
  set local role authenticated;
  begin
    insert into public.partidas (user_id, fecha, dificultad, gano, causa, misiones_completadas, vidas_perdidas, vidas_restantes,
                                 segundos_restantes, uso_snooze, emboscadas, emboscadas_ganadas, vida_perdida_por)
    values (a, marca, 'normal', true, null, 9, 0, 2, 170, false, 0, 0, '{}');
    err := null;
  exception when others then err := sqlerrm;
  end;
  reset role;
  insert into resultados values (7, 'B no puede insertar a nombre de A', err is not null, coalesce(err, 'SE ACEPTÓ (mal)'));

  -- 8. A no puede editar sus partidas (no hay permiso de update)
  perform set_config('request.jwt.claims', json_build_object('sub', a, 'role', 'authenticated')::text, true);
  set local role authenticated;
  begin
    update public.partidas set segundos_restantes = 180 where fecha = marca;
    err := null;
  exception when others then err := sqlerrm;
  end;
  reset role;
  insert into resultados values (8, 'A no puede editar su récord', err is not null, coalesce(err, 'SE PERMITIÓ (mal)'));

  -- 8b. A no puede borrar sus partidas
  set local role authenticated;
  begin
    delete from public.partidas where fecha = marca;
    err := null;
  exception when others then err := sqlerrm;
  end;
  reset role;
  insert into resultados values (8, 'A no puede borrar sus partidas', err is not null, coalesce(err, 'SE PERMITIÓ (mal)'));

  -- 9. Visitante sin sesión (anon) no puede leer la tabla
  perform set_config('request.jwt.claims', json_build_object('role', 'anon')::text, true);
  set local role anon;
  begin
    select count(*) into n from public.partidas;
    err := null;
  exception when others then err := sqlerrm;
  end;
  reset role;
  insert into resultados values (9, 'Sin sesión no se puede leer', err is not null, coalesce(err, 'SE PERMITIÓ (mal): ' || n || ' filas'));

  -- Limpieza: borra las filas de prueba (como dueño de la base, sin RLS)
  delete from public.partidas where fecha = marca;
end $$;

select * from resultados order by n, prueba;
