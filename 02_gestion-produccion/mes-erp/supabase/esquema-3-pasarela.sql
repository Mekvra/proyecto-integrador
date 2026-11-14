-- MES de Lácteos Altos de Teusacá (Mekvra S.A.S) · tercera parte: pasarela de planta simulada en vivo
-- Se ejecuta después de esquema.sql y esquema-2-planta.sql, en Supabase → SQL Editor → Run.
--
-- Qué hace: una "pasarela" (el papel que en la planta real cumplen el PLC + Node-RED/OPC UA) corre dentro de la
-- base de datos cada 30 s con pg_cron. Mueve los estados de las máquinas, publica sus señales (temperaturas,
-- velocidades, contadores), recibe leche de las fincas, ejecuta órdenes, crea lotes y les hace los controles de
-- calidad. Todo lo que genera queda con origen = 'Simulación' y la página lo marca "SIM": no son datos reales.
-- Las fallas de las llenadoras U311, U312 y U313 usan el % de tiempo en falla del modelo de Tecnomatix (12 semanas);
-- las capacidades salen de la planta de 150.000 L/día. Lo demás son supuestos razonables de planta láctea.
--
-- Para cargar historia (5 días): select public.sim_sembrar(5);
-- Para apagar o prender la pasarela: desde el MES (Administrador) o  update public.simulacion set activa = false;

create extension if not exists pg_cron;

-- ---------------- columnas nuevas ----------------
alter table public.lotes add column if not exists origen text not null default 'Manual';
alter table public.lotes add column if not exists recepcion text not null default '';
alter table public.ordenes add column if not exists origen text not null default 'Manual';
alter table public.calidad add column if not exists origen text not null default 'Manual';
alter table public.paros add column if not exists origen text not null default 'Manual';
alter table public.eventos_maquina add column if not exists origen text not null default 'Manual';
alter table public.lotes alter column autor drop not null;
alter table public.ordenes alter column autor drop not null;
alter table public.calidad alter column autor drop not null;
alter table public.paros alter column autor drop not null;
alter table public.maquinas add column if not exists senales jsonb not null default '[]';
alter table public.maquinas add column if not exists contador numeric not null default 0;
alter table public.maquinas add column if not exists lectura timestamptz;

-- recepción de leche cruda (inicio de la trazabilidad)
create table if not exists public.recepciones (
  id bigint generated always as identity primary key,
  creado timestamptz not null default now(),
  autor uuid default auth.uid() references auth.users (id),
  codigo text not null unique,
  proveedor text not null,
  litros numeric not null check (litros > 0),
  temperatura numeric,
  acidez numeric,
  grasa numeric,
  antibioticos text not null default 'Negativo',
  estado text not null default 'Aceptada' check (estado in ('Aceptada', 'Rechazada')),
  origen text not null default 'Manual'
);

-- historial corto de señales (para las mini gráficas)
create table if not exists public.lecturas (
  id bigint generated always as identity primary key,
  maquina text not null references public.maquinas (codigo) on delete cascade,
  ts timestamptz not null default now(),
  valores jsonb not null
);
create index if not exists lecturas_ts on public.lecturas (ts desc);

-- interruptor de la pasarela
create table if not exists public.simulacion (
  id int primary key default 1 check (id = 1),
  activa boolean not null default true,
  ultimo timestamptz
);
insert into public.simulacion (id) values (1) on conflict (id) do nothing;

