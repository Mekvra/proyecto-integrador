-- MES de Lácteos Altos de Teusacá (Mekvra S.A.S) · segunda parte: planta en vivo, órdenes y roles
-- Se ejecuta después de esquema.sql, una sola vez, en Supabase → SQL Editor → New query → Run.
-- Agrega: rol Gerencia, permisos por rol, máquinas con su estado en tiempo real, historial de estados
-- (para disponibilidad, MTTR y MTBF), órdenes de producción y el enlace lote ↔ orden.

-- ---------------- roles ----------------
alter table public.perfiles drop constraint if exists perfiles_rol_check;
alter table public.perfiles add constraint perfiles_rol_check
  check (rol in ('Operario', 'Supervisor', 'Calidad', 'Mantenimiento', 'Jefe de planta', 'Gerencia', 'Administrador'));

-- rol de quien hace la consulta
create or replace function public.mi_rol() returns text
language sql stable security definer set search_path = public as $$
  select coalesce((select rol from public.perfiles where id = auth.uid()), '')
$$;

-- solo el administrador cambia roles (cada quien puede editar su nombre)
create or replace function public.proteger_rol() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.rol is distinct from old.rol and auth.uid() is not null and public.mi_rol() <> 'Administrador' then
    raise exception 'Solo el administrador cambia los roles';
  end if;
  return new;
end $$;

drop trigger if exists proteger_rol on public.perfiles;
create trigger proteger_rol before update on public.perfiles
  for each row execute function public.proteger_rol();

drop policy if exists "perfiles: administrador edita" on public.perfiles;
create policy "perfiles: administrador edita" on public.perfiles for update to authenticated
  using (public.mi_rol() = 'Administrador');

-- ---------------- máquinas ----------------
create table if not exists public.maquinas (
  codigo text primary key,
  nombre text not null,
  linea text not null check (linea in ('Recepción', 'Yogurts', 'Quesos', 'Leche UHT')),
  etapa text not null default '',
  posicion int not null default 0,
  estado text not null default 'Parada'
    check (estado in ('En marcha', 'Parada', 'Cambio', 'Limpieza', 'Falla', 'Mantenimiento')),
  causa text not null default 'Sin orden',
  orden text not null default '',
  desde timestamptz not null default now(),
  actualizado_por uuid references auth.users (id)
);

-- historial: un evento por cada cambio de estado (inicio y fin)
create table if not exists public.eventos_maquina (
  id bigint generated always as identity primary key,
  maquina text not null references public.maquinas (codigo) on delete cascade,
  estado text not null,
  causa text not null default '',
  orden text not null default '',
  inicio timestamptz not null default now(),
  fin timestamptz,
  autor uuid references auth.users (id)
);
create index if not exists eventos_maquina_inicio on public.eventos_maquina (inicio desc);
create index if not exists eventos_maquina_abiertos on public.eventos_maquina (maquina) where fin is null;

create or replace function public.maquina_antes() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'INSERT' or new.estado is distinct from old.estado then
    new.desde := now();
  end if;
  new.actualizado_por := auth.uid();
  return new;
end $$;

create or replace function public.maquina_despues() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'INSERT' or new.estado is distinct from old.estado or new.causa is distinct from old.causa
     or new.orden is distinct from old.orden then
    update public.eventos_maquina set fin = now() where maquina = new.codigo and fin is null;
    insert into public.eventos_maquina (maquina, estado, causa, orden, inicio, autor)
      values (new.codigo, new.estado, new.causa, new.orden, now(), auth.uid());
  end if;
  return null;
end $$;

drop trigger if exists maquina_antes on public.maquinas;
create trigger maquina_antes before insert or update on public.maquinas
  for each row execute function public.maquina_antes();
drop trigger if exists maquina_despues on public.maquinas;
create trigger maquina_despues after insert or update on public.maquinas
  for each row execute function public.maquina_despues();

