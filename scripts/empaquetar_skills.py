#!/usr/bin/env python3
"""Empaqueta cada skill como .zip para subirla a la app de Claude (Configuración > Capacidades > Skills).

Cada paquete queda autocontenido:
- carpeta <skill>/ con SKILL.md en su raíz;
- la guía compartida skills/_shared/motor-fiscal-cliente.md copiada en <skill>/referencia/;
- el encabezado YAML solo con name, description y metadata (version y author pasan a metadata).

Uso: python scripts/empaquetar_skills.py [--salida dist]
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SKILLS = RAIZ / "skills"
COMPARTIDA = SKILLS / "_shared" / "motor-fiscal-cliente.md"


def _encabezado(texto: str) -> tuple[str, str]:
    if not texto.startswith("---\n"):
        raise SystemExit("SKILL.md sin encabezado YAML")
    fin = texto.index("\n---\n", 4)
    return texto[4:fin], texto[fin + 5:]


def normalizar(texto: str) -> str:
    """Deja name, description y metadata; version y author se mueven dentro de metadata."""
    import yaml

    crudo, cuerpo = _encabezado(texto)
    datos = yaml.safe_load(crudo)
    meta = dict(datos.get("metadata") or {})
    for clave in ("version", "author"):
        if clave in datos:
            meta[clave] = str(datos[clave])
    nuevo = {"name": datos["name"], "description": " ".join(str(datos["description"]).split())}
    if meta:
        nuevo["metadata"] = meta
    cuerpo = cuerpo.replace("skills/_shared/motor-fiscal-cliente.md", "referencia/motor-fiscal-cliente.md")
    return "---\n" + yaml.safe_dump(nuevo, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + cuerpo


def empaquetar(carpeta: Path, salida: Path) -> Path:
    nombre = carpeta.name
    destino = salida / f"{nombre}.zip"
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for archivo in sorted(carpeta.rglob("*")):
            if archivo.is_dir() or "__pycache__" in archivo.parts or archivo.name.startswith("."):
                continue
            rel = f"{nombre}/{archivo.relative_to(carpeta).as_posix()}"
            if archivo.name == "SKILL.md" and archivo.parent == carpeta:
                z.writestr(rel, normalizar(archivo.read_text(encoding="utf-8")))
            else:
                z.write(archivo, rel)
        z.write(COMPARTIDA, f"{nombre}/referencia/motor-fiscal-cliente.md")
    return destino


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--salida", default=str(RAIZ / "dist"))
    args = p.parse_args()
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    for carpeta in sorted(SKILLS.iterdir()):
        if carpeta.is_dir() and (carpeta / "SKILL.md").exists():
            destino = empaquetar(carpeta, salida)
            if not re.fullmatch(r"[a-z0-9-]{1,64}", carpeta.name):
                raise SystemExit(f"Nombre de skill inválido: {carpeta.name}")
            print(f"{destino.name}: {destino.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
