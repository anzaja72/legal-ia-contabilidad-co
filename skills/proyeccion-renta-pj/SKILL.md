---
name: proyeccion-renta-pj
description: Úsela cuando un contador quiera proyectar el impuesto de renta del año de una sociedad a partir de su balance de prueba (por ejemplo, a junio o a septiembre) y entregarle al cliente la carta con la depuración, el saldo a pagar y el anticipo. Resume el balance por grupos PUC, proyecta a diciembre, depura los no deducibles y liquida el formulario 110 con el motor fiscal.
version: 1.0.0
author: Legal-IA
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - GET /v1/versiones
    - POST /v1/retenciones/autorretencion
    - POST /v1/renta-pj/calcular
---

> Las cifras de impuesto, tasa mínima, anticipo y saldo salen solo del motor fiscal. El script de esta skill suma cuentas y proyecta saldos contables; no calcula impuestos. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Proyección del impuesto de renta de una sociedad (formulario 110)

Una proyección le dice al cliente, antes de cerrar el año, cuánto impuesto va a causar, cuánto le cubren las retenciones y autorretenciones y cuánto le falta pagar. Sirve para planear caja y para corregir a tiempo los gastos que no van a ser deducibles.

## Cuándo usarla

- El contador tiene el balance de prueba de un corte del año (junio, septiembre, octubre) y quiere estimar el cierre.
- El cliente pregunta «¿cuánto voy a pagar de renta?» antes de diciembre.
- Hay que revisar una proyección hecha por otra persona (cuadre, doble conteo, anticipo).

No la use para personas naturales (formulario 210: `planeacion-tributaria-persona-natural`), para el régimen SIMPLE (`elegir-regimen-simple-u-ordinario`) ni para regímenes que el motor no liquida (zonas francas, régimen tributario especial, hoteleros): `GET /v1/renta-pj/regimenes` los lista.

## Reglas que no se negocian

1. **El balance manda.** Los totales salen del archivo, no de la memoria ni de un estimado. Si una cuenta no cuadra, se dice.
2. **Una partida se suma una sola vez.** Lo que ya está en el saldo a la fecha no se vuelve a sumar como «proyectado». Lo proyectado cubre solo los meses que faltan.
3. **Ausente no es cero.** Si falta la cuenta de autorretenciones, el impuesto del año anterior o la tasa del interés presunto, se pide o se marca como faltante; no se asume cero.
4. **El motor calcula.** El impuesto, la tasa mínima, el anticipo y el saldo los da `POST /v1/renta-pj/calcular`. No multiplique tarifas en el chat.
5. **Es un documento de trabajo.** La responsabilidad es del contador que firma; la carta lo dice.

## Datos que hay que tener

| Dato | De dónde sale | Si falta |
| --- | --- | --- |
| Balance de prueba con cuenta, nombre y saldo | Archivo del cliente (Excel o CSV) | No hay proyección |
| Mes de corte del balance | Encabezado del balance | Preguntar |
| CIIU de la actividad principal | RUT del cliente | Preguntar; sin él no hay autorretención |
| Impuesto neto de renta del año anterior (casilla 96 del 110) | Declaración del año anterior | El anticipo solo usa la opción del año actual; decirlo |
| Años que lleva declarando (1, 2, 3 o más) | Fecha de constitución | Preguntar; cambia el porcentaje del anticipo |
| Estacionalidad (por ejemplo, diciembre 30 % más alto) | El contador | Proyectar lineal y decirlo como supuesto |
| Tasa del interés presunto del año (art. 35 E.T.) si hay cuentas por cobrar a socios | Norma del año | Pedirla. El motor no la tiene; no se estima |
| Pérdidas fiscales por compensar, descuentos tributarios, rentas exentas | Contador | Cero solo si el contador lo confirma |

## Procedimiento

### 1. Resumir el balance

Ejecute el script `scripts/resumir_balance.py` de la carpeta de esta skill sobre el archivo del cliente. Indique la hoja y las columnas de cuenta, nombre y saldo actual (letra o encabezado):

