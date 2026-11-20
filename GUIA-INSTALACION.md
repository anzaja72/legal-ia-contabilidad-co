# Guía de instalación

La guía completa, paso a paso y sin terminal, está en **https://cuenta.legal-ia.co/guia.html**.

En resumen:

- **App de Claude (recomendado):** genere su token en https://cuenta.legal-ia.co, copie la URL del conector y agréguela en *Configuración → Conectores → Agregar conector personalizado*. Luego suba la skill `proyeccion-renta-pj.zip` en *Configuración → Capacidades → Skills*.
- **Claude Code:** instale el plugin con `claude plugin marketplace add anzaja72/legal-ia-contabilidad-co` y `claude plugin install contabilidad-co@legal-ia`. Al activarlo, Claude Code le pide el token y lo guarda en el llavero del sistema.

Para empaquetar las skills como .zip: `python scripts/empaquetar_skills.py` (requiere PyYAML).
