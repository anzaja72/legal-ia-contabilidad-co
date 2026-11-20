#!/usr/bin/env python3
"""Resume un balance de prueba colombiano (PUC) y proyecta ingresos, costos y gastos a diciembre.

No calcula impuestos: entrega los totales por grupo PUC y la proyección para que la skill
`proyeccion-renta-pj` arme la depuración y la liquide con el motor fiscal.

Uso:
    uv run --with openpyxl python resumir_balance.py BALANCE.xlsx --hoja "BP Sep" \
        --col-cuenta B --col-nombre D --col-saldo H --mes-corte 9 \
        [--alza-diciembre-ingresos 0.3] [--alza-diciembre-costos 0.3] [--alza-diciembre-gastos 0]

También acepta CSV (--col-* por letra de columna o por nombre del encabezado).
La salida es JSON: totales a la fecha de corte, proyección a diciembre y cuentas a revisar.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

# Grupos PUC que usa la depuración. Clase 4 ingresos, 5 gastos, 6 y 7 costos.
GRUPOS = {
    "41": "Ingresos operacionales",
    "42": "Ingresos no operacionales",
    "51": "Gastos operacionales de administración",
    "52": "Gastos operacionales de ventas",
    "53": "Gastos no operacionales",
    "54": "Impuesto de renta y complementarios",
    "59": "Ganancias y pérdidas",
    "6": "Costos de ventas",
    "7": "Costos de producción u operación",
    "135515": "Retención en la fuente (anticipo)",
    "135517": "Impuesto a las ventas retenido",
    "135518": "Impuesto de industria y comercio retenido",
    "135519": "Autorretención de renta",
    "1330": "Anticipos y avances",
    "1325": "Cuentas por cobrar a socios y accionistas",
}

# Nombres que suelen ser gasto no deducible. Es una lista para revisar, no una conclusión.
NO_DEDUCIBLE = [
    (r"multa|sanci[oó]n|litigio", "Multas, sanciones y litigios (art. 105 E.T.)"),
    (r"inter[eé]s(es)?\s+(de\s+)?mora|intereses\s+moratorios", "Intereses de mora (art. 11 Ley 1430 de 2010)"),
    (r"4\s*x\s*mil|gmf|grav[aá]men", "GMF: deducible solo el 50% certificado (art. 115 E.T.)"),
    (r"ajuste al peso", "Ajuste al peso"),
    (r"impuesto de renta|impuesto sobre la renta|renta y complementarios", "Impuesto de renta (art. 115 E.T.)"),
    (r"ejercicios? anteriores|vigencias? anteriores", "Costos y gastos de ejercicios anteriores"),
    (r"donaci[oó]n", "Donaciones: descuento del art. 257, no deducción"),
    (r"indemnizaci", "Indemnizaciones (revisar relación de causalidad)"),
    (r"impuestos? asumidos?", "Impuestos asumidos"),
    (r"extraordinari|diversos", "Gastos extraordinarios o diversos (revisar soporte)"),
]


def _numero(valor) -> Decimal:
    if valor is None or valor == "":
        return Decimal(0)
    if isinstance(valor, (int, float, Decimal)):
        return Decimal(str(valor))
    texto = str(valor).strip().replace("$", "").replace(" ", "")
    if re.fullmatch(r"-?[\d.]+,\d+", texto):
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", "")
    try:
        return Decimal(texto)
    except InvalidOperation:
        return Decimal(0)


def _columna(indicador: str, encabezado: list[str] | None) -> int:
    if re.fullmatch(r"[A-Za-z]{1,3}", indicador):
        n = 0
        for letra in indicador.upper():
            n = n * 26 + (ord(letra) - 64)
        return n - 1
    if encabezado and indicador in encabezado:
        return encabezado.index(indicador)
    raise SystemExit(f"Columna no encontrada: {indicador}")


def leer_filas(ruta: Path, hoja: str | None) -> list[list]:
    if ruta.suffix.lower() in {".xlsx", ".xlsm"}:
        try:
            import openpyxl
        except ImportError:
            raise SystemExit("Falta openpyxl. Ejecute con: uv run --with openpyxl python resumir_balance.py ...")
        libro = openpyxl.load_workbook(ruta, data_only=True, read_only=True)
        ws = libro[hoja] if hoja else libro.worksheets[0]
        return [list(f) for f in ws.iter_rows(values_only=True)]
    with ruta.open(encoding="utf-8-sig", newline="") as fh:
        return [fila for fila in csv.reader(fh)]


def cargar(args) -> dict[str, tuple[str, Decimal]]:
    filas = leer_filas(Path(args.archivo), args.hoja)
    encabezado = None
    for fila in filas[:15]:
        textos = [str(c or "").strip() for c in fila]
        if any(t.upper() in {"CUENTA", "CODIGO", "CÓDIGO"} for t in textos):
            encabezado = textos
            break
    ic = _columna(args.col_cuenta, encabezado)
    inom = _columna(args.col_nombre, encabezado)
    isal = _columna(args.col_saldo, encabezado)
    cuentas: dict[str, tuple[str, Decimal]] = {}
    for fila in filas:
        if len(fila) <= max(ic, inom, isal):
            continue
        codigo = str(fila[ic] or "").strip().split(".")[0]
        if not re.fullmatch(r"\d{1,10}", codigo):
            continue
        cuentas[codigo] = (str(fila[inom] or "").strip(), _numero(fila[isal]))
    if not cuentas:
        raise SystemExit("No se leyó ninguna cuenta PUC. Revise --hoja y las columnas.")
    return cuentas


def total(cuentas: dict[str, tuple[str, Decimal]], prefijo: str) -> Decimal | None:
    """Saldo del código exacto; si no existe, la suma del nivel más detallado debajo de él."""
    if prefijo in cuentas:
        return cuentas[prefijo][1]
    hijas = [c for c in cuentas if c.startswith(prefijo) and c != prefijo]
    if not hijas:
        return None
    largo = max(len(c) for c in hijas)
    return sum((cuentas[c][1] for c in hijas if len(c) == largo), Decimal(0))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo")
    p.add_argument("--hoja")
    p.add_argument("--col-cuenta", default="CUENTA")
    p.add_argument("--col-nombre", default="NOMBRE CUENTA")
    p.add_argument("--col-saldo", default="SALDO ACTUAL")
    p.add_argument("--mes-corte", type=int, required=True, help="Último mes incluido en el balance (1-12).")
    p.add_argument("--alza-diciembre-ingresos", type=Decimal, default=Decimal(0),
                   help="Meses adicionales que suma diciembre en ingresos (0.3 = diciembre 30%% más alto).")
    p.add_argument("--alza-diciembre-costos", type=Decimal, default=Decimal(0))
    p.add_argument("--alza-diciembre-gastos", type=Decimal, default=Decimal(0))
    args = p.parse_args(argv)
    if not 1 <= args.mes_corte <= 12:
        raise SystemExit("--mes-corte debe estar entre 1 y 12.")

    cuentas = cargar(args)
    corte: dict[str, str | None] = {}
    for codigo in GRUPOS:
        valor = total(cuentas, codigo)
        corte[codigo] = None if valor is None else str(valor)

    # Los ingresos (clase 4) suelen venir con saldo crédito negativo: se presentan en positivo.
    signo_ingresos = Decimal(-1) if (total(cuentas, "4") or Decimal(0)) < 0 else Decimal(1)
    meses_restantes = 12 - args.mes_corte

    def proyectar(valor: Decimal | None, alza: Decimal) -> dict | None:
        if valor is None:
            return None
        promedio = valor / args.mes_corte
        resto = promedio * meses_restantes + (promedio * alza if meses_restantes else 0)
        return {"a_la_fecha": str(valor), "proyectado_resto_del_anio": str(resto.quantize(Decimal("0.01"))),
                "total_anio": str((valor + resto).quantize(Decimal("0.01")))}

    proyeccion = {}
    for codigo, alza in (("41", args.alza_diciembre_ingresos), ("42", args.alza_diciembre_ingresos),
                         ("6", args.alza_diciembre_costos), ("7", args.alza_diciembre_costos),
                         ("51", args.alza_diciembre_gastos), ("52", args.alza_diciembre_gastos),
                         ("53", args.alza_diciembre_gastos)):
        valor = total(cuentas, codigo)
        if valor is not None and codigo.startswith("4"):
            valor = valor * signo_ingresos
        proyeccion[codigo] = proyectar(valor, alza)
    # Retenciones que le practicaron: misma proporción mensual, sin alza. La autorretención
    # (135519) no se proyecta aquí: la calcula el motor con la tarifa del CIIU.
    proyeccion["135515"] = proyectar(total(cuentas, "135515"), Decimal(0))

    revisar = []
    for codigo, (nombre, saldo) in sorted(cuentas.items()):
        if not codigo[:1] in {"5", "6", "7"} or saldo == 0 or len(codigo) < 6:
            continue
        for patron, motivo in NO_DEDUCIBLE:
            if re.search(patron, nombre, re.I):
                revisar.append({"cuenta": codigo, "nombre": nombre, "saldo": str(saldo), "motivo": motivo})
                break
    # Si una subcuenta y sus auxiliares coinciden, se deja solo el nivel más detallado.
    codigos = {r["cuenta"] for r in revisar}
    revisar = [r for r in revisar if not any(c != r["cuenta"] and c.startswith(r["cuenta"]) for c in codigos)]

    salida = {
        "archivo": Path(args.archivo).name,
        "hoja": args.hoja,
        "mes_corte": args.mes_corte,
        "meses_restantes": meses_restantes,
        "supuestos": {
            "alza_diciembre_ingresos": str(args.alza_diciembre_ingresos),
            "alza_diciembre_costos": str(args.alza_diciembre_costos),
            "alza_diciembre_gastos": str(args.alza_diciembre_gastos),
            "signo_ingresos": "invertido (saldo crédito)" if signo_ingresos < 0 else "tal cual",
        },
        "saldos_a_la_fecha": {f"{c} {GRUPOS[c]}": v for c, v in corte.items()},
        "proyeccion_a_diciembre": {f"{c} {GRUPOS[c]}": v for c, v in proyeccion.items()},
        "cuentas_a_revisar_no_deducibles": revisar,
        "aviso": "Totales contables, no fiscales. La depuración y el impuesto los hace el motor fiscal.",
    }
    json.dump(salida, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
