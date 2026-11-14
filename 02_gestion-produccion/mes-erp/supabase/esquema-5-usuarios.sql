-- MES · quinta parte: crear usuarios del equipo con un nombre corto (sin correo real).
-- El MES deja entrar con "pablo" y por dentro usa pablo@mekvra.test (dominio reservado, no recibe correos).
-- Uso (solo desde el SQL Editor, cada quien con su propia clave):
--   select public.crear_usuario('pablo', 'Pablo Arcila', 'Supervisor', 'la-clave');

create or replace function public.crear_usuario(usuario text, nombre text, rol text, clave text)
returns text language plpgsql security definer set search_path = public, extensions, auth as $$
declare uid uuid := gen_random_uuid(); correo text := lower(trim(usuario)) || '@mekvra.test';
begin
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
  return format('Usuario %s (%s) creado como %s', usuario, nombre, rol);
end $$;

revoke execute on function public.crear_usuario(text, text, text, text) from public, anon, authenticated;
