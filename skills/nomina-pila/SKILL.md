---
name: nomina-pila
description: Úsela cuando un contador o empresario necesite liquidar la nómina del mes de uno o varios trabajadores, revisar la PILA (salud, pensión, ARL, caja, SENA e ICBF), calcular la retención en la fuente laboral o saber cuánto le cuesta de verdad un trabajador. Las cifras salen del motor fiscal con su norma.
version: 1.0.0
author: Legal-IA
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - POST /v1/nomina/liquidar
    - GET /v1/versiones
---

> Las cifras (IBC, aportes, parafiscales, provisiones, retención, neto y costo) salen solo del motor fiscal. No multiplique tasas a mano. Lo único que se hace fuera del motor es sumar las cifras que el motor devolvió por trabajador, mostrando los sumandos. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Nómina del mes y aportes (PILA)

Liquida, trabajador por trabajador, lo que se le paga, lo que se le descuenta, lo que el empleador aporta a seguridad social y parafiscales y lo que debe provisionar para prestaciones. Sirve para cerrar la nómina, cuadrar la PILA antes de pagarla y responder «¿cuánto me cuesta este empleado?».

## Cuándo usarla

- Cierre de nómina mensual o quincenal (envíe los días laborados).
- Revisar una PILA ya liquidada por el operador o por el software de nómina.
- Calcular la retención en la fuente de un trabajador (procedimiento 1).
- Presupuestar una contratación: costo total del empleador según el salario.

No la use para aportes de independientes o contratistas, liquidación final del contrato (indemnización, días pendientes), nómina electrónica (XML) ni para generar el archivo plano de la PILA: el motor no los hace.

## Paso 1. Datos del empleador

| Dato | Para qué |
| --- | --- |
| Año del pago | SMMLV, auxilio de transporte y UVT del año |
| ¿Es sociedad declarante de renta, o persona natural con dos o más trabajadores? | Exoneración de salud, SENA e ICBF (art. 114-1 E.T.) |
| Clase de riesgo de la ARL (1 a 5) por centro de trabajo | Aporte a riesgos laborales |

Si el empleador es entidad sin ánimo de lucro, persona natural con un solo trabajador o no está seguro, envíe `empleador_exonerado_114_1` en `false` y dígalo.

## Paso 2. Datos por trabajador

| Dato | Campo del motor |
| --- | --- |
| Salario mensual pactado (tiempo completo) | `salario_basico` |
| Días laborados del mes | `dias` (30 si fue el mes completo) |
| ¿Salario integral? | `salario_integral` |
| Horas extra, recargos, comisiones, bonificaciones salariales | `otros_pagos_salariales` |
| Pagos pactados como no salariales (bonos, auxilios de alimentación) | `pagos_no_salariales` |
| Para la retención: dependientes, intereses de vivienda, medicina prepagada, aportes voluntarios y AFC del mes | `retencion` |

El auxilio de transporte no se envía: el motor lo pone si el salario no pasa de 2 SMMLV. Incapacidades, licencias y vacaciones disfrutadas no están modeladas: liquide los días trabajados y dígale al usuario que esas novedades se ajustan aparte.

## Paso 3. Liquide cada trabajador

Una llamada a `nomina/liquidar` por trabajador. Con varios, llame en serie y arme la tabla del entregable.

## Paso 4. Revise lo que el motor advierte

- **Pagos no salariales sobre el 40 %.** El exceso entra al IBC (Ley 1393 de 2010, art. 30). Explíquelo: muchas PILA lo omiten.
- **Exoneración que no aplica.** Si el trabajador devenga 10 SMMLV o más, el empleador paga salud, SENA e ICBF aunque sea exonerado.
- **Salario inferior al mínimo.** El IBC se lleva al mínimo proporcional.
- **Fondo de Solidaridad Pensional.** El motor usa la escala de la Ley 797 de 2003 y lo advierte; la Ley 2381 de 2024 podría cambiarla.

## Cálculo (motor fiscal)

Endpoint: `POST /v1/nomina/liquidar`. En el MCP, la herramienta `nomina_liquidar`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/nomina/liquidar" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"anio":2026,"salario_basico":3000000,"clase_riesgo_arl":1,"empleador_exonerado_114_1":true,"retencion":{"dependiente":false}}'
```

Reporte, sin alterar: `devengos`, `ibc`, `aportes_trabajador`, `aportes_empleador`, `exoneracion_114_1`, `provisiones`, `retencion` (`base_depurada`, `tarifa_marginal`, `retencion`), `neto_a_pagar`, `costo_total_empleador`, `parametros` (SMMLV, auxilio y UVT con su fuente), `base_legal` y `advertencias`. Un 422 por año significa que ese año no tiene SMMLV o auxilio publicados: no los estime.

Cite siempre `version_tablas`.

## Entregable

1. **Tabla por trabajador:** devengado, auxilio, IBC, descuentos (salud, pensión, FSP, retención), neto a pagar.
2. **Resumen de la PILA del mes:** por subsistema (salud, pensión, FSP, ARL, caja, SENA, ICBF), la suma de lo que el motor dio para cada trabajador, separando trabajador y empleador. Muestre los sumandos.
3. **Provisiones del mes:** cesantías, intereses, prima y vacaciones, por trabajador y en total, para el asiento contable.
4. **Costo total del empleador** por trabajador y de la nómina.
5. **Alertas:** las `advertencias` del motor y las novedades que no se modelaron.
6. **Cierre:** `version_tablas`, la fuente del SMMLV y del auxilio, y que la liquidación es un documento de trabajo que el contador revisa antes de pagar.

Si el usuario usa la app de Claude, entregue la tabla y el resumen como un artefacto.

## Límites

- Un trabajador dependiente por llamada, un mes por llamada. Años 2025 y 2026.
- ARL con la tarifa mínima de cada clase: si la ARL cobra una tarifa distinta dentro del rango, el aporte cambia.
- No modela incapacidades, licencias, vacaciones disfrutadas, aprendices SENA, trabajadores por días ni el pago de la prima o las cesantías: solo su provisión.
- Retención solo por el procedimiento 1.
- No genera el archivo de la PILA ni la nómina electrónica.
