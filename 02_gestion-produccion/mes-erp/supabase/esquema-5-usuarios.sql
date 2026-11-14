-- MES · quinta parte: usuarios del equipo con nombre corto y acceso total.
-- El MES deja entrar con "pablo" y por dentro usa pablo@mekvra.test (dominio reservado, no recibe correos).
-- Acceso total (pleno): la persona conserva su rol (define con qué pantalla arranca), pero puede hacer
-- todo lo que hace el administrador. Se quita en la tabla perfiles (pleno = false).
--
-- Crear usuarios (desde el SQL Editor). Si no se da clave, la base de datos inventa una y la muestra:
--   select public.crear_usuario('pablo', 'Pablo Arcila', 'Mantenimiento');

alter table public.perfiles add column if not exists pleno boolean not null default true;
update public.perfiles set pleno = true;

-- con acceso total, los permisos se evalúan como administrador
create or replace function public.mi_rol() returns text
language sql stable security definer set search_path = public as $$
  select coalesce((select case when pleno then 'Administrador' else rol end from public.perfiles where id = auth.uid()), '')
$$;

drop function if exists public.crear_usuario(text, text, text, text);
create or replace function public.crear_usuario(usuario text, nombre text, rol text, clave text default null)
returns text language plpgsql security definer set search_path = public, extensions, auth as $$
declare uid uuid := gen_random_uuid(); correo text := lower(trim(usuario)) || '@mekvra.test';
begin
  clave := coalesce(clave, lower(trim(usuario)) || '-' || lpad((floor(random() * 9000) + 1000)::int::text, 4, '0'));
  if length(clave) < 6 then raise exception 'La clave debe tener al menos 6 caracteres'; end if;
  if exists (select 1 from auth.users where email = correo) then raise exception 'Ya existe el usuario %', usuario; end if;
  insert into auth.users (instance_id, id, aud, role, email, encrypted_password, email_confirmed_at,
                          raw_app_meta_data, raw_user_meta_data, created_at, updated_at,
                          confirmation_token, email_change, email_change_token_new, recovery_token)
  values ('00000000-0000-0000-0000-000000000000', uid, 'authenticated', 'authenticated', correo,
          crypt(clave, gen_salt('bf')), now(), '{"provider":"email","providers":["email"]}',
          jsonb_build_object('nombre', nombre, 'rol', rol), now(), now(), '', '', '', '');
  insert into auth.identities (id, user_id, provider_id, identity_data, provider, last_sign_in_at, created_at, updated_at)
  values (gen_random_uuid(), uid, uid::text, jsonb_build_object('sub', uid::text, 'email', correo, 'email_verified', true),
          'email', now(), now(), now());
  return format('usuario: %s   ·   clave: %s   ·   %s (%s)', initcap(trim(usuario)), clave, nombre, rol);
end $$;

revoke execute on function public.crear_usuario(text, text, text, text) from public, anon, authenticated;
