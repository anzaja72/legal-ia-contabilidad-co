---
name: estados-financieros-niif-pymes
description: Úsela cuando un contador en Colombia quiera armar, desde el balance de prueba, los estados financieros de fin de año de una empresa del grupo 2 (NIIF para Pymes, Decreto 2420 de 2015) o revisar unos ya hechos. Agrupa las cuentas en rubros, presenta los cuatro estados comparativos, propone el esqueleto de las notas y lista las certificaciones que exige la ley.
version: 1.0.0
author: Legal-IA
metadata:
  motor_fiscal:
    cobertura: ninguna
    endpoints: []
---

# Estados financieros bajo NIIF para Pymes

Al cierre del año, las empresas del grupo 2 presentan sus estados financieros con la NIIF para las Pymes (anexo 2 del Decreto 2420 de 2015). Esta skill toma el balance de prueba ya ajustado y lo convierte en los estados y el esqueleto de notas, para que el contador los revise, los complete y los firme.

## Cuándo usarla

- Al cierre del año, después de `cierre-anual-co` (ajustes) y antes de la asamblea.
- Para revisar la presentación de unos estados financieros hechos por otra persona.

No la use para empresas del grupo 1 (NIIF plenas) ni para microempresas del grupo 3 (contabilidad simplificada): pregunte el grupo si no está claro.

## Reglas que no se negocian

1. **Los saldos salen del balance de prueba ajustado.** Si el balance no cuadra (activo distinto de pasivo más patrimonio, o débitos distintos de créditos), se detiene y se dice.
2. **Comparativos.** Se presenta el año actual y el anterior (sección 3 de la NIIF para Pymes).
3. **Las políticas contables y los juicios son del contador.** La skill propone redacción de notas con base en lo que él indique; no inventa políticas ni cifras.
4. **Lo que firma el representante legal y el contador no lo firma la skill.**

## Los cuatro estados y las notas

| Estado | Qué muestra | Sección NIIF para Pymes |
| --- | --- | --- |
| Situación financiera | Activos, pasivos y patrimonio, corrientes y no corrientes | 4 |
| Resultado integral | Ingresos, costos, gastos, impuesto y resultado del año | 5 |
| Cambios en el patrimonio | Movimiento de capital, reservas y resultados | 6 |
| Flujos de efectivo | Efectivo de operación, inversión y financiación | 7 |
| Notas | Políticas, juicios y detalle de cada rubro | 8 |

## Agrupación del PUC en rubros

| Rubro | Cuentas PUC habituales |
| --- | --- |
| Efectivo y equivalentes | 11 |
| Inversiones | 12 |
| Deudores comerciales y otras cuentas por cobrar | 13 (sin 1355) |
| Activos por impuestos corrientes | 1355 |
| Inventarios | 14 |
| Propiedades, planta y equipo | 15 (neto de depreciación) |
| Intangibles | 16 |
| Obligaciones financieras | 21 |
| Proveedores y cuentas por pagar | 22, 23 |
| Pasivos por impuestos corrientes | 24 |
| Beneficios a empleados | 25 |
| Provisiones y otros pasivos | 26, 27, 28 |
| Patrimonio | 3 (capital, reservas, resultados) |
| Ingresos de actividades ordinarias | 41 |
| Otros ingresos | 42 |
| Costo de ventas | 6 y 7 |
| Gastos de administración y de ventas | 51, 52 |
| Otros gastos y gastos financieros | 53 |
| Impuesto de renta | 54 |

Adapte la agrupación al plan de cuentas del cliente y explique cualquier reclasificación (por ejemplo, la porción corriente de una deuda de largo plazo).

## Procedimiento

1. **Datos.** Balance de prueba ajustado al 31 de diciembre del año actual y del anterior, grupo NIIF de la empresa, políticas contables que aplica y hechos relevantes del año.
2. **Cuadre.** Verifique débitos contra créditos y activo contra pasivo más patrimonio.
3. **Agrupe** las cuentas en rubros con la tabla y presente la situación financiera y el resultado integral comparativos.
4. **Cambios en el patrimonio:** utilidad del año, distribuciones aprobadas, reserva legal y otros movimientos.
5. **Flujos de efectivo** por el método indirecto: utilidad, partidas que no mueven efectivo (depreciación, deterioro, provisiones), cambios en el capital de trabajo, inversión y financiación. El efectivo final debe coincidir con el rubro de efectivo.
6. **Notas:** esqueleto con información de la entidad, bases de preparación, políticas contables significativas, juicios y estimaciones, y una nota por rubro relevante, con los espacios que el contador debe completar.
7. **Certificación y dictamen:** recuerde la certificación del representante legal y del contador (art. 37 de la Ley 222 de 1995) y el dictamen del revisor fiscal si la sociedad está obligada a tenerlo (art. 38 de la Ley 222 de 1995).

## Entregable

1. **Los cuatro estados comparativos** en tablas, con los totales cuadrados.
2. **Esqueleto de notas** con lo que el contador debe completar marcado.
3. **Lista de reclasificaciones** hechas y su motivo.
4. **Pendientes:** diferencias de cuadre, información faltante y certificaciones por firmar.

Si el usuario lo pide, entregue los estados en Excel o Word con el formato de la empresa.

## Límites

- No calcula impuestos: la provisión de renta y el impuesto diferido vienen de `cierre-anual-co` y `conciliacion-fiscal`.
- No aplica NIIF plenas ni la contabilidad simplificada del grupo 3.
- No reemplaza el juicio profesional sobre políticas, estimaciones y revelaciones.