```bash
uv run --with openpyxl python scripts/resumir_balance.py "BALANCE.xlsx" \
  --hoja "BP Sep" --col-cuenta B --col-nombre D --col-saldo H --mes-corte 9 \
  --alza-diciembre-ingresos 0.3 --alza-diciembre-costos 0.3
```

Lea del JSON: los saldos a la fecha por grupo PUC (41, 42, 51, 52, 53, 54, 59, 6, 7), la proyección a diciembre, las retenciones (135515) y autorretenciones (135519) acumuladas, las cuentas por cobrar a socios (1325) y la lista `cuentas_a_revisar_no_deducibles`.

Control: la utilidad del balance (clase 4 menos clases 5, 6 y 7) debe coincidir con la del estado de resultados del cliente. Si no coincide, deténgase y pregunte.

### 2. Confirmar los supuestos de proyección

Muestre al contador, en una tabla, el saldo a la fecha, el proyectado y el total del año de ingresos, costos y gastos. Diga qué supuesto se usó (lineal o con alza de diciembre) y pídale que lo confirme antes de seguir.

### 3. Depurar los no deducibles

Revise con el contador la lista del script y agregue lo que él conozca. Las partidas típicas:

- Impuesto de renta registrado como gasto (grupo 54): siempre se suma.
- GMF: solo es deducible el 50 % certificado (art. 115 E.T.).
- Multas, sanciones e intereses de mora.
- Costos y gastos de ejercicios anteriores.
- Gastos sin factura electrónica o documento soporte, pagos en efectivo por encima del límite del art. 771-5, contratistas sin soporte de seguridad social.

Para cada partida separe lo causado a la fecha y lo proyectado de los meses que faltan. **Revise el doble conteo** antes de liquidar:

- Una fila de «no deducibles proyectados» no puede ser la suma de las mismas partidas a la fecha.
- El impuesto de renta (cuentas 54 y, si la usan, 59) entra una sola vez: si ya está dentro de «otros no deducibles», no va también en su propia fila.
- Cada cuenta de `cuentas_a_revisar_no_deducibles` queda incluida o descartada con su motivo; ninguna en cero sin decirlo (por ejemplo, gastos de ejercicios anteriores con saldo en el balance).

### 4. Interés presunto por préstamos a socios

Si la cuenta 1325 tiene saldo, el art. 35 E.T. presume un ingreso por intereses. Pida la tasa del año y el detalle de saldos promedio. Ese valor entra como ingreso financiero. Si el contador ya lo calculó, use su cifra y cítela.

### 5. Autorretención y retenciones

- Autorretención especial de renta: llame `POST /v1/retenciones/autorretencion` con el CIIU y, como base, los ingresos proyectados de los meses que faltan. Súmele lo acumulado en la 135519.
- Retenciones que le practicaron: use la proyección de la 135515 que entrega el script.

### 6. Liquidar el formulario 110

Arme el cuerpo de `POST /v1/renta-pj/calcular` con la tabla de la sección siguiente y llame al motor. Antes, consulte `GET /v1/versiones`: si la vigencia del año proyectado no está publicada, use la vigente y dígalo en la carta (la tarifa general del 35 %, la tasa mínima y el anticipo se liquidan con las mismas reglas).

### 7. Revisar y entregar

Compare el resultado con la proyección del cliente si existe. Explique cada diferencia por su causa (doble conteo, supuesto distinto, partida omitida). Arme la carta con `referencia/plantilla-carta.md`.

## Cálculo (motor fiscal)

### Autorretención del CIIU