-- parámetros de cada máquina para la pasarela
create table if not exists public.sim_maquina (
  codigo text primary key references public.maquinas (codigo) on delete cascade,
  mtbf numeric not null,          -- min en marcha entre fallas
  mttr numeric not null,          -- min promedio por falla
  senales jsonb not null default '[]', -- [{n, u, sp, r, rep}]: nombre, unidad, consigna, ruido, valor en reposo
  hasta timestamptz,
  ultima_cip timestamptz
);
insert into public.sim_maquina (codigo, mtbf, mttr, senales) values
  ('U111', 2500, 20, '[{"n":"Caudal","u":"L/h","sp":6500,"r":120,"rep":0},{"n":"Temperatura","u":"°C","sp":4.0,"r":0.15,"rep":6}]'),
  ('U121', 2200, 25, '[{"n":"Temperatura","u":"°C","sp":73.5,"r":0.25,"rep":24},{"n":"Caudal","u":"L/h","sp":6300,"r":110,"rep":0}]'),
  ('U201', 3000, 15, '[{"n":"Nivel","u":"%","sp":68,"r":3,"rep":22}]'),
  ('U202', 2800, 20, '[{"n":"Temperatura","u":"°C","sp":92,"r":0.4,"rep":30}]'),
  ('U211', 6000, 30, '[{"n":"pH","u":"","sp":4.6,"r":0.02,"rep":6.6},{"n":"Temperatura","u":"°C","sp":42.5,"r":0.15,"rep":20}]'),
  ('U215', 5000, 15, '[{"n":"Temperatura","u":"°C","sp":20,"r":0.4,"rep":16}]'),
  ('U216', 4000, 20, '[{"n":"Caudal","u":"L/h","sp":900,"r":30,"rep":0}]'),
  ('U311', 175, 15, '[{"n":"Velocidad","u":"vasos/min","sp":120,"r":3,"rep":0},{"n":"Peso","u":"g","sp":150.8,"r":0.8,"rep":0}]'),
  ('U312', 258, 15, '[{"n":"Velocidad","u":"bot/min","sp":60,"r":1.5,"rep":0},{"n":"Peso","u":"g","sp":1004,"r":2.5,"rep":0}]'),
  ('U313', 380, 15, '[{"n":"Velocidad","u":"vasos/min","sp":40,"r":1.2,"rep":0},{"n":"Peso","u":"g","sp":502,"r":1.5,"rep":0}]'),
  ('U321', 1500, 10, '[{"n":"Velocidad","u":"cajas/min","sp":10,"r":0.4,"rep":0}]'),
  ('U341', 1200, 12, '[{"n":"Velocidad","u":"palets/h","sp":14,"r":0.8,"rep":0}]'),
  ('Q201', 4000, 25, '[{"n":"Temperatura","u":"°C","sp":33,"r":0.3,"rep":18}]'),
  ('Q202', 4000, 25, '[{"n":"Temperatura","u":"°C","sp":33,"r":0.3,"rep":18}]'),
  ('Q203', 4000, 25, '[{"n":"Temperatura","u":"°C","sp":33,"r":0.3,"rep":18}]'),
  ('Q301', 900, 20, '[{"n":"Temperatura","u":"°C","sp":78,"r":0.7,"rep":30}]'),
  ('Q311', 700, 15, '[{"n":"Velocidad","u":"und/min","sp":30,"r":1.2,"rep":0}]'),
  ('L202', 1800, 30, '[{"n":"Temperatura","u":"°C","sp":140,"r":0.5,"rep":30},{"n":"Presión","u":"bar","sp":4.2,"r":0.08,"rep":1}]'),
  ('L311', 600, 15, '[{"n":"Velocidad","u":"env/min","sp":110,"r":2.5,"rep":0}]')
on conflict (codigo) do update set mtbf = excluded.mtbf, mttr = excluded.mttr, senales = excluded.senales;

-- ---------------- permisos ----------------
alter table public.recepciones enable row level security;
alter table public.lecturas enable row level security;
alter table public.simulacion enable row level security;
alter table public.sim_maquina enable row level security;
drop policy if exists "recepciones: leer" on public.recepciones;
create policy "recepciones: leer" on public.recepciones for select to authenticated using (true);
drop policy if exists "recepciones: registrar" on public.recepciones;
create policy "recepciones: registrar" on public.recepciones for insert to authenticated with check (autor = auth.uid());
drop policy if exists "lecturas: leer" on public.lecturas;
create policy "lecturas: leer" on public.lecturas for select to authenticated using (true);
drop policy if exists "simulacion: leer" on public.simulacion;
create policy "simulacion: leer" on public.simulacion for select to authenticated using (true);
drop policy if exists "sim_maquina: leer" on public.sim_maquina;
create policy "sim_maquina: leer" on public.sim_maquina for select to authenticated using (true);

-- ---------------- reloj: la pasarela puede escribir con su propia hora (para cargar historia) ----------------
create or replace function public.sim_reloj() returns timestamptz
language sql stable as $$
  select coalesce(nullif(current_setting('app.reloj', true), '')::timestamptz, now())
$$;

create or replace function public.maquina_antes() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'INSERT' or new.estado is distinct from old.estado then
    new.desde := public.sim_reloj();
  end if;
  new.actualizado_por := auth.uid();
  return new;
