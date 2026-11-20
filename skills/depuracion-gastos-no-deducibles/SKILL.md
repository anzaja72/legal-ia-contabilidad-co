---
name: depuracion-gastos-no-deducibles
description: Úsela cuando un contador quiera saber qué costos y gastos de una sociedad o persona obligada a llevar contabilidad no son deducibles en renta, revisar el auxiliar o el balance cuenta por cuenta contra los requisitos del Estatuto Tributario (causalidad, factura electrónica, medios de pago, seguridad social, límites) y medir con el motor cuánto impuesto cuesta cada partida rechazada.
version: 1.0.0
author: Legal-IA
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - POST /v1/renta-pj/calcular
---

> La skill clasifica y explica; el impuesto que cuesta cada partida lo calcula el motor. No multiplique por el 35 % en el chat. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Depuración de gastos no deducibles

Un gasto contable no siempre es deducible en renta. Esta skill revisa los costos y gastos contra los requisitos del Estatuto Tributario, separa los que no pasan, explica por qué con la norma y mide su efecto en el impuesto. El resultado alimenta la proyección (`proyeccion-renta-pj`) o la conciliación fiscal (`conciliacion-fiscal`).

## Cuándo usarla

- Antes de proyectar o declarar renta, para saber qué sumar como no deducible.
- Para revisar el auxiliar de gastos de un período y corregir soportes a tiempo.
- Cuando el cliente pregunta «¿esto me lo puedo deducir?».

## Reglas que no se negocian

1. **Cada rechazo lleva su norma.** Si no hay norma clara, la partida va como «revisar», no como no deducible.
2. **El soporte manda.** Un gasto real sin factura electrónica o sin pago bancario puede no ser deducible aunque sea necesario. Dígalo.
3. **No se rechaza por sospecha.** Si falta información (¿hubo pago en efectivo?, ¿el contratista aportó a seguridad social?), se pregunta.
4. **La decisión es del contador.** La skill propone y explica; él confirma cada partida.

## Requisitos que se revisan, en este orden

### 1. Requisitos generales (art. 107 E.T.)

El gasto debe tener **relación de causalidad** con la actividad que produce la renta, ser **necesario** y **proporcional**. Ejemplos que suelen fallar: gastos personales de socios, vehículos que no se usan en el negocio, regalos sin relación con la actividad.

### 2. Soporte (arts. 616-1 y 771-2 E.T.)

- Compras a responsables de IVA y facturadores: **factura electrónica** válida ante la DIAN.
- Pagos a quienes no están obligados a facturar: **documento soporte electrónico**.
- Nómina: **nómina electrónica** transmitida a la DIAN para que los pagos laborales sean deducibles.
- Compras a crédito: los eventos de recibo en RADIAN cuando la factura se use como título valor.

### 3. Medios de pago (art. 771-5 E.T.)

- Los pagos en efectivo individuales por más de **100 UVT** no son deducibles.
- Lo pagado en efectivo solo se reconoce hasta el menor entre el **40 %** de lo efectivamente pagado y el **35 %** de los costos y deducciones totales (par. 1).
- Para revisarlo pida el auxiliar de caja o el reporte de pagos por medio.

### 4. Seguridad social y aportes (art. 108 E.T.)

- Salarios: deducibles si se pagaron los aportes a seguridad social y parafiscales que correspondan.
- Contratistas personas naturales: verificar que el pago tenga el soporte de sus aportes a seguridad social.

### 5. Gastos que la ley excluye o limita

| Partida | Tratamiento | Norma |
| --- | --- | --- |
| Impuesto de renta y complementarios | No deducible | Art. 115 E.T. |
| Gravamen a los movimientos financieros (4×1000) | Deducible el 50 % certificado | Art. 115 E.T. |
| Multas, sanciones y penalidades | No deducibles | Art. 105 E.T. |
| Intereses de mora sobre impuestos | No deducibles | Art. 11 de la Ley 1430 de 2010 |
| Costos y gastos de ejercicios anteriores | No deducibles en el año (no se realizaron en él) | Arts. 59 y 105 E.T. |
| Atenciones a clientes, proveedores y empleados (regalos, cortesías, fiestas) | Deducibles hasta el 1 % del ingreso fiscal neto | Art. 107-1 E.T. |
| Intereses con vinculados económicos | Limitados por subcapitalización (deuda hasta 2 veces el patrimonio líquido) | Art. 118-1 E.T. |
| Pagos a jurisdicciones no cooperantes o de baja imposición | Deducibles solo con retención y documentación | Art. 124-2 E.T. |
| Donaciones a entidades del régimen especial | No son deducción; dan descuento del 25 % | Art. 257 E.T. |
| Costos y gastos asociados a ingresos no gravados o rentas exentas | No deducibles en la parte asociada | Art. 177-1 E.T. |

Ante una partida que no esté en esta tabla, explique la duda y márquela «revisar».

## Procedimiento

1. **Obtenga los datos.** Balance de prueba o auxiliar de gastos del período (Excel o CSV). Si viene de `proyeccion-renta-pj`, use su lista `cuentas_a_revisar_no_deducibles` como punto de partida.
2. **Clasifique cada cuenta** en una de tres columnas: deducible, no deducible (con norma) y revisar (con la pregunta que falta).
3. **Pida lo que falta** en un solo mensaje: pagos en efectivo, soportes de seguridad social, facturas no electrónicas, vinculados económicos.
4. **Separe a la fecha y proyectado** si el cálculo es de mitad de año: cada partida una sola vez.
5. **Mida el efecto en el impuesto** con el motor: dos llamadas a `POST /v1/renta-pj/calcular`, una sin los no deducibles y otra con ellos, y reporte la diferencia de las casillas que devuelva.

## Cálculo (motor fiscal)

Endpoint: `POST /v1/renta-pj/calcular`. Los no deducibles se restan de `costos_y_gastos.otros_gastos_deducciones` (o del grupo que corresponda) y, sin el impuesto de renta, van en `tasa_minima.diferencias_permanentes`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/renta-pj/calcular" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"regimen":"general","ingresos":{"actividades_ordinarias":2000000000},"costos_y_gastos":{"costos":900000000,"gastos_administracion":500000000,"gastos_distribucion_ventas":300000000,"otros_gastos_deducciones":20000000},"tasa_minima":{"utilidad_contable":300000000,"diferencias_permanentes":25000000},"anios_declarando":3}'
```

Reporte de cada llamada: `casilla_75_renta_liquida`, `casilla_99_total_impuesto_a_cargo`, `tasa_minima.tasa_tributacion_depurada`, `version_tablas` y `vigencia`. El costo tributario de los no deducibles es la diferencia de `casilla_99_total_impuesto_a_cargo` entre las dos respuestas, tal como la entregó el motor.

## Entregable

1. **Tabla de partidas:** cuenta, nombre, valor, clasificación (deducible / no deducible / revisar), norma y motivo.
2. **Preguntas pendientes** para el cliente, agrupadas.
3. **Efecto en el impuesto** según el motor, con `version_tablas`.
4. **Recomendaciones de soporte** para corregir antes del cierre: facturas, pagos bancarios, seguridad social de contratistas.

## Límites

- No decide sobre deterioro de cartera, depreciaciones fiscales ni impuesto diferido: eso va en `conciliacion-fiscal`.
- No verifica en la DIAN si una factura es válida; pide el soporte o el reporte del proveedor tecnológico.
- Los límites porcentuales se calculan con las cifras que entregue el contador; si faltan, se marcan «revisar».
