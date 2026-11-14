-- MES de Lácteos Altos de Teusacá (Mekvra S.A.S) · cuarta parte: costos y consumos para la gerencia
-- Precios y consumos son SUPUESTOS de trabajo (COP 2026, orden de magnitud de la industria láctea colombiana).
-- La gerencia o el administrador los edita desde el MES; la página siempre los muestra como supuestos.

create table if not exists public.parametros (
  clave text primary key,
  grupo text not null,
  nombre text not null,
  valor numeric not null check (valor >= 0),
  unidad text not null default '',
  orden int not null default 0
);

insert into public.parametros (clave, grupo, nombre, valor, unidad, orden) values
  ('leche', 'Insumos', 'Leche cruda pagada al productor', 1950, 'COP/L', 1),
  ('energia', 'Insumos', 'Energía eléctrica', 850, 'COP/kWh', 2),
  ('gas', 'Insumos', 'Gas natural (calderas y UHT)', 2100, 'COP/m³', 3),
  ('agua', 'Insumos', 'Agua', 6500, 'COP/m³', 4),
  ('cip', 'Insumos', 'Químicos por limpieza CIP', 180000, 'COP/ciclo', 5),
  ('precio_YF', 'Precio de venta', 'YF · Yogurt con fresa', 7800, 'COP/L', 10),
  ('precio_YN', 'Precio de venta', 'YN · Yogurt natural', 6900, 'COP/L', 11),
  ('precio_YG', 'Precio de venta', 'YG · Yogurt griego', 16500, 'COP/L', 12),
  ('precio_QM', 'Precio de venta', 'QM · Mozzarella (por L de leche)', 2650, 'COP/L', 13),
  ('precio_QQ', 'Precio de venta', 'QQ · Quesillo (por L de leche)', 2450, 'COP/L', 14),
  ('precio_QD', 'Precio de venta', 'QD · Doble crema (por L de leche)', 2600, 'COP/L', 15),
  ('precio_LE', 'Precio de venta', 'LE · Leche entera UHT', 3900, 'COP/L', 16),
  ('precio_LD', 'Precio de venta', 'LD · Leche descremada UHT', 3900, 'COP/L', 17),
  ('precio_LC', 'Precio de venta', 'LC · Leche con chocolate UHT', 4700, 'COP/L', 18),
  ('leche_YG', 'Rendimiento', 'Leche por litro de yogurt griego', 3, 'L/L', 20),
  ('leche_otros', 'Rendimiento', 'Leche por litro de los demás productos', 1.05, 'L/L', 21),
  ('otros_YF', 'Rendimiento', 'Fruta, azúcar y empaque · yogurt con fresa', 1400, 'COP/L', 22),
  ('otros_Y', 'Rendimiento', 'Cultivos y empaque · yogurt natural y griego', 900, 'COP/L', 23),
  ('otros_Q', 'Rendimiento', 'Cuajo, sal y empaque · quesos (por L de leche)', 220, 'COP/L', 24),
  ('otros_L', 'Rendimiento', 'Envase aséptico · leche UHT', 650, 'COP/L', 25),
  ('meta_dia', 'Metas', 'Litros de producto por día (meta)', 150000, 'L/día', 30)
on conflict (clave) do nothing;

alter table public.parametros enable row level security;
drop policy if exists "parametros: leer" on public.parametros;
create policy "parametros: leer" on public.parametros for select to authenticated using (true);
drop policy if exists "parametros: editar" on public.parametros;
create policy "parametros: editar" on public.parametros for update to authenticated
  using (public.mi_rol() in ('Gerencia', 'Jefe de planta', 'Administrador'));

-- consumo de cada máquina: kW en marcha (en reposo se toma el 15 %), gas y agua por hora en marcha
alter table public.sim_maquina add column if not exists kw numeric not null default 0;
alter table public.sim_maquina add column if not exists gas_m3h numeric not null default 0;
alter table public.sim_maquina add column if not exists agua_m3h numeric not null default 0;
update public.sim_maquina s set kw = v.kw, gas_m3h = v.gas, agua_m3h = v.agua
from (values ('U111', 15, 0, 0.5), ('U121', 30, 22, 1.5), ('U201', 11, 0, 0.3), ('U202', 22, 15, 1.0), ('U211', 18, 4, 0.2),
             ('U215', 37, 0, 0.8), ('U216', 45, 0, 0.6), ('U311', 22, 0, 0.2), ('U312', 18, 0, 0.2), ('U313', 15, 0, 0.2),
             ('U321', 7.5, 0, 0), ('U341', 5, 0, 0), ('Q201', 7.5, 3, 0.4), ('Q202', 7.5, 3, 0.4), ('Q203', 7.5, 3, 0.4),
             ('Q301', 30, 10, 1.2), ('Q311', 11, 0, 0.1), ('L202', 55, 38, 2.0), ('L311', 30, 0, 0.4)) as v(codigo, kw, gas, agua)
where s.codigo = v.codigo;

do $$ begin
  alter publication supabase_realtime add table public.parametros;
exception when duplicate_object then null; end $$;

-- historia de 5 días de la planta simulada
select public.sim_sembrar(5);
