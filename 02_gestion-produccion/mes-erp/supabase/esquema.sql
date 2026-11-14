-- MES de Lácteos Altos de Teusacá (Mekvra S.A.S) · base de datos en Supabase
-- Se ejecuta una sola vez en Supabase → SQL Editor → New query → Run.
-- Crea los perfiles de usuario, los registros de producción (lotes, paros y calidad), el almacén de archivos
-- y los permisos: solo usuarios con sesión iniciada leen y escriben; cada quien edita o borra lo suyo.

-- ---------------- perfiles ----------------
create table if not exists public.perfiles (
  id uuid primary key references auth.users (id) on delete cascade,
  nombre text not null default '',
  rol text not null default 'Operario' check (rol in ('Operario', 'Supervisor', 'Calidad', 'Mantenimiento', 'Jefe de planta', 'Administrador')),
  creado timestamptz not null default now()
);

-- crea el perfil automáticamente cuando se crea un usuario
create or replace function public.nuevo_perfil() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.perfiles (id, nombre, rol)
  values (new.id,
          coalesce(new.raw_user_meta_data ->> 'nombre', split_part(new.email, '@', 1)),
          coalesce(new.raw_user_meta_data ->> 'rol', 'Operario'));
  return new;
end $$;

drop trigger if exists al_crear_usuario on auth.users;
create trigger al_crear_usuario after insert on auth.users
  for each row execute function public.nuevo_perfil();

-- ---------------- registros de producción ----------------
create table if not exists public.lotes (
  id bigint generated always as identity primary key,
  creado timestamptz not null default now(),
  autor uuid not null default auth.uid() references auth.users (id),
  linea text not null check (linea in ('Yogurts', 'Quesos', 'Leche UHT')),
  producto text not null,
  codigo text not null,
  litros numeric not null check (litros > 0),
  estado text not null default 'En proceso' check (estado in ('En proceso', 'Terminado', 'Retenido', 'Liberado')),
  nota text default ''
);

create table if not exists public.paros (
  id bigint generated always as identity primary key,
  creado timestamptz not null default now(),
  autor uuid not null default auth.uid() references auth.users (id),
  linea text not null,
  equipo text not null,
  causa text not null check (causa in ('Falla', 'Cambio de formato', 'Limpieza CIP', 'Falta de material', 'Mantenimiento', 'Otra')),
  minutos numeric not null check (minutos > 0),
  nota text default ''
);

create table if not exists public.calidad (
  id bigint generated always as identity primary key,
  creado timestamptz not null default now(),
  autor uuid not null default auth.uid() references auth.users (id),
  lote text not null,
  prueba text not null,
  valor text not null,
  resultado text not null check (resultado in ('Aprobado', 'Rechazado', 'En revisión')),
  nota text default ''
);

-- ---------------- permisos (RLS) ----------------
alter table public.perfiles enable row level security;
alter table public.lotes enable row level security;
alter table public.paros enable row level security;
alter table public.calidad enable row level security;

drop policy if exists "perfiles: leer" on public.perfiles;
create policy "perfiles: leer" on public.perfiles for select to authenticated using (true);
drop policy if exists "perfiles: editar el propio" on public.perfiles;
create policy "perfiles: editar el propio" on public.perfiles for update to authenticated using (id = auth.uid());

do $$
declare t text;
begin
  foreach t in array array['lotes', 'paros', 'calidad'] loop
    execute format('drop policy if exists "%1$s: leer" on public.%1$s', t);
    execute format('create policy "%1$s: leer" on public.%1$s for select to authenticated using (true)', t);
    execute format('drop policy if exists "%1$s: registrar" on public.%1$s', t);
    execute format('create policy "%1$s: registrar" on public.%1$s for insert to authenticated with check (autor = auth.uid())', t);
    execute format('drop policy if exists "%1$s: editar lo propio" on public.%1$s', t);
    execute format('create policy "%1$s: editar lo propio" on public.%1$s for update to authenticated using (autor = auth.uid())', t);
    execute format('drop policy if exists "%1$s: borrar lo propio" on public.%1$s', t);
    execute format('create policy "%1$s: borrar lo propio" on public.%1$s for delete to authenticated using (autor = auth.uid())', t);
  end loop;
end $$;

-- tiempo real: los demás portátiles ven cada registro apenas se guarda
alter publication supabase_realtime add table public.lotes, public.paros, public.calidad;

-- ---------------- archivos ----------------
insert into storage.buckets (id, name, public) values ('mes-archivos', 'mes-archivos', false)
  on conflict (id) do nothing;

drop policy if exists "archivos: leer" on storage.objects;
create policy "archivos: leer" on storage.objects for select to authenticated using (bucket_id = 'mes-archivos');
drop policy if exists "archivos: subir" on storage.objects;
create policy "archivos: subir" on storage.objects for insert to authenticated with check (bucket_id = 'mes-archivos');
drop policy if exists "archivos: borrar lo propio" on storage.objects;
create policy "archivos: borrar lo propio" on storage.objects for delete to authenticated using (bucket_id = 'mes-archivos' and owner = auth.uid());
