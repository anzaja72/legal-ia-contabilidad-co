# Cliente del motor fiscal

Todas las skills cuantitativas llaman al mismo servicio. Esta nota es la convención común. No la sustituya con una cuenta hecha en el chat.

## Variables

- `MOTOR_FISCAL_URL`: origen del servicio, sin barra final. Ejemplo: `https://renta.ejemplo.com`.
- `MOTOR_FISCAL_API_KEY`: la clave del cliente. Viaja solo en el header `X-API-Key`.

La clave puede ser la clave única del servidor o una clave anual emitida para un cliente (`scripts/emitir_api_key.py`). Para la skill es el mismo header.

## Llamada

```bash
curl -fsS -X POST "$MOTOR_FISCAL_URL/v1/..." \
  -H "content-type: application/json" \
  -H "X-API-Key: $MOTOR_FISCAL_API_KEY" \
  -d '{...}'
```

Los nombres de campos son los del modelo Pydantic de esa ruta. Si un campo no está en la skill, no lo invente. `vigencia` omitida usa la vigencia publicada por defecto (hoy AG2025).

## Con el MCP del motor (plugin)

Si la sesión tiene las herramientas MCP del motor (servidor `motor-fiscal` del plugin o `motor-fiscal-local`), úselas en lugar de `curl`. Cada ruta es una herramienta con el mismo cuerpo JSON: `POST /v1/renta-pj/calcular` es `renta_pj_calcular`, `POST /v1/retenciones/autorretencion` es `retenciones_autorretencion`, `GET /v1/versiones` es `versiones`. El nombre sale de la ruta sin `/v1/`, con guiones y barras cambiados por guion bajo. La autenticación ya va en la conexión: no pida la clave.

## Qué se cita

Cada respuesta de cálculo trae `version_tablas` y `vigencia`. Cítelas junto con las cifras, tal como llegaron. No recompute, no redondee al millar ni al peso, no “ajuste” un saldo. El redondeo ya está aplicado (`peso_half_up` en retenciones e IVA; el formulario 210 usa su propio redondeo dentro del motor). El interés moratorio DIAN trae `interes_exacto` en centavos y `interes_a_pagar` al millar (art. 577). Cite los dos. Su `version_tablas` es la de la tabla TIM, no la de AG2025.

## Errores

| Respuesta | Qué significa | Qué hacer |
| --- | --- | --- |
| 401 | API key ausente, inválida o vencida. El detalle no dice cuál de los tres. | No reintente con otra cifra. Diga que no hay acceso y no estime. |
| 422 | Cuerpo inválido, vigencia no publicada, concepto desconocido, municipio sin tabla, o el año no corresponde a la vigencia. El `detail` trae el motivo. | Corrija el JSON si el error es de forma. Si el caso no está publicado, dígalo y no estime. |
| 501 | Hoy el motor no responde 501. Si apareciera, la operación no está cubierta. | No estime. |
| 503 | El proceso no tiene clave configurada. | No estime. Es un fallo de operación, no un cero tributario. |
| Tiempo agotado o conexión rechazada | El motor no contestó. | Diga que está inalcanzable y no estime. |

Un `estado` `faltan_datos` es una respuesta válida con cifras en cero o nulas porque faltó un hecho. No complete ese hueco.

## Privacidad

El servicio calcula y responde. No guarda la declaración, el pago ni el período. La bitácora anota método, ruta, status, latencia y `cliente` (el `cliente_id` de la clave, o `default` si es la clave única). No anota el cuerpo, el NIT, la clave ni el hash.
