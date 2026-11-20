# Contabilidad colombiana para Claude (plugin `contabilidad-co`)

Plugin de Claude Code con skills de contabilidad y tributación colombiana. Las cifras (impuesto, tasa mínima, anticipo, retenciones) las calcula el **motor fiscal de Legal-IA** con su norma citada; las skills ordenan el trabajo y nunca estiman un valor que el motor no dio.

## Skills

| Skill | Para qué |
| --- | --- |
| `proyeccion-renta-pj` | Proyectar la renta de una sociedad (formulario 110) desde el balance de prueba: resumen por PUC, proyección a diciembre, no deducibles, liquidación en el motor, tablero y carta al cliente |
| `planeacion-tributaria-persona-juridica` | Comparar escenarios del formulario 110 y medir la tasa mínima del 15 % |
| `planeacion-tributaria-persona-natural` | Comparar escenarios del formulario 210 (AFC, dependientes, medicina prepagada) |
| `elegir-regimen-simple-u-ordinario` | Decidir con cifras si conviene el SIMPLE o el régimen ordinario |
| `depuracion-gastos-no-deducibles` | Revisar los gastos contra los requisitos del E.T. y medir su efecto en el impuesto |
| `cierre-mensual-co` | Cerrar el mes: conciliaciones, documentos electrónicos, retenciones, IVA y reteICA verificados |
| `cierre-anual-co` | Cerrar el año: ajustes, provisión de renta, ICA anual, certificados, exógena y obligaciones societarias |
| `conciliacion-fiscal` | Puente de la utilidad contable a la renta líquida, impuesto diferido y formato 2516 |
| `flujo-caja-impuestos` | Calendario mes a mes de los pagos de impuestos y costo de pagar tarde |
| `estados-financieros-niif-pymes` | Estados financieros del grupo 2 desde el balance de prueba, con notas y certificaciones |

## Instalación

Ver [GUIA-INSTALACION.md](GUIA-INSTALACION.md). En corto:

```bash
claude plugin marketplace add anzaja72/legal-ia-contabilidad-co
```

```bash
claude plugin install contabilidad-co@legal-ia
```

El plugin necesita un token del motor fiscal en la variable `MOTOR_FISCAL_TOKEN`. El token se obtiene en [cuenta.legal-ia.co](https://cuenta.legal-ia.co).

## Lo que no es

Las salidas son documentos de trabajo para un contador. No son asesoría ni declaraciones presentadas. La responsabilidad profesional es de quien firma.

## Licencia

Ver [LICENSE](LICENSE). El código del motor fiscal no está en este repositorio.