end $$;

create or replace function public.maquina_despues() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'INSERT' or new.estado is distinct from old.estado or new.causa is distinct from old.causa
     or new.orden is distinct from old.orden then
    update public.eventos_maquina set fin = public.sim_reloj() where maquina = new.codigo and fin is null;
    insert into public.eventos_maquina (maquina, estado, causa, orden, inicio, autor, origen)
      values (new.codigo, new.estado, new.causa, new.orden, public.sim_reloj(), auth.uid(),
              coalesce(nullif(current_setting('app.origen', true), ''), 'Manual'));
  end if;
  return null;
end $$;

-- ---------------- utilidades de la pasarela ----------------
create or replace function public.sim_gauss() returns double precision
language sql volatile as $$
  select sqrt(-2 * ln(greatest(random(), 1e-9))) * cos(2 * pi() * random())
$$;

create or replace function public.sim_turno(t timestamptz) returns text
language sql immutable as $$
  select case when extract(hour from t at time zone 'America/Bogota') >= 6 and extract(hour from t at time zone 'America/Bogota') < 14 then 'Mañana'
              when extract(hour from t at time zone 'America/Bogota') >= 14 and extract(hour from t at time zone 'America/Bogota') < 22 then 'Tarde'
              else 'Noche' end
$$;

create or replace function public.sim_dia(t timestamptz) returns text
language sql immutable as $$ select to_char(t at time zone 'America/Bogota', 'YYMMDD') $$;

create or replace function public.sim_nuevo_lote(t timestamptz, o public.ordenes, litros numeric, rec text)
returns void language plpgsql security definer set search_path = public as $$
declare n int; pre text := left(o.producto, 2);
begin
  n := (select count(*) from lotes where codigo like pre || '-' || sim_dia(t) || '-%') + 1;
  insert into lotes (creado, autor, linea, producto, codigo, litros, estado, orden, recepcion, origen)
  values (t, null, o.linea, o.producto, pre || '-' || sim_dia(t) || '-' || lpad(n::text, 3, '0'), litros, 'En proceso', o.codigo, coalesce(rec, ''), 'Simulación');
end $$;

create or replace function public.sim_prueba(t timestamptz, lote text, prueba text, media float, sd float, lo float, hi float, decs int)
returns boolean language plpgsql security definer set search_path = public as $$
declare v float := media + sd * sim_gauss(); r text;
begin
  r := case when v between lo and hi then 'Aprobado' when v between lo - sd and hi + sd then 'En revisión' else 'Rechazado' end;
  insert into calidad (creado, autor, lote, prueba, valor, resultado, nota, origen)
  values (t, null, lote, prueba, round(v::numeric, decs)::text, r, format('Especificación %s – %s', lo, hi), 'Simulación');
  return r = 'Aprobado';
end $$;

-- ---------------- un paso de la pasarela ----------------
create or replace function public.sim_paso(t timestamptz, dt numeric, con_senales boolean default true)
returns void language plpgsql security definer set search_path = public as $$
declare
  c record; o public.ordenes; m record; p record; s record;
  rec text; n int; prods text[]; prod text; lotado numeric; tam numeric; tasa numeric;
  activa boolean; nuevo text; ncausa text; corriendo boolean; arr jsonb; prev float; v float; objetivo float; vel float;
