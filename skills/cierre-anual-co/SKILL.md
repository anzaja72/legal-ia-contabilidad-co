---
name: cierre-anual-co
description: Úsela cuando un contador en Colombia vaya a cerrar el año de una sociedad. Ordena los ajustes de fin de año, la provisión del impuesto de renta, el ICA anual, los certificados de retención, la información exógena y las obligaciones societarias de los primeros meses (asamblea, reserva legal, matrícula mercantil), con las cifras tributarias liquidadas por el motor fiscal.
version: 1.0.0
author: Legal-IA
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - POST /v1/renta-pj/calcular
    - POST /v1/ica/liquidar
    - POST /v1/retenciones/certificado
---

> La provisión de renta, el ICA anual y el consolidado de retenciones los calcula el motor. La skill ordena el cierre, pide los datos y explica. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Cierre anual contable, tributario y societario

El cierre del año es el cierre de diciembre más todo lo que solo ocurre una vez al año: ajustes de fin de ejercicio, impuesto de renta, ICA anual, certificados, exógena y las decisiones de los socios. Esta skill lo organiza en cinco bloques con su orden lógico, porque cada uno depende del anterior.

## Cuándo usarla

- Entre diciembre y marzo, para cerrar el año y preparar lo que vence en el primer semestre.
- Para revisar si a un cliente le falta alguna obligación anual.

Primero cierre diciembre con `cierre-mensual-co`. Para depurar los gastos no deducibles use `depuracion-gastos-no-deducibles`; para la conciliación entre NIIF y lo fiscal, `conciliacion-fiscal`; para los estados financieros, `estados-financieros-niif-pymes`.

## Reglas que no se negocian

1. **El orden importa.** No se provisiona renta sobre una contabilidad sin ajustes de cierre, ni se reparten utilidades antes de aprobar los estados financieros.
2. **Las fechas salen del calendario oficial** del año (decreto nacional y resoluciones municipales). Si no lo tiene, dígalo y no suponga vencimientos.
3. **El motor calcula; el contador decide** los criterios contables (vidas útiles, deterioro, provisiones).

## Bloque 1. Ajustes contables de fin de año

- [ ] Toma física de inventarios y ajuste contra el kárdex.
- [ ] Depreciación y amortización del año completas; revisión de vidas útiles.
- [ ] Deterioro de cartera (contable) y su tratamiento fiscal (art. 145 E.T.) por separado.
- [ ] Diferencia en cambio de saldos en moneda extranjera a la TRM del 31 de diciembre. Fiscalmente solo se reconoce al realizarse (art. 288 E.T.).
- [ ] Provisiones y pasivos estimados: prestaciones sociales consolidadas, litigios, garantías.
- [ ] Ingresos y gastos diferidos: lo que corresponde al año siguiente sale de resultados.
- [ ] Conciliación de impuestos por pagar y a favor contra las declaraciones presentadas en el año.

## Bloque 2. Impuesto de renta del año

- [ ] Depure los gastos no deducibles (`depuracion-gastos-no-deducibles`).
- [ ] Liquide la provisión del impuesto de renta en el motor (`POST /v1/renta-pj/calcular`), con la tasa mínima y el anticipo del año siguiente.
- [ ] Registre la provisión y, si aplica, el impuesto diferido (NIIF para Pymes, sección 29).
- [ ] Prepare el formato 2516 de conciliación fiscal si la sociedad está obligada (`conciliacion-fiscal`).

## Bloque 3. Impuestos territoriales y certificados

- [ ] **ICA anual** de cada municipio donde la sociedad declara anualmente, con sus retenciones y autorretenciones del año (`POST /v1/ica/liquidar`).
- [ ] **Certificados de retención** que la sociedad debe expedir: ingresos y retenciones laborales (formulario 220) y certificados por otros conceptos, en los plazos del art. 381 E.T. El consolidado por concepto lo arma el motor (`POST /v1/retenciones/certificado`).
- [ ] **Certificados que debe recibir:** retenciones que le practicaron, para soportar la casilla de retenciones del formulario 110.

## Bloque 4. Información y reportes a la DIAN y a otras entidades

