---
name: elegir-regimen-simple-u-ordinario
description: Úsela cuando un empresario (persona natural o sociedad) pregunte si le
  conviene más el Régimen SIMPLE o el régimen ordinario de renta. Compara los dos
  con sus cifras reales, liquidadas por el motor fiscal, y dice cuál paga menos y por qué.
version: 1.0.0
author: Alfred - MC Consultorías
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - POST /v1/simple/calcular
    - GET /v1/simple/tarifas
    - POST /v1/renta-pj/calcular
    - POST /v1/renta/calcular
    - POST /v1/ica/liquidar
    - GET /v1/ica/ciudades
---

> Las cifras de esta skill (impuesto de cada régimen, ICA, saldo) salen solo del motor fiscal. No multiplique tarifas ni estime un impuesto a mano. Lo único que se hace fuera del motor es sumar o restar cifras que el motor ya devolvió, mostrando los sumandos. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Elegir entre el Régimen SIMPLE y el régimen ordinario

El SIMPLE cobra un porcentaje sobre los **ingresos brutos** y ya incluye el ICA. El ordinario cobra sobre la **utilidad** y el ICA se paga aparte. Por eso no gana siempre el mismo: depende sobre todo del margen del negocio. Esta skill liquida los dos regímenes con los números del empresario y los compara en igualdad de condiciones.

## Cuándo usarla

- El empresario pregunta si se pasa al SIMPLE o si se queda en el ordinario.
- Está en el SIMPLE y quiere saber si le conviene salir.
- Va a crear empresa y quiere elegir régimen con una proyección.

No la use si el contribuyente no puede estar en el SIMPLE (paso 1): en ese caso solo hay ordinario y no hay nada que comparar.

## Paso 1. ¿Puede estar en el SIMPLE?

El motor no valida estos requisitos. Pregúntelos antes de calcular. Si alguno falla, diga que solo aplica el régimen ordinario y cite la norma.

**Condiciones (E.T. art. 905):**

- Es persona natural que desarrolla empresa, o sociedad cuyos socios son todos personas naturales residentes en Colombia.
- Ingresos brutos del año anterior inferiores a 100.000 UVT. Si es empresa nueva, que los del año no los superen.
- Si un socio participa en otras empresas, los ingresos se revisan consolidados.
- Tiene RUT, firma electrónica y factura electrónica.

**No pueden optar (E.T. art. 906), entre otros:**

- Sociedades extranjeras, no residentes, filiales o sucursales.
- Sociedades que sean socias de otras sociedades.
- Entidades financieras.
- Personas cuya actividad configure una relación laboral con quien les paga.
- Quienes se dediquen a microcrédito, factoring, asesoría financiera, gestión o arrendamiento de activos con ingresos pasivos del 20 % o más, energía eléctrica, automóviles, importación de combustibles o armas.
- Sociedades que resulten de una escisión de los últimos cinco años.

## Paso 2. Datos que hacen falta

Use cifras reales del año, o la proyección que el empresario respalde. Liste aparte lo que no tenga.

| Dato | Para qué |
| --- | --- |
| Ingresos brutos del año, por actividad | Base del SIMPLE y de los dos regímenes |
| Costos y gastos deducibles | Utilidad del ordinario |
| Utilidad contable antes de impuestos | Tasa mínima del ordinario (sociedades) |
| Municipio y actividad de ICA | ICA aparte en el ordinario; tarifa consolidada en el SIMPLE |
| Ingresos por comidas y bebidas | Impuesto al consumo en el SIMPLE |
| Aportes a pensión pagados como empleador | Descuento en el SIMPLE |
| Ventas cobradas con tarjeta o pagos electrónicos | Descuento del 0,5 % en el SIMPLE |
| Retenciones que le practican en el año | Efecto en la caja |
| Persona natural: salarios, aportes, dependientes y demás datos del formulario 210 | Ordinario de persona natural |

## Paso 3. Liquide los dos regímenes

1. **SIMPLE:** una llamada a `simple/calcular` con período anual.
2. **Ordinario de sociedad:** `renta-pj/calcular`. **Ordinario de persona natural:** `renta/calcular`.
3. **ICA del ordinario:** `ica/liquidar` si la ciudad está en `ica/ciudades`. Si no está, use el ICA que el empresario declaró y dígalo; si tampoco lo tiene, la comparación queda incompleta.