begin
  perform set_config('app.reloj', t::text, true);
  perform set_config('app.origen', 'Simulación', true);

  -- 1 · recepción de leche: una cisterna cada ~110 min
  if random() < dt / 110 then
    n := (select count(*) from recepciones where codigo like 'RL-' || sim_dia(t) || '-%') + 1;
    insert into recepciones (creado, autor, codigo, proveedor, litros, temperatura, acidez, grasa, antibioticos, estado, origen)
    select t, null, 'RL-' || sim_dia(t) || '-' || lpad(n::text, 2, '0'),
      (array['Hacienda El Rosal', 'Finca La Esperanza', 'Lechería San Isidro', 'Hacienda Teusacá', 'Cooperativa La Calera', 'Finca Los Alpes'])[1 + floor(random() * 6)::int],
      round((9000 + random() * 5000)::numeric, -2), round((3.3 + random() * 1.3)::numeric, 1),
      round((0.14 + random() * 0.03)::numeric, 3), round((3.4 + random() * 0.4)::numeric, 2), ab, case when ab = 'Positivo' then 'Rechazada' else 'Aceptada' end, 'Simulación'
    from (select case when random() < 0.02 then 'Positivo' else 'Negativo' end as ab) x;
  end if;
  select codigo into rec from recepciones where estado = 'Aceptada' order by creado desc limit 1;

  -- 2 · órdenes: plan, liberación y cierre
  update ordenes set estado = 'Liberada' where origen = 'Simulación' and estado = 'Planeada' and creado <= t - interval '45 minutes';
  update ordenes set estado = 'Cerrada' where origen = 'Simulación' and estado = 'Terminada' and fin <= t - interval '2 hours';
  for c in select * from (values ('Yogurts', 3), ('Quesos', 1), ('Leche UHT', 1)) as x(linea, cola) loop
    if (select count(*) from ordenes where linea = c.linea and estado in ('Planeada', 'Liberada')) < c.cola then
      prods := case c.linea when 'Yogurts' then array['YF · Yogurt con fresa', 'YN · Yogurt natural', 'YG · Yogurt griego']
                            when 'Quesos' then array['QM · Mozzarella', 'QQ · Quesillo', 'QD · Doble crema']
                            else array['LE · Leche entera', 'LE · Leche entera', 'LD · Leche descremada', 'LC · Leche con chocolate'] end;
      n := (select count(*) from ordenes where codigo like 'OP-' || sim_dia(t) || '-%') + 1;
      insert into ordenes (creado, autor, codigo, linea, producto, litros_plan, fecha, turno, prioridad, estado, origen)
      values (t, null, 'OP-' || sim_dia(t) || '-' || lpad(n::text, 2, '0'), c.linea, prods[1 + floor(random() * array_length(prods, 1))::int],
              round(((case c.linea when 'Yogurts' then 5000 when 'Quesos' then 9000 else 12000 end) + random() * 5000)::numeric, -2),
              (t at time zone 'America/Bogota')::date, sim_turno(t), case when random() < 0.12 then 'Alta' else 'Normal' end, 'Planeada', 'Simulación');
    end if;
  end loop;

  -- 3 · puestos que ejecutan órdenes (llenadoras y cuellos de cada línea)
  for c in select * from (values ('U311', 'Yogurts', 'YF', 25), ('U312', 'Yogurts', 'YN', 15), ('U313', 'Yogurts', 'YG', 10),
                                 ('Q301', 'Quesos', '', 44), ('L311', 'Leche UHT', '', 38)) as x(maq, linea, pre, tasa) loop
    select * into o from ordenes where maquina = c.maq and estado = 'En ejecución' limit 1;
    select * into m from maquinas where codigo = c.maq;
    if o.id is null then
      if m.estado in ('Falla', 'Mantenimiento', 'Cambio', 'Limpieza') then continue; end if;
      select * into o from ordenes where linea = c.linea and estado = 'Liberada' and (c.pre = '' or left(producto, 2) = c.pre)
        order by case prioridad when 'Urgente' then 0 when 'Alta' then 1 else 2 end, id limit 1;
      if o.id is null then
        if random() > dt / 20 then continue; end if; -- espera de plan
        prods := case c.linea when 'Quesos' then array['QM · Mozzarella', 'QQ · Quesillo', 'QD · Doble crema']
                              when 'Leche UHT' then array['LE · Leche entera', 'LD · Leche descremada', 'LC · Leche con chocolate']
                              else array[case c.pre when 'YF' then 'YF · Yogurt con fresa' when 'YN' then 'YN · Yogurt natural' else 'YG · Yogurt griego' end] end;
        n := (select count(*) from ordenes where codigo like 'OP-' || sim_dia(t) || '-%') + 1;
        insert into ordenes (creado, autor, codigo, linea, producto, litros_plan, fecha, turno, prioridad, estado, origen)
        values (t, null, 'OP-' || sim_dia(t) || '-' || lpad(n::text, 2, '0'), c.linea, prods[1 + floor(random() * array_length(prods, 1))::int],
                round(((case c.linea when 'Yogurts' then 4000 when 'Quesos' then 9000 else 12000 end) + random() * 5000)::numeric, -2),
                (t at time zone 'America/Bogota')::date, sim_turno(t), 'Normal', 'Liberada', 'Simulación')
        returning * into o;
      end if;
      update ordenes set estado = 'En ejecución', inicio = t, maquina = c.maq where id = o.id;
      update maquinas set estado = 'Cambio', causa = 'Cambio de producto', orden = o.codigo where codigo = c.maq;
      update sim_maquina set hasta = t + make_interval(mins => (12 + random() * 15)::int) where codigo = c.maq;
    elsif m.estado = 'En marcha' then
      update ordenes set litros_real = litros_real + round((c.tasa * dt * (0.86 + random() * 0.18))::numeric, 0)
        where id = o.id returning * into o;
      tam := case c.linea when 'Yogurts' then 2000 when 'Quesos' then 2500 else 3000 end;
      select coalesce(sum(litros), 0) into lotado from lotes where orden = o.codigo;
      while o.litros_real - lotado >= tam loop
        perform sim_nuevo_lote(t, o, tam, rec);
        lotado := lotado + tam;
      end loop;
      if o.litros_real >= o.litros_plan then
        if o.litros_real - lotado > 0 then perform sim_nuevo_lote(t, o, o.litros_real - lotado, rec); end if;
        update ordenes set estado = 'Terminada', fin = t where id = o.id;
        update maquinas set estado = 'Parada', causa = 'Sin orden', orden = '' where codigo = c.maq;
      end if;
    end if;
  end loop;

  -- 4 · estados de las máquinas y señales
  for m in select mq.*, sm.mtbf, sm.mttr, sm.senales as def, sm.hasta, sm.ultima_cip
           from maquinas mq join sim_maquina sm using (codigo) loop
    activa := case when m.codigo in ('U311', 'U312', 'U313', 'Q301', 'L311') then m.orden <> ''
                   when m.codigo = 'U216' then exists (select 1 from maquinas where codigo = 'U313' and orden <> '')
                   when m.linea = 'Recepción' then true
                   else exists (select 1 from ordenes where linea = m.linea and estado = 'En ejecución') end;
    nuevo := null; ncausa := null;
    if m.estado in ('Falla', 'Mantenimiento', 'Cambio', 'Limpieza') then
      if m.hasta is null or t >= m.hasta then
        if m.estado = 'Limpieza' then update sim_maquina set ultima_cip = t where codigo = m.codigo; end if;
        if activa then nuevo := 'En marcha'; ncausa := 'Producción'; else nuevo := 'Parada'; ncausa := 'Sin orden'; end if;
      end if;
    elsif m.estado = 'En marcha' then
      if not activa then
        nuevo := 'Parada'; ncausa := 'Sin orden';
      elsif random() < dt / m.mtbf then
        nuevo := 'Falla';
        ncausa := (array['Falla mecánica', 'Falla eléctrica', 'Falla de instrumentación', 'Atasco'])[1 + floor(random() * 4)::int];
        update sim_maquina set hasta = t + make_interval(secs => (m.mttr * 60 * (0.4 + random() * 1.2))::int) where codigo = m.codigo;
      elsif t - coalesce(m.ultima_cip, t) > interval '10 hours' and random() < dt / 60 then
        nuevo := 'Limpieza'; ncausa := 'Limpieza CIP';
        update sim_maquina set hasta = t + make_interval(mins => (30 + random() * 20)::int) where codigo = m.codigo;
      end if;
    elsif m.estado = 'Parada' then
      if activa and (m.causa in ('Sin orden', 'Fin de turno') or t - m.desde > interval '20 minutes') then
        nuevo := 'En marcha'; ncausa := 'Producción';
      end if;
    end if;

    if con_senales then
      corriendo := coalesce(nuevo, m.estado) = 'En marcha';
      arr := '[]'::jsonb;
      vel := 0;
      for s in select e.value as d, e.ordinality - 1 as i from jsonb_array_elements(m.def) with ordinality e loop
        prev := coalesce((m.senales -> s.i::int ->> 'v')::float, (s.d ->> 'rep')::float);
        if s.d ->> 'n' = 'pH' then
          v := case when corriendo then 4.55 + 2.0 * exp(-((extract(epoch from t) / 60)::numeric % 300) / 70.0) + 0.01 * sim_gauss()
                    else prev + (6.6 - prev) * least(1, dt / 30) end;
        elsif s.d ->> 'n' = 'Velocidad' or (s.d ->> 'rep')::float = 0 then
          v := case when corriendo then (s.d ->> 'sp')::float + (s.d ->> 'r')::float * sim_gauss() else 0 end;
        else
          objetivo := case when corriendo then (s.d ->> 'sp')::float else (s.d ->> 'rep')::float end;
          v := prev + (objetivo - prev) * least(1, dt / 6) + case when corriendo then 0.6 * (s.d ->> 'r')::float * sim_gauss() else 0 end;
        end if;
        if s.d ->> 'n' = 'Velocidad' then vel := v; end if;
        arr := arr || jsonb_build_object('n', s.d ->> 'n', 'u', s.d ->> 'u',
          'v', round(v::numeric, case when abs(v) >= 1000 then 0 when abs(v) >= 100 then 1 else 2 end));
      end loop;
      if (select count(*) from jsonb_array_elements(m.def) e where e ->> 'n' = 'Velocidad' and e ->> 'u' = 'palets/h') > 0 then vel := vel / 60; end if;
      update maquinas set estado = coalesce(nuevo, estado), causa = coalesce(ncausa, causa), senales = arr,
        contador = contador + case when corriendo then round((vel * dt)::numeric, 2) else 0 end, lectura = t
        where codigo = m.codigo;
      if not exists (select 1 from lecturas where maquina = m.codigo and ts > t - interval '110 seconds') then
        insert into lecturas (maquina, ts, valores) values (m.codigo, t, arr);
      end if;
    elsif nuevo is not null then
      update maquinas set estado = nuevo, causa = ncausa where codigo = m.codigo;
    end if;
  end loop;

  -- 5 · calidad: controles a los 25 min, decisión a los 70 min
  for p in select * from lotes where origen = 'Simulación' and estado = 'En proceso' and creado <= t - interval '25 minutes' loop
    if p.linea = 'Yogurts' then
      perform sim_prueba(t, p.codigo, 'pH', 4.5, 0.035, 4.4, 4.6, 2);
      perform sim_prueba(t, p.codigo, 'Acidez (% ácido láctico)', 0.9, 0.03, 0.8, 1.0, 2);
      perform sim_prueba(t, p.codigo, 'Temperatura (°C)', 4.4, 0.45, 2, 6, 1);
      if left(p.producto, 2) = 'YF' then perform sim_prueba(t, p.codigo, 'Peso de llenado (g)', 150.8, 0.9, 148, 154, 1);
      elsif left(p.producto, 2) = 'YN' then perform sim_prueba(t, p.codigo, 'Peso de llenado (g)', 1004, 2.4, 995, 1012, 0);
      else perform sim_prueba(t, p.codigo, 'Peso de llenado (g)', 502, 1.4, 497, 508, 1); end if;
    elsif p.linea = 'Quesos' then
      perform sim_prueba(t, p.codigo, 'pH', 5.25, 0.045, 5.1, 5.4, 2);
      perform sim_prueba(t, p.codigo, 'Grasa (%)', 20, 0.6, 18, 22, 1);
      perform sim_prueba(t, p.codigo, 'Sólidos (%)', 47.5, 0.8, 45, 50, 1);
      perform sim_prueba(t, p.codigo, 'Temperatura (°C)', 4.4, 0.45, 2, 6, 1);
    else
      perform sim_prueba(t, p.codigo, 'pH', 6.7, 0.025, 6.6, 6.8, 2);
      if left(p.producto, 2) = 'LE' then perform sim_prueba(t, p.codigo, 'Grasa (%)', 3.1, 0.035, 3.0, 3.2, 2);
      elsif left(p.producto, 2) = 'LD' then perform sim_prueba(t, p.codigo, 'Grasa (%)', 0.3, 0.06, 0.1, 0.5, 2);
      else perform sim_prueba(t, p.codigo, 'Grasa (%)', 1.5, 0.035, 1.4, 1.6, 2); end if;
      perform sim_prueba(t, p.codigo, 'Sólidos (%)', 12.2, 0.25, 11.5, 13, 1);
      insert into calidad (creado, autor, lote, prueba, valor, resultado, nota, origen)
      values (t, null, p.codigo, 'Microbiología', case when random() < 0.995 then 'Estéril' else 'No estéril' end, 'Aprobado', 'Incubación 7 días a 30 °C', 'Simulación');
      update calidad set resultado = 'Rechazado' where lote = p.codigo and prueba = 'Microbiología' and valor = 'No estéril';
    end if;
    update lotes set estado = 'Terminado' where id = p.id;
  end loop;
  update lotes l set estado = case when exists (select 1 from calidad q where q.lote = l.codigo and q.resultado <> 'Aprobado') then 'Retenido' else 'Liberado' end
    where origen = 'Simulación' and estado = 'Terminado' and creado <= t - interval '70 minutes';

  -- 6 · limpieza del historial de señales
  if con_senales and random() < 0.02 then delete from lecturas where ts < t - interval '1 day'; end if;