- [ ] **Información exógena** (art. 631 E.T.) según la resolución anual de la DIAN y sus plazos.
- [ ] **Declaración de activos en el exterior** (art. 607 E.T.) si los tiene por encima del tope legal.
- [ ] **Registro Único de Beneficiarios Finales (RUB)**: actualizar si hubo cambios en socios o beneficiarios.
- [ ] **RUT** actualizado: responsabilidades, actividades económicas y establecimientos.
- [ ] Reportes a la Superintendencia de Sociedades si la sociedad está obligada.

## Bloque 5. Obligaciones societarias (primer trimestre)

- [ ] **Renovación de la matrícula mercantil** en la cámara de comercio dentro de los tres primeros meses del año (art. 33 del Código de Comercio).
- [ ] **Asamblea o junta ordinaria** dentro de los tres meses siguientes al cierre (art. 422 del Código de Comercio), salvo que los estatutos digan otra cosa: aprueba los estados financieros y el informe de gestión.
- [ ] **Reserva legal:** el 10 % de las utilidades líquidas hasta llegar al 50 % del capital suscrito (art. 452 del Código de Comercio), si aplica al tipo de sociedad y a sus estatutos.
- [ ] **Distribución de utilidades:** acta, retención en la fuente sobre dividendos al pagarlos o abonarlos en cuenta, y certificado a los socios.

## Cálculo (motor fiscal)

### Provisión del impuesto de renta

Endpoint: `POST /v1/renta-pj/calcular`. Use los campos y la tabla de `proyeccion-renta-pj`, con las cifras reales del año y no proyectadas.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/renta-pj/calcular" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"regimen":"general","ingresos":{"actividades_ordinarias":3000000000},"costos_y_gastos":{"costos":1400000000,"gastos_administracion":700000000,"gastos_distribucion_ventas":500000000},"tasa_minima":{"utilidad_contable":420000000,"diferencias_permanentes":30000000},"anios_declarando":3,"impuesto_neto_anio_anterior":110000000,"autorretenciones":33000000,"otras_retenciones":40000000}'
```

Reporte `casilla_99_total_impuesto_a_cargo` (provisión), `casilla_108_anticipo_anio_siguiente`, `casilla_113_total_saldo_a_pagar` o `casilla_114_total_saldo_a_favor`, `tasa_minima`, `version_tablas` y `vigencia`.

### ICA anual por municipio

Endpoint: `POST /v1/ica/liquidar`. Campos: `municipio`, `periodicidad` (`anual`), `ingresos_brutos`, `actividades` (`codigo` de la ciudad e `ingresos`), `deducciones` (`concepto`, `valor`), `retenciones`, `autorretenciones`, `fecha`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/ica/liquidar" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"municipio":"barranquilla","periodicidad":"anual","ingresos_brutos":1200000000,"actividades":[{"codigo":"304","ingresos":1200000000}],"deducciones":[],"fecha":"2026-12-31"}'
```

### Consolidado de retenciones para certificados

Endpoint: `POST /v1/retenciones/certificado`. Campos: `anio` y `practicas`, cada una con `tipo` (`retefuente`, `reteiva`, `reteica` o `autorretencion`), `concepto`, `base` y `retencion` ya practicadas.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/retenciones/certificado" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"anio":2026,"practicas":[{"tipo":"retefuente","concepto":"honorarios","base":96000000,"retencion":9600000}]}'
```

Cite cada cifra con `version_tablas`, `vigencia` y la norma que devuelva el motor.

## Entregable

1. **Lista de cierre anual** por bloque, con estado (hecho, pendiente, no aplica), responsable y fecha límite según el calendario que entregue el contador.
2. **Provisión de renta y anticipo** del motor, con la depuración que la sustenta.
3. **ICA anual** por municipio y **consolidado de certificados** de retención.
4. **Agenda del primer trimestre:** matrícula, asamblea, reserva legal, distribución de utilidades, exógena y renta.

## Límites

- No elabora los estados financieros ni sus notas (`estados-financieros-niif-pymes`) ni el formato 2516 (`conciliacion-fiscal`).
- No liquida dividendos de socios ni el impuesto al patrimonio de personas naturales.
- ICA solo en las ciudades que cubre el motor.
- La renta del año gravable 2026 se liquida con las tablas de 2025 mientras el motor no publique la vigencia 2026; dígalo en el entregable.
