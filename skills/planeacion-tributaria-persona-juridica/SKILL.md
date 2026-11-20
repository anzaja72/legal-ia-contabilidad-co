---
name: planeacion-tributaria-persona-juridica
description: Úsela cuando una sociedad quiera optimizar su impuesto de renta de
  forma legal, comparar escenarios del formulario 110 o medir si un beneficio se
  pierde por la tasa mínima del 15% o por el límite del 3%. Las cifras salen del motor.
version: 1.0.0
author: Alfred - MC Consultorías
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - POST /v1/renta-pj/calcular
    - GET /v1/renta-pj/regimenes
    - POST /v1/simple/calcular
---

> Las cifras de esta skill (impuesto, tasa efectiva, impuesto a adicionar, anticipo, saldo) salen solo del motor fiscal. No multiplique tarifas ni estime un ahorro a mano. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Planeación tributaria de persona jurídica (formulario 110)

En una sociedad, un beneficio tributario puede no ahorrar nada: la tasa mínima de tributación y el límite del 3 % lo devuelven como impuesto adicional. Esta skill compara escenarios con el motor para ver el efecto real antes de recomendar.

## Cuándo usarla

- Una sociedad nacional del régimen ordinario quiere reducir su impuesto de renta del año gravable 2025.
- Hay que decidir si conviene tomar una renta exenta, una deducción especial o un descuento.
- Hay que medir el efecto de compensar pérdidas fiscales este año.
- Hay que elegir la base del anticipo.

No la use para régimen tributario especial, zonas francas, extractivas, hoteleros al 15 %, entidades controladas del exterior ni grupos que consolidan: el motor responde 422.

## Reglas que no se negocian

1. **Solo con información real.** Un dato que falta se declara faltante. No se completa con un supuesto favorable.
2. **El ahorro no basta.** Si la única explicación honesta de una idea es «pagar menos impuestos», se descarta aunque sea legal.
3. **Test del periódico.** Si el representante legal no podría explicar la idea en público sin incomodidad, no se recomienda.
4. **El motor calcula, usted cita.** Si no hay cifra del motor, escriba «no cuantificable con la información disponible».

## Clasifique cada idea antes de proponerla

| Zona | Qué es | Qué hacer |
| --- | --- | --- |
| Blanca | Economía de opción: la ley permite elegir expresamente | Siempre se presenta |
| Verde | Planeación legítima con sustancia económica real | Solo si pasa el test de propósito de negocio |
| Amarilla | Legal en la forma, sustancia dudosa | No se recomienda; va a «descartadas» con el motivo |
| Naranja | Elusión, abuso de formas (art. 869 E.T.) | Nunca |
| Roja | Evasión: omitir ingresos, costos falsos | Nunca; si hay indicios, adviértalo |

### Test de propósito de negocio

Aplíquelo a toda idea que implique una estructura o un cambio de forma jurídica. Los cuatro filtros son acumulativos:

1. **Propósito comercial:** razón de negocio real, independiente del ahorro, ya presente en la información.
2. **Sustancia económica:** empleados, instalaciones, activos u operaciones reales. ¿Un funcionario de la DIAN encontraría algo real en una visita sin aviso?
3. **Eliminación hipotética:** si el beneficio fiscal desapareciera mañana, ¿la estructura seguiría teniendo sentido?
4. **Proporcionalidad:** beneficio comercial frente a beneficio fiscal, solo con cifras disponibles.

Si falla el filtro 1 o el 2, la idea se descarta. Si un filtro no se puede evaluar, márquela «verificar antes de implementar».

## Palancas que el motor permite medir

| Palanca | Qué cambiar en el cuerpo | Qué mirar en la respuesta |
| --- | --- | --- |
| Renta exenta o deducción especial | `renta_exenta`, `costos_y_gastos` y, si está en la lista del art. 259-1, `limite_beneficios` | Casillas 92, 94, 95 y 96 |
| Descuento tributario | `descuentos_tributarios` (y `limite_beneficios.descuentos_tributarios` si aplica) | Casillas 92, 93, 94 y 95 |
| Compensación de pérdidas fiscales | `compensaciones` y `tasa_minima.compensaciones` | Casillas 74, 79, 95 y 96 |
| Base del anticipo | `impuesto_neto_anio_anterior` y `anios_declarando` | Casilla 108 |
| Régimen ordinario frente a SIMPLE | Llamar también `POST /v1/simple/calcular` con los mismos ingresos | `casilla_99_total_impuesto_a_cargo` contra `total_a_cargo` |
| Ganancia ocasional frente a renta ordinaria | Mover el ingreso entre `ingresos` y `ganancias_ocasionales`, solo si la ley lo clasifica así | Casillas 84 y 97 |

Qué esperar, para explicarlo y no para calcularlo:

- **Tasa mínima (art. 240 par. 6):** si el impuesto depurado es menos del 15 % de la utilidad depurada, la casilla 95 sube el impuesto hasta ese piso. Un beneficio que baja la casilla 94 puede reaparecer en la 95.
- **Límite del 3 % (art. 259-1):** los beneficios que enumera ese artículo, por encima del 3 % de la renta líquida ordinaria, vuelven como valor a adicionar en la casilla 92.
- **Compensar pérdidas** baja la renta gravable, pero también entra a la utilidad depurada. Puede convenir guardarlas para otro año.

## Procedimiento