-- equipos de la planta (los mismos de los planos y de Tecnomatix)
insert into public.maquinas (codigo, nombre, linea, etapa, posicion) values
  ('U111', 'Recepción y filtrado', 'Recepción', 'Recepción', 1),
  ('U121', 'Pasteurizador HTST', 'Recepción', 'Pasteurización', 2),
  ('U201', 'Formulación', 'Yogurts', 'Preparación', 1),
  ('U202', 'Tratamiento de la base', 'Yogurts', 'Preparación', 2),
  ('U211', 'Fermentadores U211–U218', 'Yogurts', 'Fermentación', 3),
  ('U215', 'Ruptura y enfriamiento', 'Yogurts', 'Fermentación', 4),
  ('U216', 'Separador del griego', 'Yogurts', 'Fermentación', 5),
  ('U311', 'Llenadora de vasos', 'Yogurts', 'Llenado', 6),
  ('U312', 'Llenadora de botellas', 'Yogurts', 'Llenado', 7),
  ('U313', 'Llenadora del griego', 'Yogurts', 'Llenado', 8),
  ('U321', 'Encajonadoras U321–U323', 'Yogurts', 'Empaque', 9),
  ('U341', 'Paletizado', 'Yogurts', 'Empaque', 10),
  ('Q201', 'Tina de cuajado 1', 'Quesos', 'Cuajado', 1),
  ('Q202', 'Tina de cuajado 2', 'Quesos', 'Cuajado', 2),
  ('Q203', 'Tina de cuajado 3', 'Quesos', 'Cuajado', 3),
  ('Q301', 'Hiladora', 'Quesos', 'Hilado', 4),
  ('Q311', 'Empacadora al vacío', 'Quesos', 'Empaque', 5),
  ('L202', 'Esterilizador UHT', 'Leche UHT', 'Tratamiento', 1),
  ('L311', 'Envasadora aséptica', 'Leche UHT', 'Envasado', 2)
on conflict (codigo) do nothing;

-- ---------------- órdenes de producción ----------------
create table if not exists public.ordenes (
  id bigint generated always as identity primary key,
  creado timestamptz not null default now(),
  autor uuid not null default auth.uid() references auth.users (id),
  codigo text not null unique,
  linea text not null check (linea in ('Yogurts', 'Quesos', 'Leche UHT')),
  producto text not null,
  litros_plan numeric not null check (litros_plan > 0),
  litros_real numeric not null default 0 check (litros_real >= 0),
  fecha date not null default current_date,
  turno text not null default 'Mañana' check (turno in ('Mañana', 'Tarde', 'Noche')),
  prioridad text not null default 'Normal' check (prioridad in ('Normal', 'Alta', 'Urgente')),
  estado text not null default 'Planeada'
    check (estado in ('Planeada', 'Liberada', 'En ejecución', 'Terminada', 'Cerrada')),
  maquina text references public.maquinas (codigo),
  inicio timestamptz,
  fin timestamptz,
  nota text not null default ''
);

-- lotes ligados a su orden
alter table public.lotes add column if not exists orden text not null default '';

-- ---------------- permisos (RLS) ----------------
alter table public.maquinas enable row level security;
alter table public.eventos_maquina enable row level security;
alter table public.ordenes enable row level security;

drop policy if exists "maquinas: leer" on public.maquinas;
create policy "maquinas: leer" on public.maquinas for select to authenticated using (true);
drop policy if exists "maquinas: cambiar estado" on public.maquinas;
create policy "maquinas: cambiar estado" on public.maquinas for update to authenticated using (true) with check (true);
drop policy if exists "maquinas: crear" on public.maquinas;
create policy "maquinas: crear" on public.maquinas for insert to authenticated
  with check (public.mi_rol() in ('Jefe de planta', 'Administrador'));
drop policy if exists "maquinas: borrar" on public.maquinas;
create policy "maquinas: borrar" on public.maquinas for delete to authenticated
  using (public.mi_rol() in ('Jefe de planta', 'Administrador'));

drop policy if exists "eventos: leer" on public.eventos_maquina;
create policy "eventos: leer" on public.eventos_maquina for select to authenticated using (true);

drop policy if exists "ordenes: leer" on public.ordenes;
create policy "ordenes: leer" on public.ordenes for select to authenticated using (true);
drop policy if exists "ordenes: planear" on public.ordenes;
create policy "ordenes: planear" on public.ordenes for insert to authenticated
  with check (autor = auth.uid() and public.mi_rol() in ('Supervisor', 'Jefe de planta', 'Administrador'));
drop policy if exists "ordenes: avanzar" on public.ordenes;
create policy "ordenes: avanzar" on public.ordenes for update to authenticated using (true) with check (true);
drop policy if exists "ordenes: borrar" on public.ordenes;
create policy "ordenes: borrar" on public.ordenes for delete to authenticated
  using (public.mi_rol() in ('Supervisor', 'Jefe de planta', 'Administrador'));

-- calidad libera o retiene cualquier lote
drop policy if exists "lotes: calidad dispone" on public.lotes;
create policy "lotes: calidad dispone" on public.lotes for update to authenticated
  using (public.mi_rol() in ('Calidad', 'Jefe de planta', 'Administrador'));

-- ---------------- tiempo real ----------------
do $$
declare t text;
begin
  foreach t in array array['maquinas', 'eventos_maquina', 'ordenes', 'perfiles'] loop
    begin
      execute format('alter publication supabase_realtime add table public.%I', t);
    exception when duplicate_object then null;
    end;
  end loop;
end $$;

-- el primer usuario (quien montó la planta) queda como administrador
update public.perfiles set rol = 'Administrador' where (select count(*) from public.perfiles) = 1;