Endpoint: `POST /v1/retenciones/autorretencion`. Campos: `ciiu`, `base`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/retenciones/autorretencion" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"ciiu":"5630","base":900000000}'
```

Reporte `tarifa_aplicada`, `retencion` y `base_legal`.

### Formulario 110

Endpoint: `POST /v1/renta-pj/calcular`.

| Campo del motor | Qué va |
| --- | --- |
| `ingresos.actividades_ordinarias` | Total del año del grupo 41 |
| `ingresos.otros` | Total del año del grupo 42 |
| `ingresos.financieros` | Interés presunto del art. 35 (y rendimientos si el contador los separa) |
| `costos_y_gastos.costos` | Total del año de las clases 6 y 7 |
| `costos_y_gastos.gastos_administracion` | Total del año del grupo 51 |
| `costos_y_gastos.gastos_distribucion_ventas` | Total del año del grupo 52 |
| `costos_y_gastos.otros_gastos_deducciones` | Grupo 53 más el impuesto de renta (54), menos todos los no deducibles del paso 3 |
| `tasa_minima.utilidad_contable` | Utilidad antes del impuesto de renta |
| `tasa_minima.diferencias_permanentes` | No deducibles del paso 3 sin el impuesto de renta |
| `anios_declarando`, `impuesto_neto_anio_anterior` | Datos del cliente |
| `autorretenciones`, `otras_retenciones` | Paso 5 |
| `compensaciones`, `renta_exenta`, `descuentos_tributarios` | Solo si el contador los da |

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/renta-pj/calcular" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"regimen":"general","ingresos":{"actividades_ordinarias":4000000000,"otros":10000000,"financieros":8000000},"costos_y_gastos":{"costos":1200000000,"gastos_administracion":900000000,"gastos_distribucion_ventas":1500000000,"otros_gastos_deducciones":40000000},"tasa_minima":{"utilidad_contable":420000000,"diferencias_permanentes":60000000},"anios_declarando":3,"impuesto_neto_anio_anterior":120000000,"autorretenciones":44000000,"otras_retenciones":50000000}'
```

Reporte, sin alterar: `casilla_75_renta_liquida`, `casilla_84_impuesto_renta_liquida_gravable`, `tasa_minima` (`tasa_tributacion_depurada`, `impuesto_a_adicionar`), `casilla_99_total_impuesto_a_cargo`, `casilla_107_total_retenciones`, `casilla_108_anticipo_anio_siguiente`, `casilla_113_total_saldo_a_pagar` o `casilla_114_total_saldo_a_favor`, las `advertencias`, `version_tablas` y `vigencia`.

## Entregable

1. **Tablero de la proyección** (HTML de una sola página): saldo a pagar, impuesto, retenciones y anticipo; depuración del 110 con sus casillas; escenarios a escala; no deducibles con su norma; supuestos y hallazgos.
2. **Carta al cliente** con la plantilla: datos generales, depuración, saldo a pagar, anticipo y recomendaciones.
3. **Supuestos** en una lista: corte, estacionalidad, no deducibles incluidos, tasa del interés presunto, vigencia usada.
4. **Hallazgos**: diferencias con proyecciones previas y su causa; partidas que el contador debe soportar antes de diciembre.
5. **Cierre**: `version_tablas`, `vigencia` y que la proyección puede cambiar con el cierre real.

### Cómo se arma el tablero

Guarde en un JSON los datos de la empresa, la proyección contable, los no deducibles, los supuestos, los hallazgos y, por cada escenario, la respuesta completa de `POST /v1/renta-pj/calcular` (el formato está al inicio de `scripts/tablero.py`). Luego ejecute el script de la carpeta de esta skill:

```bash
python scripts/tablero.py proyeccion.json --salida tablero-proyeccion.html
```

El script solo presenta: toma las casillas que devolvió el motor y no calcula nada. Ábralo en el navegador o entréguelo como archivo.

**Publicarlo como artefacto.** Si la sesión tiene la herramienta de artefactos de Claude, genere el contenido con `--artefacto` y publíquelo como página. Los datos de un cliente son sensibles: **pregunte antes de publicar** y, si el usuario no lo autoriza, deje solo el archivo local. Un tablero con datos ficticios se puede publicar sin preguntar.

## Límites

- No hace la conciliación fiscal completa (formato 2516) ni decide qué gasto es deducible: propone y el contador confirma.
- No calcula la tasa del interés presunto ni el impuesto diferido.
- No liquida ICA: para eso use `ica-liquidar-declaracion` con los ingresos por municipio.
- Mientras la vigencia del año proyectado no esté publicada en el motor, la liquidación usa la última vigente.
