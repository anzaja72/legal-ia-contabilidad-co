---
name: cierre-mensual-co
description: Úsela cuando un contador en Colombia vaya a cerrar el mes de una empresa. Cubre conciliaciones, causaciones, nómina electrónica, facturación electrónica y eventos RADIAN, y prepara las declaraciones del período (retención en la fuente, IVA, reteICA y autorretención) con las cifras verificadas por el motor fiscal.
version: 1.0.0
author: Legal-IA
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - POST /v1/retenciones/retefuente
    - POST /v1/retenciones/reteica
    - POST /v1/retenciones/reteiva
    - POST /v1/retenciones/autorretencion
    - POST /v1/iva/liquidar
---

> Las retenciones, el IVA y la autorretención los liquida el motor. La skill ordena el cierre y verifica; no recalcula tarifas en el chat. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Cierre mensual contable y tributario

El cierre del mes deja la contabilidad conciliada y las obligaciones del período listas para declarar. Esta skill lo recorre en cuatro bloques, del dato al impuesto, y verifica con el motor las retenciones y el IVA que se van a declarar.

## Cuándo usarla

- En los primeros días del mes, para cerrar el mes anterior.
- Antes de presentar el formulario 350 (retenciones), el 300 (IVA) o la declaración de reteICA.
- Para revisar el cierre que hizo un auxiliar.

Para el cierre del año use `cierre-anual-co`, que incluye este mismo recorrido para diciembre.

## Reglas que no se negocian

1. **Primero conciliado, después declarado.** No se liquida un impuesto sobre cifras sin conciliar.
2. **Las fechas salen del calendario oficial.** Pregunte el último dígito del NIT y la ciudad. Si no tiene el calendario del año, dígalo; no suponga vencimientos.
3. **Ausente no es cero.** Si un auxiliar no llegó, el cierre queda pendiente en ese punto.

## Los cuatro bloques

### 1. Conciliaciones

- [ ] Bancos y cuentas de pago (pasarelas, billeteras): saldo en libros contra extracto; partidas conciliatorias con antigüedad.
- [ ] Cartera: auxiliar contra informe de clientes; abonos sin identificar.
- [ ] Proveedores: auxiliar contra estados de cuenta de los principales.
- [ ] Anticipos e impuestos a favor (1355): retenciones que le practicaron, con certificado o soporte.
- [ ] Inventarios: kárdex contra contabilidad, si aplica.

### 2. Causaciones y ajustes del mes

- [ ] Facturas de compra del mes causadas, incluidas las que llegaron tarde.
- [ ] Depreciación y amortización del mes.
- [ ] Provisiones de nómina: cesantías, intereses, prima y vacaciones.
- [ ] Gastos pagados por anticipado (seguros, arriendos) amortizados.
- [ ] Ingresos facturados contra ingresos causados.

### 3. Documentos electrónicos

- [ ] **Facturación electrónica:** todas las ventas del mes facturadas y validadas por la DIAN; notas crédito por devoluciones.
- [ ] **RADIAN:** eventos de acuse de recibo y aceptación de las facturas de compra que se usarán como título valor o que el proveedor necesita para negociarlas.
- [ ] **Documento soporte** de pagos a no obligados a facturar.
- [ ] **Nómina electrónica** del mes transmitida a la DIAN dentro del plazo (requisito para que los pagos laborales sean deducibles).
- [ ] **PILA** pagada y conciliada con la nómina.

### 4. Obligaciones tributarias del período

| Obligación | Formulario | Periodicidad | Qué verifica el motor |
| --- | --- | --- | --- |
| Retención en la fuente y autorretención especial de renta | 350 | Mensual | Cada retención por concepto y la autorretención por CIIU |
| IVA | 300 | Bimestral o cuatrimestral (art. 600 E.T.) | Generado, descontable, retenido y saldo |
| ReteIVA | Dentro del 350 | Mensual | 15 % del IVA, o 100 % en los casos especiales |
| ReteICA | Según la ciudad | Mensual o bimestral según el municipio | La tarifa y la base mínima de cada ciudad cubierta |

Para cada una, tome una muestra de pagos del mes (los más grandes y los de conceptos dudosos) y verifíquela en el motor. Si la retención registrada no coincide, explique la diferencia por su causa: concepto, base mínima, tarifa o sujeto.

## Cálculo (motor fiscal)

### Retención en la fuente de un pago

Endpoint: `POST /v1/retenciones/retefuente`. Campos: `concepto` (por ejemplo `honorarios`, `servicios`, `compras`, `arrendamiento_inmuebles`), `base`, `sujeto` (`tipo`: `persona_natural` o `persona_juridica`; `declarante`; `residente`), `fecha` del pago.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/retenciones/retefuente" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"concepto":"honorarios","base":8000000,"sujeto":{"tipo":"persona_natural","declarante":true},"fecha":"2026-10-15"}'
```

### ReteICA de un pago

Endpoint: `POST /v1/retenciones/reteica`. Campos: `municipio`, `actividad` (código de la ciudad), `base`, `fecha`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/retenciones/reteica" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"municipio":"barranquilla","actividad":"304","base":5000000,"fecha":"2026-10-15"}'
```

### ReteIVA y autorretención

`POST /v1/retenciones/reteiva` con `iva_facturado` y `sujeto`. `POST /v1/retenciones/autorretencion` con `ciiu` y `base` (ingresos del mes).

### IVA del período

Endpoint: `POST /v1/iva/liquidar`. Campos: `periodo` (`tipo`: `bimestre` o `cuatrimestre`, `numero`, `anio`), `ventas_gravadas_19`, `ventas_gravadas_5`, `ventas_excluidas`, `ventas_exentas`, `compras_descontables_19`, `compras_descontables_5`, `iva_retenido`, `saldo_favor_anterior`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/iva/liquidar" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"periodo":{"tipo":"bimestre","numero":5,"anio":2026},"ventas_gravadas_19":120000000,"compras_descontables_19":70000000,"iva_retenido":1500000}'
```

Reporte cada cifra como la entregó el motor, con `base_legal`, `version_tablas` y `vigencia`.

## Entregable

1. **Lista de cierre** con cada punto en hecho, pendiente o no aplica, y quién lo resuelve.
2. **Muestra de retenciones verificadas:** pago, concepto, retención registrada, retención del motor y diferencia explicada.
3. **Borradores de las declaraciones del mes** (350, 300 si corresponde, reteICA) con las cifras del motor.
4. **Vencimientos** del mes siguiente según el calendario que entregue el contador.

## Límites

- No genera los formularios oficiales ni los presenta.
- ReteICA solo en las ciudades que el motor cubre; las demás se marcan «sin tabla».
- No liquida nómina ni aportes PILA (pendiente en el motor).
