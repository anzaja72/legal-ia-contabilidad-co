---
name: planeacion-tributaria-persona-natural
description: Úsela cuando una persona natural quiera pagar menos impuesto de renta
  de forma legal, comparar escenarios (AFC, dependientes, medicina prepagada) o
  entender por qué su tasa efectiva es alta. Las cifras salen del motor fiscal.
version: 1.0.0
author: Alfred - MC Consultorías
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - POST /v1/renta/calcular
    - POST /v1/renta/simular
---

> Las cifras de esta skill (impuesto, base, ahorro, saldo) salen solo del motor fiscal. No multiplique tarifas ni estime un ahorro a mano. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Planeación tributaria de persona natural (formulario 210)

Planeación es elegir, entre lo que la ley permite, la opción que deja menos impuesto sin crear riesgo. No es esconder ingresos ni inventar gastos. Esta skill ordena el trabajo en cuatro pasos y deja que el motor haga todas las cuentas.

## Cuándo usarla

- La persona pregunta cómo reducir su impuesto de renta del año gravable 2025.
- Quiere saber cuánto ahorra si aporta a AFC o a pensiones voluntarias.
- Quiere comparar «pagar menos impuesto» contra «no inmovilizar dinero».
- Tiene saldo a pagar alto y quiere entender la causa.

No la use para sociedades (use `planeacion-tributaria-persona-juridica`) ni para años distintos de 2025: el motor responde 422.

## Reglas que no se negocian

1. **Solo con información real.** Un dato que falta se declara faltante. No se completa con un supuesto favorable.
2. **El ahorro no basta.** Si la única explicación honesta de una idea es «pagar menos impuestos», se descarta aunque sea legal.
3. **Test del periódico.** Si la persona no podría explicar la idea en público sin incomodidad, no se recomienda.
4. **El motor calcula, usted cita.** Si no hay cifra del motor, escriba «no cuantificable con la información disponible».

## Clasifique cada idea antes de proponerla

| Zona | Qué es | Qué hacer |
| --- | --- | --- |
| Blanca | Economía de opción: la ley permite elegir expresamente | Siempre se presenta |
| Verde | Planeación legítima con sustancia económica real | Solo si pasa el test de propósito de negocio |
| Amarilla | Legal en la forma, sustancia dudosa | No se recomienda; va a «descartadas» con el motivo |
| Naranja | Elusión, abuso de formas (art. 869 E.T.) | Nunca |
| Roja | Evasión: omitir ingresos, gastos falsos | Nunca; si hay indicios, adviértalo |

En una persona natural asalariada o independiente, casi todo lo recomendable es zona blanca. No proponga crear sociedades, holdings ni figuras nuevas a partir de una declaración: una declaración no muestra sustancia económica.

## Palancas de zona blanca que el motor ya mide

- **Aportes a AFC y a pensiones voluntarias:** renta exenta, hasta el tope legal. Exige comprometer dinero.
- **Dependientes económicos:** deducción por cada dependiente real, hasta cuatro. No cuesta dinero, pero exige que el dependiente exista y cumpla el art. 387 E.T.
- **Medicina prepagada y pólizas de salud:** solo lo efectivamente pagado.
- **Intereses de crédito de vivienda o leasing habitacional:** solo los pagados y certificados.
- **Compras con factura electrónica:** deducción del 1 %, fuera del límite del 40 %.
- **Margen sin usar del límite del 40 % y 1.340 UVT:** el motor lo informa en la alerta `beneficios_sin_usar`.

## Procedimiento

1. **Inventario.** Reúna ingresos, aportes, retenciones, patrimonio y deudas. Liste aparte lo que no tiene.
2. **Caso actual.** Llame `calcular`. Lea el impuesto, el saldo y las alertas.
3. **Escenarios.** Llame `simular` con el mismo cuerpo. Devuelve el caso actual y dos escenarios.
4. **Recomendación.** Presente las palancas, su costo en liquidez y su zona. Diga qué soporte debe existir.

## Cálculo (motor fiscal)

### Caso actual

Endpoint: `POST /v1/renta/calcular`.

Campos del JSON (nombres reales del modelo): `vigencia` opcional (omisión: AG2025); `declaracion.datos_generales.nit` obligatorio; `declaracion.ingresos_laborales[]` con `ingresos_salarios`, `aportes_salud_arl`, `aportes_obligatorios_pension`, `aportes_afc_avc`, `retencion_fuente`; también `deducciones_vivienda`, `deducciones_salud`, `dependientes`, `ingresos_honorarios`, `ingresos_financieros`, `ingresos_dividendos`, `ganancias_ocasionales`, patrimonio y `deudas`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/renta/calcular" \
  -H "content-type: application/json" \
  -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"vigencia":"AG2025","declaracion":{"datos_generales":{"nit":"123456789"},"ingresos_laborales":[{"ingresos_salarios":120000000,"aportes_salud_arl":4800000,"aportes_obligatorios_pension":4800000,"aportes_afc_avc":10000000,"retencion_fuente":5000000}]}}'
```

Reporte, sin alterar: `casillas.casilla_111_renta_liquida_gravable`, `casilla_126_impuesto_neto_renta`, `casilla_129_total_impuesto_cargo`, `casilla_136_total_saldo_pagar`, `casilla_137_total_saldo_favor` y la alerta `beneficios_sin_usar` si viene. Cite `version_tablas` y `vigencia`.

### Escenarios

Endpoint: `POST /v1/renta/simular`. Mismo cuerpo que `calcular`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/renta/simular" \
  -H "content-type: application/json" \
  -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"vigencia":"AG2025","declaracion":{"datos_generales":{"nit":"123456789"},"ingresos_laborales":[{"ingresos_salarios":120000000,"aportes_salud_arl":4800000,"aportes_obligatorios_pension":4800000,"aportes_afc_avc":10000000,"retencion_fuente":5000000}]}}'
```

Reporte, sin alterar:

- `actual.resultado`: punto de partida.
- `escenario_minimo_impuesto`: `resultado`, `palancas`, `dinero_comprometido` y `ahorro_vs_actual`. Lleva las palancas al tope y exige dinero nuevo.
- `escenario_capacidad_financiera`: `resultado`, `palancas`, `ahorro_vs_actual` y `liquidez_preservada`. Usa solo palancas que no cuestan dinero.

Para probar una palanca que el simulador no arma (por ejemplo, un monto intermedio de AFC), cambie ese dato en el cuerpo y vuelva a llamar `calcular`. Compare las dos respuestas; no interpole.

## Entregable

1. **Diagnóstico:** impuesto y saldo actuales, en lenguaje llano.
2. **Oportunidades recomendadas:** palanca, zona, ahorro que dio el motor, dinero que compromete y soporte que exige.
3. **Oportunidades descartadas:** idea y motivo (zona amarilla o peor, o sin sustancia).
4. **Información que faltó:** qué no se pudo cuantificar y por qué.
5. **Cierre:** `version_tablas`, `vigencia` y que la decisión final es del contribuyente con su contador.

## Límites

- El simulador solo arma AFC, pensiones voluntarias, dependientes y medicina prepagada ya pagada.
- No cubre dividendos del exterior ni el año gravable 2026.
- Un aporte a AFC debe hacerse antes del 31 de diciembre del año gravable. Para el AG2025 ya no es posible: el escenario sirve para planear el año siguiente, y el motor todavía no tiene tablas de 2026.