## Paso 4. Compare en igualdad de condiciones

Arme esta tabla solo con cifras del motor:

| Concepto | Ordinario | SIMPLE |
| --- | --- | --- |
| Impuesto de renta | `casilla_99_total_impuesto_a_cargo` (sociedad) o `casilla_129_total_impuesto_cargo` (persona natural) | Incluido en `impuesto_simple` |
| ICA, avisos y bomberil | Cargo de `ica/liquidar`: `impuesto_ica`, `avisos_tableros` y `sobretasa_bomberil` | `componente_ica_consolidado`, ya incluido |
| Impuesto al consumo | Fuera del motor en el ordinario | `impuesto_consumo` |
| Descuentos | Los de la casilla 93 | `total_descuentos` |
| **Carga total** | Renta más ICA | `total_a_cargo` |

Reglas de la comparación:

- **Sume el ICA al ordinario.** Sin eso el ordinario parece más barato de lo que es.
- **No compare saldos a pagar.** Los saldos dependen de anticipos y retenciones ya pagados. Compare la carga del año.
- **Si la casilla 95 del ordinario llega en null,** falta la utilidad contable y la comparación no cierra: consígala.
- **Con el ICA pagado en el ordinario,** inclúyalo en `costos_y_gastos`: es deducible (E.T. art. 115).

## Paso 5. Lo que el motor no mide y sí pesa

Dígalo siempre, sin ponerle cifra si no la tiene:

- **Caja durante el año:** al SIMPLE no le practican retención en la fuente ni reteICA (E.T. art. 911). Paga anticipos bimestrales. En el ordinario, las retenciones adelantan impuesto.
- **Pérdidas:** el SIMPLE cobra aunque el negocio pierda, porque grava ingresos. En el ordinario una pérdida no paga renta y se compensa en años siguientes.
- **Tasa mínima del 15 %:** aplica al ordinario de sociedades, no al SIMPLE.
- **IVA:** sigue igual en los dos regímenes.
- **Carga administrativa:** el SIMPLE unifica renta, ICA y consumo en una declaración anual con recibos bimestrales.
- **Dividendos a los socios, beneficios especiales y costos de cambiar de régimen:** no cuantificables con el motor.
- **Plazo:** la inscripción al SIMPLE tiene fecha límite cada año. Verifíquela; el motor no tiene ese calendario.

## Paso 6. Punto de equilibrio

El empresario suele preguntar «¿desde qué margen me conviene?». No lo despeje con una fórmula. Vuelva a llamar el ordinario cambiando solo los costos (por ejemplo, tres márgenes distintos) y muestre cómo cambia la carga frente al SIMPLE, que no se mueve porque no depende de los costos.

Ejemplo con cifras del motor (AG2025, sociedad de comercio, ingresos de $2.000 millones, ICA consolidado de 9 por mil):

| Escenario | Renta ordinaria | SIMPLE (incluye ICA) |
| --- | --- | --- |
| Costos de $1.500 millones (margen alto) | $175.000.000, más el ICA aparte | $90.000.000 |
| Costos de $1.900 millones (margen bajo) | $35.000.000, más el ICA aparte | $90.000.000 |

Lectura: con margen alto gana el SIMPLE; con margen bajo puede ganar el ordinario, según cuánto ICA pague. La respuesta sale de las cifras de cada empresario, no de este ejemplo.

## Cálculo (motor fiscal)

### SIMPLE

Endpoint: `POST /v1/simple/calcular`. Tablas en `GET /v1/simple/tarifas`.

Campos del JSON (nombres reales del modelo): `periodo` (`anual`); `actividades[]` con `grupo` (`tiendas_peluquerias`, `comercio_industria_otros`, `comidas_transporte`, `educacion_salud`, `servicios_profesionales` o `ciiu_4665_3830_3811`) e `ingresos`; `ingresos_comidas_bebidas`; `tarifa_ica_consolidada_por_mil`; `aportes_pension_empleador`; `ingresos_medios_electronicos` o `gmf_pagado` (se excluyen); `ganancia_ocasional_gravable`; `persona_natural`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/simple/calcular" \
  -H "content-type: application/json" \
  -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"periodo":"anual","actividades":[{"grupo":"comercio_industria_otros","ingresos":2000000000}],"tarifa_ica_consolidada_por_mil":9}'
