# MES · conexión con Supabase

La página del MES (`web/src/pages/mes.astro`) usa Supabase para el inicio de sesión, los registros compartidos (lotes, paros y calidad) y los archivos.

## Puesta en marcha (una sola vez)

1. Crear el proyecto en [supabase.com](https://supabase.com) (plan gratis), región São Paulo.
2. **SQL Editor → New query**: pegar `esquema.sql` y ejecutarlo. Crea las tablas, los permisos, el tiempo real y el almacén `mes-archivos`.
3. **Authentication → Sign In / Providers → Email**: desactivar *Allow new users to sign up* (los usuarios los crea el administrador).
4. **Authentication → Users → Add user → Create new user**: correo y contraseña de cada persona, con *Auto Confirm User*. El nombre y el rol se editan en la tabla `perfiles` (Table Editor).
5. **Project Settings → API**: copiar la *Project URL* y la clave *anon / publishable* en `web/src/data/mes.json`. Nunca usar la clave `service_role` en la página.
6. Compilar y publicar la página.

## Roles

`Operario`, `Supervisor`, `Calidad`, `Mantenimiento`, `Jefe de planta` y `Administrador`. Todos los usuarios con sesión leen y registran; cada uno solo puede editar o borrar lo que registró.