end $$;

-- ---------------- reloj de la pasarela (pg_cron cada 30 s) ----------------
create or replace function public.sim_tic() returns void
language plpgsql security definer set search_path = public as $$
declare s record; dt numeric;
begin
  select * into s from simulacion where id = 1;
  if not found or not s.activa then return; end if;
  dt := least(5, greatest(0.1, extract(epoch from now() - coalesce(s.ultimo, now() - interval '30 seconds')) / 60));
  perform sim_paso(now(), dt, true);
  update simulacion set ultimo = now() where id = 1;
end $$;

-- ---------------- historia: simula los últimos días ----------------
create or replace function public.sim_sembrar(dias int default 5) returns text
language plpgsql security definer set search_path = public as $$
declare t0 timestamptz := date_trunc('minute', now()) - make_interval(days => dias); t timestamptz;
begin
  perform set_config('app.reloj', t0::text, true);
  perform set_config('app.origen', 'Simulación', true);
  delete from eventos_maquina;
  delete from lecturas;
  delete from calidad where origen = 'Simulación';
  delete from lotes where origen = 'Simulación';
  delete from ordenes where origen = 'Simulación';
  delete from recepciones where origen = 'Simulación';
  update maquinas set estado = 'Parada', causa = 'Sin orden', orden = '', contador = 0, senales = '[]', desde = t0;
  insert into eventos_maquina (maquina, estado, causa, orden, inicio, origen)
    select codigo, 'Parada', 'Sin orden', '', t0, 'Simulación' from maquinas
    where codigo not in (select maquina from eventos_maquina where fin is null);
  update sim_maquina set hasta = null, ultima_cip = t0 - random() * interval '9 hours';
  t := t0;
  while t < now() - interval '3 hours' loop
    perform sim_paso(t, 4, false);
    t := t + interval '4 minutes';
  end loop;
  while t < now() loop
    perform sim_paso(t, 1, true);
    t := t + interval '1 minute';
  end loop;
  update simulacion set activa = true, ultimo = now() where id = 1;
  return format('%s recepciones, %s órdenes, %s lotes, %s controles, %s eventos',
    (select count(*) from recepciones), (select count(*) from ordenes), (select count(*) from lotes),
    (select count(*) from calidad), (select count(*) from eventos_maquina));