```

Reporte, sin alterar: `grupo_aplicado`, `tarifa_simple`, `impuesto_simple`, `componente_ica_consolidado`, `impuesto_consumo`, `total_descuentos`, `total_a_cargo` y `advertencias`. Si hay descuentos y falta la tarifa de ICA, el motor responde 422: pida la tarifa consolidada del municipio.

### Ordinario de sociedad

Endpoint: `POST /v1/renta-pj/calcular`.

Campos del JSON: `regimen` (`general` salvo que sea financiera, hidroeléctrica o editorial); `ingresos`; `costos_y_gastos`; `renta_exenta`; `descuentos_tributarios`; `tasa_minima.utilidad_contable`; y los demás del formulario 110.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/renta-pj/calcular" \
  -H "content-type: application/json" \
  -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"regimen":"general","ingresos":{"actividades_ordinarias":2000000000},"costos_y_gastos":{"costos":1500000000},"tasa_minima":{"utilidad_contable":500000000}}'
```

Reporte, sin alterar: `casillas.casilla_79_renta_liquida_gravable`, `casilla_95_impuesto_a_adicionar`, `casilla_96_impuesto_neto_con_adicionado`, `casilla_99_total_impuesto_a_cargo`, `estado` y `advertencias`.

### Ordinario de persona natural

Endpoint: `POST /v1/renta/calcular`. El cuerpo es el del formulario 210: `declaracion.datos_generales.nit` y las listas de ingresos, costos y deducciones. En `ingresos_honorarios[]` el monto va en `valor`. Reporte `casillas.casilla_129_total_impuesto_cargo`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/renta/calcular" \
  -H "content-type: application/json" \
  -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"vigencia":"AG2025","declaracion":{"datos_generales":{"nit":"123456789"},"ingresos_honorarios":[{"valor":200000000,"retencion_fuente":20000000}]}}'
```

Este endpoint ignora los campos que no reconoce, sin avisar. Compruebe que los ingresos enviados aparezcan en las casillas de la respuesta antes de comparar; si salen en cero, el nombre del campo está mal.

### ICA del ordinario

Endpoint: `POST /v1/ica/liquidar`. Cobertura por ciudad en `GET /v1/ica/ciudades`.

Campos del JSON: `municipio`, `periodicidad`, `ingresos_brutos`, `actividades[]` con `codigo` e `ingresos`, `deducciones[]` y `fecha`.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/ica/liquidar" \
  -H "content-type: application/json" \
  -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"municipio":"bogota","periodicidad":"anual","ingresos_brutos":2000000000,"actividades":[{"codigo":"servicios_profesion_liberal","ingresos":2000000000}],"ingresos_netos":2000000000}'
```

Reporte, sin alterar: `impuesto_ica`, `avisos_tableros`, `sobretasa_bomberil` y `advertencias`. Un 422 significa que esa ciudad o ese año no tienen tabla: no estime el ICA.

En todas las respuestas cite `version_tablas` y `vigencia`.

## Entregable

1. **Elegibilidad:** si puede estar en el SIMPLE y qué requisito quedó sin confirmar.
2. **Tabla comparativa** del paso 4, con la carga total de cada régimen.
3. **Recomendación:** el régimen de menor carga, y los factores del paso 5 que pueden cambiar la decisión.
4. **Sensibilidad:** la tabla de márgenes del paso 6, si el empresario la pidió.
5. **Información que faltó** y qué quedó sin cuantificar.
6. **Cierre:** `version_tablas`, `vigencia`, las `advertencias` del motor y que la decisión es del empresario con su contador.

## Límites

- Solo el año gravable 2025. Una proyección para 2026 usa tablas de 2025 y hay que decirlo.
- El motor no valida la elegibilidad al SIMPLE ni conoce la tarifa de ICA consolidado de cada municipio: hay que enviarla.
- El ICA del ordinario solo se liquida en 12 ciudades, con completitud desigual.
- El ordinario de sociedades recibe cifras ya depuradas: no decide qué gasto es deducible.
- No cubre regímenes especiales (zonas francas, régimen tributario especial, extractivas).
