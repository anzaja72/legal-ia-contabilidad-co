---
name: conciliacion-fiscal
description: Úsela cuando un contador necesite conciliar la contabilidad bajo NIIF con las cifras fiscales de una sociedad (art. 772-1 E.T. y Decreto 1998 de 2017). Clasifica las diferencias entre lo contable y lo fiscal en permanentes y temporarias, arma el puente de la utilidad contable a la renta líquida, identifica la base del impuesto diferido y deja la información lista para el formato 2516, con la renta liquidada por el motor fiscal.
version: 1.0.0
author: Legal-IA
metadata:
  motor_fiscal:
    cobertura: parcial
    endpoints:
    - POST /v1/renta-pj/calcular
---

> La renta líquida, el impuesto y la tasa mínima salen del motor. El impuesto diferido no lo calcula el motor: la skill entrega la tabla de diferencias y, si hace una multiplicación, la muestra como cálculo propio y no del motor. La convención de llamada está en `skills/_shared/motor-fiscal-cliente.md`.

# Conciliación fiscal

La contabilidad se lleva bajo NIIF, pero el impuesto de renta se liquida con las reglas del Estatuto Tributario. La conciliación fiscal explica, partida por partida, por qué la utilidad contable y la renta líquida son distintas. Es obligatoria para quienes llevan contabilidad (art. 772-1 E.T.); la DIAN la pide en el formato 2516 a las sociedades de mayores ingresos y las demás la conservan como control de detalle.

## Cuándo usarla

- Al cierre del año, antes de declarar renta.
- Para preparar el formato 2516 o el control de detalle.
- Para calcular la base del impuesto diferido.

## Reglas que no se negocian

1. **Cada diferencia lleva su norma** (artículo del E.T.) y su naturaleza: permanente o temporaria.
2. **El puente cuadra.** Utilidad contable más diferencias igual a renta líquida del motor. Si no cuadra, se dice cuánto falta y no se fuerza.
3. **La obligación del formato 2516 la confirma el contador** con el tope de ingresos y la resolución vigente de la DIAN. La skill no la supone.

## Diferencias típicas

| Partida | Contable (NIIF) | Fiscal | Tipo | Norma |
| --- | --- | --- | --- | --- |
| Impuesto de renta del año | Gasto | No deducible | Permanente | Art. 115 E.T. |
| Multas, sanciones, intereses de mora | Gasto | No deducibles | Permanente | Art. 105 E.T.; art. 11 Ley 1430 de 2010 |
| GMF | Gasto 100 % | Deducible 50 % | Permanente | Art. 115 E.T. |
| Atenciones por encima del 1 % | Gasto | Exceso no deducible | Permanente | Art. 107-1 E.T. |
| Depreciación | Vida útil contable | Límites de tasas fiscales | Temporaria | Art. 137 E.T. |
| Deterioro de cartera | Pérdida esperada (NIIF) | Métodos fiscales | Temporaria | Art. 145 E.T. |
| Diferencia en cambio no realizada | Ingreso o gasto | Se reconoce al realizarse | Temporaria | Art. 288 E.T. |
| Provisiones y pasivos estimados | Gasto al estimarse | Deducible al pagarse o causarse fiscalmente | Temporaria | Arts. 59 y 105 E.T. |
| Mediciones a valor razonable | Ingreso o gasto | No se reconocen hasta la enajenación | Temporaria | Art. 28 y 59 E.T. |
| Ingresos por método de participación | Ingreso | No constitutivo en la medida de la ley | Permanente | Art. 28 E.T. |

Las permanentes no se revierten y no generan impuesto diferido. Las temporarias se revierten en años futuros y son la base del impuesto diferido (NIIF para Pymes, sección 29).

## Procedimiento

1. **Datos.** Estado de resultados y estado de situación financiera bajo NIIF, balance de prueba y el detalle de las partidas con tratamiento distinto.
2. **Clasifique** cada diferencia con la tabla: permanente o temporaria, con su norma.
3. **Arme el puente** de la utilidad contable antes de impuestos a la renta líquida.
4. **Liquide en el motor** con las cifras fiscales y compare su `casilla_72_renta_liquida_ordinaria` con el puente.
5. **Impuesto diferido:** liste las diferencias temporarias por partida (activo o pasivo) y su saldo. El valor del impuesto diferido no lo da el motor; si lo calcula, muestre la operación y márquela como cálculo propio para que el contador la revise.
6. **Formato 2516:** organice las cifras por las secciones del formato (patrimonio, renta líquida, impuesto diferido, ingresos y facturación, activos fijos y resumen) para transcribirlas en el prevalidador de la DIAN.

## Cálculo (motor fiscal)

Endpoint: `POST /v1/renta-pj/calcular`. Las cifras van fiscales (ya depuradas). En `tasa_minima.utilidad_contable` va la utilidad contable antes de impuestos y en `tasa_minima.diferencias_permanentes` las permanentes que aumentan la renta.

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/renta-pj/calcular" \
  -H "content-type: application/json" -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{"regimen":"general","ingresos":{"actividades_ordinarias":3000000000},"costos_y_gastos":{"costos":1400000000,"gastos_administracion":680000000,"gastos_distribucion_ventas":500000000},"tasa_minima":{"utilidad_contable":380000000,"diferencias_permanentes":40000000},"anios_declarando":3}'
```

Reporte `casilla_72_renta_liquida_ordinaria`, `casilla_79_renta_liquida_gravable`, `casilla_99_total_impuesto_a_cargo`, `tasa_minima` (`utilidad_depurada`, `tasa_tributacion_depurada`, `impuesto_a_adicionar`), `version_tablas` y `vigencia`.

## Entregable

1. **Puente** de la utilidad contable a la renta líquida, partida por partida, con su norma y naturaleza.
2. **Cuadre** contra la renta líquida del motor, y la diferencia si la hay.
3. **Tabla de diferencias temporarias** para el impuesto diferido, con el cálculo marcado como propio si lo hubo.
4. **Cifras ordenadas por sección del formato 2516**, o el control de detalle si la sociedad no está obligada.

## Límites

- No genera el archivo del formato 2516 ni usa el prevalidador de la DIAN.
- No calcula el impuesto diferido en el motor.
- La clasificación de cada partida la confirma el contador; ante la duda, se marca «revisar».
