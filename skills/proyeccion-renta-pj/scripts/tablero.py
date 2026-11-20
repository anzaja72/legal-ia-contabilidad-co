#!/usr/bin/env python3
"""Arma el tablero HTML de una proyección de renta (formulario 110) a partir de un JSON.

No calcula impuestos: muestra las cifras que devolvió el motor fiscal y los totales del balance.

Uso:
    python tablero.py proyeccion.json --salida tablero.html                 # archivo completo
    python tablero.py proyeccion.json --salida contenido.html --artefacto   # sin <html>/<head>/<body>

El JSON de entrada (lo arma la skill `proyeccion-renta-pj`):
{
  "empresa": "Sociedad Ejemplo SAS", "ciudad": "Barranquilla", "fecha": "2026-11-20",
  "anio_gravable": 2026, "corte": "septiembre de 2026", "ciiu": "5630",
  "elaborado_por": "Nombre, cargo",
  "proyeccion": {"ingresos": {"a_la_fecha": 0, "proyectado": 0}, "costos": {...},
                 "gastos": {...}, "utilidad_contable": 0},
  "no_deducibles": [{"concepto": "...", "a_la_fecha": 0, "proyectado": 0, "norma": "..."}],
  "supuestos": ["..."], "hallazgos": ["..."],
  "escenarios": [{"nombre": "...", "descripcion": "...", "motor": {respuesta de /v1/renta-pj/calcular}}],
  "escenario_principal": 0
}
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

FILAS_110 = [
    ("casilla_58_total_ingresos_brutos", "58", "Ingresos brutos", ""),
    ("casilla_67_total_costos_y_gastos", "67", "Costos y deducciones", "menos"),
    ("casilla_75_renta_liquida", "75", "Renta líquida", "sub"),
    ("casilla_74_compensaciones", "74", "Compensaciones", "menos"),
    ("casilla_77_renta_exenta", "77", "Rentas exentas", "menos"),
    ("casilla_79_renta_liquida_gravable", "79", "Renta líquida gravable", "sub"),
    ("casilla_84_impuesto_renta_liquida_gravable", "84", "Impuesto sobre la renta líquida gravable", ""),
    ("casilla_93_descuentos_tributarios", "93", "Descuentos tributarios", "menos"),
    ("casilla_95_impuesto_a_adicionar", "95", "Impuesto a adicionar (tasa mínima)", ""),
    ("casilla_97_impuesto_ganancias_ocasionales", "97", "Impuesto de ganancias ocasionales", ""),
    ("casilla_99_total_impuesto_a_cargo", "99", "Total impuesto a cargo", "sub"),
    ("casilla_105_autorretenciones", "105", "Autorretenciones", "menos"),
    ("casilla_106_otras_retenciones", "106", "Otras retenciones", "menos"),
    ("casilla_108_anticipo_anio_siguiente", "108", "Anticipo del año siguiente", ""),
    ("casilla_113_total_saldo_a_pagar", "113", "Saldo a pagar", "total"),
    ("casilla_114_total_saldo_a_favor", "114", "Saldo a favor", "total"),
]

CSS = """
:root {
  /* Hoja de trabajo del contador: papel de formulario, tinta azul DIAN y un sello para el saldo. */
  --papel: #f7f8f6; --hoja: #ffffff; --tinta: #1b2430; --tenue: #5d6876; --linea: #dfe3e0;
  --azul: #1f4e8c; --azul-suave: #e6eef8; --pagar: #a33a22; --pagar-suave: #f8e7e2;
  --favor: #1f6b4a; --favor-suave: #e2f1e9; --aviso: #8a5a00; --aviso-suave: #fbf0d9;
  --display: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --texto: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --cifra: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --papel: #11161c; --hoja: #18202a; --tinta: #e6ebf0; --tenue: #9aa6b3; --linea: #2a3542;
  --azul: #8fb6ec; --azul-suave: #1d2b3e; --pagar: #f0937c; --pagar-suave: #3a2019;
  --favor: #7dd3a8; --favor-suave: #16302a; --aviso: #f1c66e; --aviso-suave: #352a13; color-scheme: dark } }
:root[data-theme="dark"] {
  --papel: #11161c; --hoja: #18202a; --tinta: #e6ebf0; --tenue: #9aa6b3; --linea: #2a3542;
  --azul: #8fb6ec; --azul-suave: #1d2b3e; --pagar: #f0937c; --pagar-suave: #3a2019;
  --favor: #7dd3a8; --favor-suave: #16302a; --aviso: #f1c66e; --aviso-suave: #352a13; color-scheme: dark }
body { background: var(--papel); color: var(--tinta); font-family: var(--texto); font-size: 15px; line-height: 1.5; }
.pag { max-width: 1040px; margin: 0 auto; padding-block: 28px 48px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 22px; }
header { display: grid; gap: 6px; border-bottom: 2px solid var(--tinta); padding-bottom: 14px; }
.eyebrow { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--tenue); }
h1 { font-family: var(--display); font-weight: 700; font-size: clamp(24px, 4vw, 34px); margin: 0; text-wrap: balance; }
h2 { font-family: var(--display); font-size: 17px; margin: 0 0 10px; }
.meta { display: flex; flex-wrap: wrap; gap: 6px 18px; color: var(--tenue); font-size: 13.5px; }
.meta b { color: var(--tinta); font-weight: 600; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }
.kpi { background: var(--hoja); border: 1px solid var(--linea); border-radius: 6px; padding: 14px 16px; display: grid; gap: 4px; }
.kpi .v { font-family: var(--cifra); font-size: 21px; font-variant-numeric: tabular-nums; }
.kpi .l { font-size: 12.5px; color: var(--tenue); }
.kpi.sello { border: 2px solid var(--pagar); background: var(--pagar-suave); }
.kpi.sello .v { color: var(--pagar); font-weight: 600; }
.kpi.sello.favor { border-color: var(--favor); background: var(--favor-suave); }
.kpi.sello.favor .v { color: var(--favor); }
.bloque { background: var(--hoja); border: 1px solid var(--linea); border-radius: 6px; padding: 16px 18px; min-width: 0; }
.dos { display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 16px; }
@media (max-width: 760px) { .dos { grid-template-columns: 1fr; } }
.tabla { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { padding: 7px 8px; border-bottom: 1px solid var(--linea); text-align: left; vertical-align: top; }
th { font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: var(--tenue); font-weight: 600; }
td.n, th.n { text-align: right; font-family: var(--cifra); font-variant-numeric: tabular-nums; white-space: nowrap; }
td.cas { font-family: var(--cifra); color: var(--azul); width: 3.2em; }
tr.sub td { font-weight: 600; background: var(--azul-suave); }
tr.total td { font-weight: 700; border-top: 2px solid var(--tinta); }
tr.menos td:nth-child(2)::before { content: "− "; color: var(--tenue); }
.barras { display: grid; gap: 10px; }
.barra { display: grid; gap: 4px; }
.barra .t { display: flex; justify-content: space-between; gap: 8px; font-size: 13.5px; }
.barra .t span:last-child { font-family: var(--cifra); font-variant-numeric: tabular-nums; }
.pista { height: 10px; background: var(--azul-suave); border-radius: 3px; overflow: hidden; }
.pista i { display: block; height: 100%; background: var(--azul); }
.barra.principal .pista i { background: var(--pagar); }
.chip { display: inline-block; font-size: 11.5px; padding: 1px 8px; border-radius: 999px; background: var(--azul-suave); color: var(--azul); margin-left: 6px; }
ul.lista { margin: 0; padding-left: 18px; display: grid; gap: 6px; }
.hallazgos li::marker { color: var(--aviso); }
.aviso { background: var(--aviso-suave); border-left: 3px solid var(--aviso); padding: 10px 14px; border-radius: 4px; font-size: 14px; }
footer { color: var(--tenue); font-size: 12.5px; border-top: 1px solid var(--linea); padding-top: 12px; display: grid; gap: 4px; }
code { font-family: var(--cifra); font-size: 12.5px; }
"""

FUENTES = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700'
           '&family=IBM+Plex+Mono:wght@400;600&family=Source+Sans+3:wght@400;600&display=swap">')


def pesos(valor) -> str:
    if valor is None or valor == "":
        return "—"
    numero = round(float(valor))
    signo = "-" if numero < 0 else ""
    return f"{signo}${abs(numero):,}".replace(",", ".")


def e(texto) -> str:
    return html.escape(str(texto if texto is not None else ""))


def casillas(escenario: dict) -> dict:
    motor = escenario.get("motor") or {}
    return motor.get("casillas") or motor


def construir(datos: dict) -> tuple[str, str]:
    escenarios = datos.get("escenarios") or []
    if not escenarios:
        raise SystemExit("El JSON no trae escenarios con la respuesta del motor.")
    i = int(datos.get("escenario_principal", 0))
    principal = escenarios[i]
    c = casillas(principal)
    motor = principal.get("motor") or {}
    tm = motor.get("tasa_minima") or {}
    saldo_pagar = c.get("casilla_113_total_saldo_a_pagar") or 0
    saldo_favor = c.get("casilla_114_total_saldo_a_favor") or 0
    titulo = f"Proyección de renta {datos.get('anio_gravable', '')} · {datos.get('empresa', '')}".strip()

    partes = [f'<div class="pag">', "<header>",
              f'<div class="eyebrow">Formulario 110 · proyección al corte de {e(datos.get("corte"))}</div>',
              f"<h1>{e(datos.get('empresa'))}</h1>",
              '<div class="meta">',
              f"<span>Año gravable <b>{e(datos.get('anio_gravable'))}</b></span>",
              f"<span>CIIU <b>{e(datos.get('ciiu'))}</b></span>",
              f"<span>{e(datos.get('ciudad'))}, {e(datos.get('fecha'))}</span>",
              f"<span>Escenario <b>{e(principal.get('nombre'))}</b></span>",
              "</div></header>"]

    favor = saldo_favor and not saldo_pagar
    partes.append('<section class="kpis" aria-label="Resumen">')
    for valor, etiqueta in ((c.get("casilla_99_total_impuesto_a_cargo"), "Impuesto a cargo (casilla 99)"),
                            (c.get("casilla_107_total_retenciones"), "Retenciones y autorretenciones (casilla 107)"),
                            (c.get("casilla_108_anticipo_anio_siguiente"), "Anticipo del año siguiente (casilla 108)")):
        partes.append(f'<div class="kpi"><span class="v">{pesos(valor)}</span><span class="l">{e(etiqueta)}</span></div>')
    partes.append(f'<div class="kpi sello{" favor" if favor else ""}"><span class="v">{pesos(saldo_favor if favor else saldo_pagar)}</span>'
                  f'<span class="l">{"Saldo a favor (casilla 114)" if favor else "Saldo a pagar (casilla 113)"}</span></div>')
    partes.append("</section>")

    # Depuración del formulario 110 y comparación de escenarios.
    partes.append('<div class="dos"><section class="bloque"><h2>Depuración del formulario 110</h2><div class="tabla"><table>'
                  '<thead><tr><th>Cas.</th><th>Concepto</th><th class="n">Valor</th></tr></thead><tbody>')
    for clave, numero, nombre, clase in FILAS_110:
        valor = c.get(clave)
        if valor in (None, 0) and clase not in {"sub", "total"} and numero not in {"58", "67", "84"}:
            continue
        if clave == "casilla_114_total_saldo_a_favor" and not saldo_favor:
            continue
        if clave == "casilla_113_total_saldo_a_pagar" and favor:
            continue
        partes.append(f'<tr class="{clase}"><td class="cas">{numero}</td><td>{e(nombre)}</td><td class="n">{pesos(valor)}</td></tr>')
    partes.append("</tbody></table></div>")
    if tm:
        partes.append(f'<p style="margin:10px 0 0;font-size:13.5px;color:var(--tenue)">Tasa mínima (art. 240 par. 6): tasa depurada '
                      f'<b>{float(tm.get("tasa_tributacion_depurada") or 0)*100:.1f} %</b> frente al 15 %; impuesto a adicionar '
                      f'{pesos(tm.get("impuesto_a_adicionar"))}.</p>')
    partes.append("</section>")

    partes.append('<section class="bloque"><h2>Escenarios</h2><div class="barras">')
    maximo = max(float(casillas(x).get("casilla_113_total_saldo_a_pagar") or 0) for x in escenarios) or 1
    for j, esc in enumerate(escenarios):
        valor = float(casillas(esc).get("casilla_113_total_saldo_a_pagar") or 0)
        ancho = max(0.0, min(100.0, valor / maximo * 100))
        partes.append(f'<div class="barra{" principal" if j == i else ""}"><div class="t"><span>{e(esc.get("nombre"))}'
                      f'{"<span class=chip>principal</span>" if j == i else ""}</span><span>{pesos(valor)}</span></div>'
                      f'<div class="pista"><i style="width:{ancho:.1f}%"></i></div>'
                      f'<span style="font-size:12.5px;color:var(--tenue)">{e(esc.get("descripcion"))}</span></div>')
    partes.append('</div><p style="margin:12px 0 0;font-size:12.5px;color:var(--tenue)">Saldo a pagar de cada escenario, a escala.</p></section></div>')

    proy = datos.get("proyeccion") or {}
    if proy:
        partes.append('<section class="bloque"><h2>Proyección contable a diciembre</h2><div class="tabla"><table><thead><tr>'
                      '<th>Concepto</th><th class="n">A la fecha</th><th class="n">Proyectado</th><th class="n">Total año</th></tr></thead><tbody>')
        for clave, nombre in (("ingresos", "Ingresos"), ("costos", "Costos"), ("gastos", "Gastos")):
            fila = proy.get(clave) or {}
            if fila:
                total = fila.get("total", (fila.get("a_la_fecha") or 0) + (fila.get("proyectado") or 0))
                partes.append(f'<tr><td>{nombre}</td><td class="n">{pesos(fila.get("a_la_fecha"))}</td>'
                              f'<td class="n">{pesos(fila.get("proyectado"))}</td><td class="n">{pesos(total)}</td></tr>')
        if "utilidad_contable" in proy:
            partes.append(f'<tr class="sub"><td>Utilidad contable</td><td></td><td></td><td class="n">{pesos(proy["utilidad_contable"])}</td></tr>')
        partes.append("</tbody></table></div></section>")

    nd = datos.get("no_deducibles") or []
    if nd:
        partes.append('<section class="bloque"><h2>Gastos no deducibles tomados</h2><div class="tabla"><table><thead><tr>'
                      '<th>Concepto</th><th class="n">A la fecha</th><th class="n">Proyectado</th><th>Norma</th></tr></thead><tbody>')
        for fila in nd:
            partes.append(f'<tr><td>{e(fila.get("concepto"))}</td><td class="n">{pesos(fila.get("a_la_fecha"))}</td>'
                          f'<td class="n">{pesos(fila.get("proyectado"))}</td><td>{e(fila.get("norma"))}</td></tr>')
        partes.append("</tbody></table></div></section>")

    lado = []
    if datos.get("hallazgos"):
        lado.append('<section class="bloque"><h2>Hallazgos</h2><ul class="lista hallazgos">'
                    + "".join(f"<li>{e(h)}</li>" for h in datos["hallazgos"]) + "</ul></section>")
    if datos.get("supuestos"):
        lado.append('<section class="bloque"><h2>Supuestos</h2><ul class="lista">'
                    + "".join(f"<li>{e(s)}</li>" for s in datos["supuestos"]) + "</ul></section>")
    if lado:
        partes.append('<div class="dos">' + "".join(lado) + "</div>")

    advertencias = motor.get("advertencias") or []
    if advertencias:
        partes.append('<div class="aviso">' + "<br>".join(e(a) for a in advertencias) + "</div>")

    partes.append(f'<footer><span>Liquidación del motor fiscal: <code>version_tablas {e(motor.get("version_tablas"))}</code>, '
                  f'vigencia <code>{e(motor.get("vigencia"))}</code>. {e(motor.get("base_legal"))}</span>'
                  f'<span>Documento de trabajo. Las cifras proyectadas cambian con el cierre real. '
                  f'Elaboró: {e(datos.get("elaborado_por"))}.</span></footer></div>')
    return titulo, "\n".join(partes)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("entrada")
    p.add_argument("--salida", required=True)
    p.add_argument("--artefacto", action="store_true", help="Solo el contenido, para publicarlo como artefacto.")
    args = p.parse_args(argv)
    datos = json.loads(Path(args.entrada).read_text(encoding="utf-8"))
    titulo, cuerpo = construir(datos)
    cabeza = (f"<title>{e(titulo)}</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n"
              f"{FUENTES}\n<style>{CSS}</style>\n")
    if args.artefacto:
        salida = cabeza + cuerpo
    else:
        salida = ("<!doctype html>\n<html lang=\"es\"><head><meta charset=\"utf-8\">"
                  "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
                  + cabeza + "</head><body>\n" + cuerpo + "\n</body></html>\n")
    Path(args.salida).write_text(salida, encoding="utf-8")
    sys.stdout.write(f"tablero: {args.salida}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
