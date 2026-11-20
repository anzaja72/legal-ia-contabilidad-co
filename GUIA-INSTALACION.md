# Guía de instalación y primera prueba

Para contadores que van a probar el plugin `contabilidad-co`. Toma unos 15 minutos.

## 1. Lo que necesita

- **Claude Code**, en la app de escritorio de Claude (pestaña Code) o en la terminal. Con un plan Pro o superior de Claude.
- **Un token del motor fiscal.** Legal-IA se lo activa: regístrese en [cuenta.legal-ia.co](https://cuenta.legal-ia.co), avise a Legal-IA para que active su acceso de prueba y luego pulse «Generar token». El token se muestra una sola vez: cópielo y guárdelo.
- **`uv`**, para que la skill lea el balance de prueba en Excel. Si no lo tiene, en la terminal:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Guardar el token

En macOS o Linux, agregue esta línea al final de su archivo `~/.zshrc` (o `~/.bashrc`) con su token, y abra una terminal nueva:

```bash
export MOTOR_FISCAL_TOKEN="pegue-aqui-su-token"
```

En Windows, cree la variable de entorno de usuario `MOTOR_FISCAL_TOKEN` desde *Configuración → Sistema → Acerca de → Configuración avanzada del sistema → Variables de entorno*.

No comparta el token ni lo pegue en un chat.

## 3. Instalar el plugin

En la terminal:

```bash
claude plugin marketplace add anzaja72/legal-ia-contabilidad-co
```

```bash
claude plugin install contabilidad-co@legal-ia
```

Reinicie Claude Code. Para comprobar la conexión con el motor:

```bash
claude mcp list
```

Debe aparecer `motor-fiscal` como **Connected**.

## 4. Primera prueba: proyección de renta

1. Abra una sesión de Claude Code en la carpeta donde tiene el balance de prueba del cliente (Excel o CSV, con columnas de cuenta, nombre y saldo).
2. Escriba algo como:

   > Proyecta la renta 2026 de esta sociedad con el balance a septiembre `Balance septiembre.xlsx`. CIIU 5630, lleva más de tres años declarando y el impuesto neto de renta del año pasado fue de 245 millones.

3. Claude le va a:
   - resumir el balance por grupos PUC y mostrarle la proyección a diciembre para que la confirme;
   - pedirle que revise la lista de posibles gastos no deducibles;
   - pedirle la tasa del interés presunto si hay préstamos a socios;
   - liquidar el formulario 110 en el motor;
   - entregarle el tablero en HTML y el borrador de la carta.

El tablero se guarda como archivo en su computador. Claude solo lo publica en claude.ai si usted lo autoriza.

## 5. Qué esperar y cómo reportar

- Mientras el año gravable 2026 no esté publicado en el motor, la liquidación usa las tablas del 2025 (la tarifa general del 35 %, la tasa mínima y el anticipo tienen las mismas reglas). El tablero lo dice.
- Si una cifra no le cuadra, anote el caso (sin datos del cliente) y envíelo a Legal-IA.
- Si `motor-fiscal` no aparece conectado, revise que la variable `MOTOR_FISCAL_TOKEN` esté en una terminal nueva.