end $$;

-- el administrador prende o apaga la pasarela desde el MES
create or replace function public.sim_control(prender boolean) returns void
language plpgsql security definer set search_path = public as $$
begin
  if public.mi_rol() <> 'Administrador' then raise exception 'Solo el administrador controla la pasarela'; end if;
  update simulacion set activa = prender, ultimo = now() where id = 1;
end $$;

-- nadie llama la pasarela desde la página salvo sim_control
revoke execute on function public.sim_paso(timestamptz, numeric, boolean) from public, anon, authenticated;
revoke execute on function public.sim_tic() from public, anon, authenticated;
revoke execute on function public.sim_sembrar(int) from public, anon, authenticated;
revoke execute on function public.sim_nuevo_lote(timestamptz, public.ordenes, numeric, text) from public, anon, authenticated;
revoke execute on function public.sim_prueba(timestamptz, text, text, float, float, float, float, int) from public, anon, authenticated;
revoke execute on function public.sim_control(boolean) from public, anon;

-- tiempo real
do $$
declare t text;
begin
  foreach t in array array['recepciones', 'lecturas', 'simulacion'] loop
    begin
      execute format('alter publication supabase_realtime add table public.%I', t);
    exception when duplicate_object then null;
    end;
  end loop;
end $$;

-- programar la pasarela cada 30 s
select cron.schedule('mes-pasarela-planta', '30 seconds', 'select public.sim_tic()');