1. **Inventario.** Reúna las cifras fiscales ya depuradas por casilla y la utilidad contable antes de impuestos. Liste lo que no tiene.
2. **Régimen.** Confirme con `regimenes` que el caso se liquida.
3. **Caso base.** Llame `calcular` con los datos reales. Si falta `tasa_minima`, el estado es `parcial`: consiga la utilidad contable antes de seguir.
4. **Un escenario por palanca.** Cambie un solo dato y vuelva a llamar `calcular`.
5. **Compare** las casillas 94, 95, 96, 99, 108 y 113 entre el caso base y cada escenario. La diferencia la dan las dos respuestas; no la calcule aparte.
6. **Recomiende** solo lo que baja la casilla 99 o la 113 y pasa la clasificación por zonas.

## Cálculo (motor fiscal)

### Regímenes

Endpoint: `GET /v1/renta-pj/regimenes`. Devuelve `regimenes` (tarifa, puntos adicionales, umbral y norma) y `no_soportados`.

```bash
curl -fsS "$MOTOR_FISCAL_URL/v1/renta-pj/regimenes" -H "X-API-Key: $MOTOR_FISCAL_API_KEY"
```

### Caso base y escenarios

Endpoint: `POST /v1/renta-pj/calcular`.

Campos del JSON (nombres reales del modelo): `vigencia` opcional (omisión: AG2025); `regimen` (`general`, `financiera`, `hidroelectrica` o `editorial`); `patrimonio` y `pasivos`; `ingresos` (`actividades_ordinarias`, `financieros`, `dividendos_no_constitutivos`, `dividendos_gravados_tarifa_general`, `otros`); `devoluciones`; `ingresos_no_constitutivos`; `costos_y_gastos` (`costos`, `gastos_administracion`, `gastos_distribucion_ventas`, `gastos_financieros`, `otros_gastos_deducciones`); `renta_recuperacion_deducciones`; `compensaciones`; `renta_exenta`; `rentas_gravables`; `ganancias_ocasionales`; `descuentos_tributarios`; `descuento_impuestos_exterior`; `limite_beneficios`; `tasa_minima` (`utilidad_contable` obligatoria dentro del bloque); `anios_declarando`; `impuesto_neto_anio_anterior`; `anticipo_anio_anterior`; `saldo_favor_anio_anterior`; `autorretenciones`; `otras_retenciones`; `sanciones`. Un campo que no esté en esta lista responde 422.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/renta-pj/calcular" \
  -H "content-type: application/json" \
  -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"regimen":"general","ingresos":{"actividades_ordinarias":2000000000},"costos_y_gastos":{"costos":1200000000,"gastos_administracion":300000000},"otras_retenciones":50000000,"tasa_minima":{"utilidad_contable":480000000}}'
```

Reporte, sin alterar: `casillas.casilla_79_renta_liquida_gravable`, `casilla_84_impuesto_renta_liquida_gravable`, `casilla_92_valor_a_adicionar`, `casilla_94_impuesto_neto_sin_adicionado`, `casilla_95_impuesto_a_adicionar`, `casilla_96_impuesto_neto_con_adicionado`, `casilla_99_total_impuesto_a_cargo`, `casilla_108_anticipo_anio_siguiente`, `casilla_113_total_saldo_a_pagar` y `casilla_114_total_saldo_a_favor`. Cite también `tasa_minima.tasa_tributacion_depurada`, `estado`, `advertencias`, `version_tablas` y `vigencia`.

Si `estado` es `parcial`, la casilla 95 llegó en null: dígalo y no compare escenarios hasta tener la utilidad contable.

### Comparación con el SIMPLE

Endpoint: `POST /v1/simple/calcular`. Úselo solo si la sociedad puede estar en el SIMPLE: socios personas naturales residentes, ingresos del año anterior inferiores a 100.000 UVT y ninguna causal del art. 906 E.T. El motor no valida esos requisitos.

Campos del JSON (nombres reales del modelo): `periodo` (`anual`); `actividades[]` con `grupo` (`tiendas_peluquerias`, `comercio_industria_otros`, `comidas_transporte`, `educacion_salud`, `servicios_profesionales` o `ciiu_4665_3830_3811`) e `ingresos`; `ingresos_comidas_bebidas`; `tarifa_ica_consolidada_por_mil`; `aportes_pension_empleador`; `ingresos_medios_electronicos` o `gmf_pagado`; `ganancia_ocasional_gravable`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/simple/calcular" \
  -H "content-type: application/json" \
  -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"periodo":"anual","actividades":[{"grupo":"comercio_industria_otros","ingresos":2000000000}],"tarifa_ica_consolidada_por_mil":9}'
```

Reporte, sin alterar: `tarifa_simple`, `impuesto_simple`, `componente_ica_consolidado`, `total_descuentos` y `total_a_cargo`, con `version_tablas`. Al comparar, diga que el SIMPLE grava ingresos brutos y ya incluye el ICA, y que el ordinario grava la utilidad y el ICA se paga aparte: la comparación justa suma el ICA al ordinario.

## Entregable

1. **Diagnóstico:** impuesto, tasa de tributación depurada y saldo del caso base.
2. **Tabla de escenarios:** una fila por palanca con las casillas 94, 95, 96, 99 y 113 que devolvió el motor.
3. **Oportunidades recomendadas:** palanca, zona, efecto según el motor y soporte que exige.
4. **Oportunidades descartadas:** idea y motivo. Incluya aquí los beneficios que la tasa mínima o el límite del 3 % anulan.
5. **Información que faltó.**
6. **Cierre:** `version_tablas`, `vigencia`, los supuestos del motor (`advertencias`) y que la decisión es de la sociedad con su contador y su revisor fiscal.

## Límites

- El motor recibe cifras ya depuradas. No decide si un gasto es deducible ni hace la conciliación fiscal.
- No hay simulador automático: cada escenario es una llamada.
- La comparación con el SIMPLE no valida si la sociedad cumple los requisitos para acogerse.
- No calcula sanciones ni el año gravable 2026.
