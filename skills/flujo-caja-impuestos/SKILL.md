---
name: flujo-caja-impuestos
description: Úsela cuando un contador o empresario en Colombia quiera saber cuánta plata necesita, mes a mes, para pagar impuestos en los próximos meses (renta y sus cuotas, anticipo, IVA, retenciones, ICA y SIMPLE) y cuánto le cuesta pagar tarde. Arma el calendario de salidas de caja con cifras del motor fiscal.
version: 1.0.0
author: Legal-IA
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - POST /v1/renta-pj/calcular
    - POST /v1/iva/liquidar
    - POST /v1/simple/calcular
    - POST /v1/intereses/moratorio-dian
---

> Cada valor del flujo sale de una respuesta del motor o de una cifra que dio el contador. La skill no estima un impuesto ni reparte una cuota sin la norma o el calendario que la respalde. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Flujo de caja de impuestos

Los impuestos son salidas de caja con fecha fija. Esta skill las pone en un calendario mensual para que la empresa sepa cuánto apartar y cuándo, y muestra cuánto cuesta pagar tarde con el interés de mora de la DIAN.

## Cuándo usarla

- Al planear el presupuesto o el flujo de caja del año.
- Después de una proyección de renta (`proyeccion-renta-pj`), para saber cuándo se paga.
- Cuando la empresa evalúa pagar tarde o pedir un acuerdo de pago.

## Reglas que no se negocian

1. **Fechas del calendario oficial.** Las cuotas y vencimientos salen del decreto de calendario tributario y de las resoluciones municipales del año. Pídalas o pida el último dígito del NIT y la calidad del contribuyente (gran contribuyente, persona jurídica, régimen SIMPLE). Sin calendario, el flujo va por mes estimado y se dice.
2. **El monto lo da el motor** o el contador. No se reparte el impuesto en cuotas con un porcentaje supuesto.
3. **Pagar tarde no es una opción neutra:** el costo de la mora se calcula y se muestra.

## Componentes del flujo

| Impuesto | De dónde sale el monto | Cuándo se paga |
| --- | --- | --- |
| Renta del año anterior | Motor (`POST /v1/renta-pj/calcular`, casilla 113) | En las cuotas del decreto de calendario según la calidad del contribuyente |
| Anticipo del año siguiente | Motor (casilla 108) | Se paga junto con la renta; reduce la del año siguiente |
| Retención en la fuente y autorretención | Retenciones practicadas del mes (contabilidad) | Mensual, formulario 350 |
| IVA | Motor (`POST /v1/iva/liquidar`) con las ventas y compras proyectadas | Bimestral o cuatrimestral (art. 600 E.T.) |
| ICA | Declaraciones municipales (`ica-liquidar-declaracion`) | Anual o bimestral según la ciudad |
| SIMPLE | Motor (`POST /v1/simple/calcular`, `periodo` `bimestral`) | Anticipos bimestrales y declaración anual |
| Interés de mora | Motor (`POST /v1/intereses/moratorio-dian`) | Solo si se paga después del vencimiento |

## Procedimiento

1. **Datos.** Proyección de ingresos y compras por mes, última declaración de renta, régimen, periodicidad de IVA, ciudades donde declara ICA y calendario del año.
2. **Liquide cada impuesto** en el motor con las cifras del período que corresponda.
3. **Ubique cada pago** en su mes según el calendario. Si la renta se paga en cuotas, use las fechas y la división que fija el decreto para esa calidad de contribuyente.
4. **Sume por mes** las salidas y muestre el total del año.
5. **Si evalúan pagar tarde,** liquide el interés de mora con el motor para la fecha de pago que propongan y póngalo al lado del valor del impuesto.

## Cálculo (motor fiscal)

### Renta y anticipo

Use `POST /v1/renta-pj/calcular` como en `proyeccion-renta-pj` y tome `casilla_113_total_saldo_a_pagar` y `casilla_108_anticipo_anio_siguiente`.

### IVA de un bimestre proyectado

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/iva/liquidar" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"periodo":{"tipo":"bimestre","numero":1,"anio":2026},"ventas_gravadas_19":150000000,"compras_descontables_19":80000000}'
```

### Anticipo bimestral del SIMPLE

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/simple/calcular" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"periodo":"bimestral","anio":2026,"actividades":[{"grupo":"comercio_industria_otros","ingresos":180000000}]}'
```

### Costo de pagar tarde

Endpoint: `POST /v1/intereses/moratorio-dian`. Campos: `impuesto` (valor en mora), `fecha_vencimiento`, `fecha_pago` y, si los hay, `abonos`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/intereses/moratorio-dian" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"impuesto":50000000,"fecha_vencimiento":"2026-05-12","fecha_pago":"2026-08-12"}'
```

Reporte el interés que entregue el motor, su `base_legal`, `version_tablas` y `vigencia`. Si la fecha de pago es posterior a la última tasa publicada, el motor lo dice: no complete la tasa.

## Entregable

1. **Tabla mes a mes:** impuesto, valor, fecha límite y fuente (motor o contador).
2. **Total por mes y del año**, con los meses de mayor salida resaltados.
3. **Costo de la mora** si se evaluó pagar tarde.
4. **Supuestos:** proyecciones usadas, calendario aplicado y vigencia del motor.

## Límites

- No proyecta ventas ni compras: usa las que entregue el contador.
- No conoce por sí mismo las fechas de vencimiento de personas jurídicas ni las municipales; las pide.
- No incluye nómina ni aportes PILA (pendiente en el motor).
