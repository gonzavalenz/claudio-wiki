#!/usr/bin/env python3
"""Genera assets/claude-code-guia-equipo-datos.html a partir de docs/*.md.

Cómo se corre (desde la raíz del repo, solo necesita Python 3.8+ y la stdlib):

    python3 assets/build_guia.py

- Fuente de verdad: docs/01-*.md … docs/21-*.md y docs/cheatsheet.md.
  El orden y la agrupación en 5 partes están en PARTES (abajo).
- Cada capítulo sale así:
    * "# Título"                       -> título del capítulo
    * primer blockquote ("> **En 30 segundos:** …") -> recuadro "En 30 segundos"
    * "## Trucos y errores comunes"    -> dos callouts: "Trucos" y "Cuidado"
    * "## Ver también"                 -> lista compacta de links
    * el resto (##, ###, tablas, listas, código) se convierte tal cual.
- Links: NN-*.md (y NN-*.md#ancla) pasan a anclas internas de la página;
  ../ejemplos/…, ../buenas-practicas/… etc. quedan relativos a assets/ (misma
  profundidad que docs/). Un link a un archivo que no existe se deja como texto
  y se avisa por consola.
- La página generada es standalone: usa css/base.css, css/guia.css y js/site.js,
  sin CDNs ni dependencias; se abre con doble clic (file://).

Convertidor de Markdown mínimo, pensado para el subconjunto que usan los docs
(encabezados, párrafos, listas de un nivel con bloques indentados, tablas,
bloques de código cercados, blockquotes, código inline, negrita, cursiva, links).
"""

import html
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DOCS = os.path.join(RAIZ, "docs")
SALIDA = os.path.join(AQUI, "claude-code-guia-equipo-datos.html")

# (nombre de la parte, descripción, [(id de ancla, número, archivo, nombre corto para el índice)])
PARTES = [
    ("Entender", "Qué es Claude Code, cómo piensa, cómo se instala y cómo cuidar el contexto.", [
        ("fundamentos", "01", "01-fundamentos.md", "Fundamentos"),
        ("claude-code", "02", "02-que-es-claude-code.md", "Qué es Claude Code"),
        ("instalacion", "03", "03-instalacion.md", "Instalación"),
        ("modelos", "04", "04-modelos.md", "Modelos y esfuerzo"),
        ("contexto", "05", "05-contexto.md", "Contexto"),
    ]),
    ("Configurar", "Memoria, permisos, comandos y plan mode: que trabaje como trabaja tu equipo.", [
        ("memoria", "06", "06-memoria.md", "Memoria (CLAUDE.md)"),
        ("permisos", "07", "07-permisos.md", "Permisos"),
        ("comandos", "08", "08-comandos-slash.md", "Comandos y atajos"),
        ("plan-mode", "09", "09-plan-mode-y-checkpoints.md", "Plan mode y checkpoints"),
    ]),
    ("Extender", "Skills, subagents, hooks, MCP y plugins: conocimiento, herramientas y reglas.", [
        ("skills", "10", "10-skills.md", "Skills"),
        ("subagents", "11", "11-subagents.md", "Subagents"),
        ("hooks", "12", "12-hooks.md", "Hooks"),
        ("mcp", "13", "13-mcp.md", "MCP"),
        ("plugins", "14", "14-plugins.md", "Plugins"),
    ]),
    ("Escalar", "Varias sesiones en paralelo, automatización y trabajo con otros agentes.", [
        ("paralelismo", "15", "15-paralelismo-y-worktrees.md", "Paralelismo y worktrees"),
        ("automatizacion", "16", "16-automatizacion.md", "Automatización"),
        ("multi-agente", "17", "17-multi-agente-gemini.md", "Multi-agente con Gemini"),
        ("arquitecturas", "18", "18-arquitecturas-de-integracion.md", "Arquitecturas"),
    ]),
    ("Día a día", "Cómo organizar el repo, flujos concretos, costos y referencia rápida.", [
        ("estructura", "19", "19-estructura-de-proyecto.md", "Estructura de proyecto"),
        ("flujos", "20", "20-flujos-de-trabajo.md", "Flujos de trabajo"),
        ("costos", "21", "21-costos.md", "Costos"),
        ("cheatsheet", "—", "cheatsheet.md", "Referencia rápida"),
    ]),
]

ID_POR_ARCHIVO = {c[2]: c[0] for _, _, caps in PARTES for c in caps}
AVISOS = []


# --------------------------------------------------------------------------
# Inline
# --------------------------------------------------------------------------

def slug(texto):
    """Ancla estilo GitHub: minúsculas, sin puntuación, espacios -> guiones."""
    t = re.sub(r"<[^>]+>", "", texto).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t, flags=re.UNICODE)
    return t.replace(" ", "-")


def resolver_link(url, cap_id):
    """Devuelve el href para la página generada, o None si el destino no existe."""
    if re.match(r"^[a-z]+:", url):
        return url
    if url.startswith("#"):
        return "#%s--%s" % (cap_id, url[1:])
    ruta, _, frag = url.partition("#")
    if "/" not in ruta and ruta in ID_POR_ARCHIVO:
        destino = ID_POR_ARCHIVO[ruta]
        return "#%s--%s" % (destino, frag) if frag else "#" + destino
    # relativo a docs/ -> relativo a assets/ (misma profundidad)
    abs_ruta = os.path.normpath(os.path.join(DOCS, ruta))
    if not os.path.exists(abs_ruta):
        AVISOS.append("link roto en %s: %s" % (cap_id, url))
        return None
    rel = os.path.relpath(abs_ruta, AQUI).replace(os.sep, "/")
    if ruta.endswith("/") and not rel.endswith("/"):
        rel += "/"
    return rel + ("#" + frag if frag else "")


def inline(texto, cap_id):
    codigos = []

    def guardar_code(m):
        codigos.append("<code>%s</code>" % html.escape(m.group(2).strip() if m.group(2).strip() else m.group(2)))
        return "\x00%d\x00" % (len(codigos) - 1)

    t = re.sub(r"(`+)(.+?)\1", guardar_code, texto)
    t = html.escape(t, quote=False)

    def link(m):
        etiqueta, url = m.group(1), m.group(2)
        href = resolver_link(html.unescape(url), cap_id)
        if href is None:
            return etiqueta
        externo = href.startswith("http")
        attrs = ' rel="noopener"' if externo else ""
        return '<a href="%s"%s>%s</a>' % (html.escape(href), attrs, etiqueta)

    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: codigos[int(m.group(1))], t)
    return t


# --------------------------------------------------------------------------
# Bloques
# --------------------------------------------------------------------------

RE_FENCE = re.compile(r"^(\s*)(`{3,})\s*([\w+-]*)\s*$")
RE_LI = re.compile(r"^([-*]|\d+\.)\s+(.*)$")


def separar_celdas(linea):
    linea = linea.strip()
    if linea.startswith("|"):
        linea = linea[1:]
    if linea.endswith("|") and not linea.endswith("\\|"):
        linea = linea[:-1]
    celdas, actual, en_code = [], "", False
    i = 0
    while i < len(linea):
        ch = linea[i]
        if ch == "\\" and i + 1 < len(linea) and linea[i + 1] == "|":
            actual += "|"
            i += 2
            continue
        if ch == "`":
            en_code = not en_code
        if ch == "|" and not en_code:
            celdas.append(actual.strip())
            actual = ""
        else:
            actual += ch
        i += 1
    celdas.append(actual.strip())
    return celdas


def codigo(lang, lineas):
    out = []
    comentarios = lang in ("bash", "sh", "shell", "python", "yaml", "text", "")
    for ln in lineas:
        esc = html.escape(ln, quote=False)
        if comentarios and re.match(r"^\s*#(?!!)", ln):
            esc = '<span class="tok-c">%s</span>' % esc
        out.append(esc)
    clase = ' class="lang-%s"' % lang if lang else ""
    return "<pre><code%s>%s</code></pre>" % (clase, "\n".join(out))


def bloques(lineas, cap_id, nivel_h=4):
    """Convierte una lista de líneas markdown en HTML."""
    out = []
    i = 0
    n = len(lineas)
    while i < n:
        ln = lineas[i]
        if not ln.strip():
            i += 1
            continue

        m = RE_FENCE.match(ln)
        if m:
            indent, ticks, lang = len(m.group(1)), m.group(2), m.group(3)
            i += 1
            cuerpo = []
            while i < n and not re.match(r"^\s*%s`*\s*$" % ticks, lineas[i]):
                cuerpo.append(lineas[i][indent:] if lineas[i][:indent].strip() == "" else lineas[i])
                i += 1
            i += 1
            out.append(codigo(lang, cuerpo))
            continue

        m = re.match(r"^(#{2,6})\s+(.*)$", ln)
        if m:
            nivel = min(6, len(m.group(1)) - 2 + nivel_h)
            texto = inline(m.group(2), cap_id)
            out.append('<h%d id="%s--%s">%s</h%d>' % (nivel, cap_id, slug(m.group(2).replace("`", "")), texto, nivel))
            i += 1
            continue

        if ln.lstrip().startswith("|"):
            filas = []
            while i < n and lineas[i].lstrip().startswith("|"):
                filas.append(separar_celdas(lineas[i]))
                i += 1
            cab = filas[0]
            cuerpo = [f for f in filas[1:] if not all(re.match(r"^:?-{2,}:?$", c) for c in f)]
            th = "".join("<th>%s</th>" % inline(c, cap_id) for c in cab)
            trs = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c, cap_id) for c in f) for f in cuerpo)
            out.append('<div class="tabla-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, trs))
            continue

        if ln.startswith(">"):
            parrafos, actual = [], []
            while i < n and lineas[i].startswith(">"):
                contenido = lineas[i][1:].strip()
                if contenido:
                    actual.append(inline(contenido, cap_id))
                elif actual:
                    parrafos.append(actual)
                    actual = []
                i += 1
            if actual:
                parrafos.append(actual)
            texto = "".join("<p>%s</p>" % "<br>".join(p) for p in parrafos)
            plano = re.sub(r"<[^>]+>", "", texto).lower()
            tipo = "callout-warn" if re.search(r"\bno (garantiza|sirve)|\bnunca\b|cuidado", plano) else "callout-ex"
            out.append('<div class="callout %s">%s</div>' % (tipo, texto))
            continue

        m = RE_LI.match(ln)
        if m:
            ordenada = m.group(1)[0].isdigit()
            items = []
            while i < n:
                m = RE_LI.match(lineas[i])
                if not m or (m.group(1)[0].isdigit()) != ordenada:
                    break
                item = [m.group(2)]
                i += 1
                # continuación: líneas indentadas, o en blanco seguidas de indentadas
                while i < n:
                    if lineas[i].startswith("  ") and lineas[i].strip():
                        item.append(lineas[i])
                        i += 1
                    elif not lineas[i].strip() and i + 1 < n and lineas[i + 1].startswith("  ") and lineas[i + 1].strip():
                        item.append("")
                        i += 1
                    else:
                        break
                items.append(item)
                # una línea en blanco entre ítems no corta la lista
                if i < n and not lineas[i].strip() and i + 1 < n and RE_LI.match(lineas[i + 1]) \
                        and (RE_LI.match(lineas[i + 1]).group(1)[0].isdigit()) == ordenada:
                    i += 1
            lis = []
            for item in items:
                if len(item) == 1:
                    lis.append("<li>%s</li>" % inline(item[0], cap_id))
                else:
                    resto = [re.sub(r"^ {2,4}", "", x) for x in item[1:]]
                    # líneas de continuación de párrafo (no bloques) se pegan al texto
                    primera = [item[0]]
                    while resto and resto[0].strip() and not RE_FENCE.match(resto[0]) and not resto[0].lstrip().startswith(("|", ">")) and not RE_LI.match(resto[0]):
                        primera.append(resto.pop(0).strip())
                    lis.append("<li>%s%s</li>" % (inline(" ".join(primera), cap_id), bloques(resto, cap_id, nivel_h)))
            tag = "ol" if ordenada else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join(lis), tag))
            continue

        if re.match(r"^(-{3,}|\*{3,})\s*$", ln):
            i += 1
            continue

        # párrafo
        par = []
        while i < n and lineas[i].strip() and not RE_FENCE.match(lineas[i]) \
                and not re.match(r"^#{2,6}\s", lineas[i]) and not lineas[i].lstrip().startswith(("|", ">")) \
                and not RE_LI.match(lineas[i]):
            par.append(lineas[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(par), cap_id))
    return "\n".join(out)


# --------------------------------------------------------------------------
# Capítulos
# --------------------------------------------------------------------------

PALABRAS_CUIDADO = re.compile(
    r"(^no\b|\bno (bloquea|tiene|funciona|deshacen|valida|lee|aplican|ve|es una barrera|son una barrera|crean|entran|"
    r"comparten|se limpian|hay|sobrevive|existe|trae|van|es \")|\bnunca\b|^nada\b|cuidado|ojo|roto|rota|falla|"
    r"error|ignora|invalida|cuesta|gasta|secret|seguridad|injection|removid|en loop|mal escrito|confirmá|"
    r"silencio|peligro|riesg|no controlás)", re.IGNORECASE)


def es_cuidado(item):
    m = re.match(r"^\*\*(.+?)\*\*", item)
    cabeza = m.group(1) if m else item[:60]
    return bool(PALABRAS_CUIDADO.search(cabeza.strip("` ")) or re.match(r"^no\b", cabeza, re.IGNORECASE))


def items_de_lista(lineas):
    items = []
    for ln in lineas:
        m = RE_LI.match(ln)
        if m:
            items.append(m.group(2))
        elif ln.strip() and items:
            items[-1] += " " + ln.strip()
    return items


def render_trucos(lineas, cap_id):
    items = items_de_lista(lineas)
    if not items:
        return bloques(lineas, cap_id)
    trucos = [x for x in items if not es_cuidado(x)]
    cuidado = [x for x in items if es_cuidado(x)]
    out = ['<h4 id="%s--trucos-y-errores-comunes">Trucos y errores comunes</h4>' % cap_id]
    if trucos:
        out.append('<div class="callout callout-tip"><span class="lbl">Trucos</span><ul>%s</ul></div>'
                   % "".join("<li>%s</li>" % inline(x, cap_id) for x in trucos))
    if cuidado:
        out.append('<div class="callout callout-warn"><span class="lbl">Cuidado</span><ul>%s</ul></div>'
                   % "".join("<li>%s</li>" % inline(x, cap_id) for x in cuidado))
    return "\n".join(out)


def render_ver_tambien(lineas, cap_id):
    items = items_de_lista(lineas)
    if not items:
        return ""
    return ('<nav class="ver-tambien" aria-label="Ver también"><span class="lbl">Ver también</span><ul>%s</ul></nav>'
            % "".join("<li>%s</li>" % inline(x, cap_id) for x in items))


def capitulo(cap_id, num, archivo):
    texto = open(os.path.join(DOCS, archivo), encoding="utf-8").read()
    lineas = texto.splitlines()

    titulo = archivo
    if lineas and lineas[0].startswith("# "):
        titulo = lineas[0][2:].strip()
        lineas = lineas[1:]

    # primer blockquote -> "En 30 segundos"
    resumen = ""
    j = 0
    while j < len(lineas) and not lineas[j].strip():
        j += 1
    if j < len(lineas) and lineas[j].startswith(">"):
        cita = []
        while j < len(lineas) and lineas[j].startswith(">"):
            cita.append(lineas[j][1:].strip())
            j += 1
        resumen = " ".join(x for x in cita if x)
        resumen = re.sub(r"^\*\*En 30 segundos:?\*\*:?\s*", "", resumen)
        if resumen[:1].islower():
            resumen = resumen[0].upper() + resumen[1:]
        lineas = lineas[j:]

    # partir por secciones "## "
    secciones, actual = [], ("", [])
    en_code = False
    for ln in lineas:
        if RE_FENCE.match(ln):
            en_code = not en_code
        if not en_code and ln.startswith("## "):
            secciones.append(actual)
            actual = (ln[3:].strip(), [])
        else:
            actual[1].append(ln)
    secciones.append(actual)

    cuerpo = []
    for nombre, ls in secciones:
        clave = nombre.lower()
        if not nombre:
            cuerpo.append(bloques(ls, cap_id))
        elif clave.startswith("trucos y errores"):
            cuerpo.append(render_trucos(ls, cap_id))
        elif clave.startswith("ver también"):
            cuerpo.append(render_ver_tambien(ls, cap_id))
        else:
            cuerpo.append(bloques(["## " + nombre] + ls, cap_id))

    ruta = "../docs/" + archivo
    etiqueta = ("Capítulo %s" % num) if num != "—" else "Referencia"
    return '''
  <article class="cap prosa" id="%s">
    <p class="cap-meta">%s <span aria-hidden="true">·</span> <a href="%s">docs/%s</a></p>
    <h3 class="cap-titulo">%s</h3>
    <div class="resumen-30"><span class="lbl">En 30 segundos</span><p>%s</p></div>
%s
    <p class="leer-completo"><a href="%s">Leer completo en docs/%s →</a></p>
  </article>
''' % (cap_id, etiqueta, ruta, archivo, inline(titulo, cap_id), inline(resumen, cap_id),
       "\n".join(x for x in cuerpo if x), ruta, archivo)


# --------------------------------------------------------------------------
# Página
# --------------------------------------------------------------------------

def pagina():
    side, chips, contenido = [], [], []
    for i, (pnombre, pdesc, caps) in enumerate(PARTES, 1):
        side.append('      <div class="indice-grupo">\n        <p class="indice-grupo-titulo"><span class="n">%d</span>%s</p>' % (i, pnombre))
        for cap_id, num, _, corto in caps:
            side.append('        <a class="indice-link" href="#%s"><span class="num">%s</span><span class="txt">%s</span></a>' % (cap_id, num, corto))
        side.append("      </div>")
        chips.append('<li><a href="#parte-%d"><span class="n">%d</span>%s</a></li>' % (i, i, pnombre))
        contenido.append('''
<section class="parte" id="parte-%d" aria-labelledby="parte-%d-titulo">
  <header class="parte-head">
    <p class="parte-num">Parte %d de 5</p>
    <h2 id="parte-%d-titulo">%s</h2>
    <p>%s</p>
  </header>
''' % (i, i, i, i, pnombre, pdesc))
        for cap_id, num, archivo, _ in caps:
            contenido.append(capitulo(cap_id, num, archivo))
        contenido.append("</section>\n")

    return '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Guía de Claude Code — equipos de datos</title>
<meta name="description" content="Guía de referencia de Claude Code en español, en cinco partes: entender, configurar, extender, escalar y día a día. Ejemplos para Python, GCP, BigQuery, dbt y Airflow.">
<!-- Archivo GENERADO por assets/build_guia.py a partir de docs/. No editar a mano:
     cambiá el .md correspondiente y corré `python3 assets/build_guia.py`. -->
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/guia.css">
<script src="js/site.js"></script>
</head>
<body>
<a class="skip-link" href="#contenido">Saltar al contenido</a>

<header class="topnav">
  <a class="topnav-brand" href="index.html"><span class="marca" aria-hidden="true">&gt;_</span><span class="nombre">Claude Code · guía</span></a>
  <nav aria-label="Secciones del sitio">
    <ul class="topnav-links">
      <li><a href="index.html">Inicio</a></li>
      <li><a href="claude-code-guia-equipo-datos.html" aria-current="page">Guía</a></li>
      <li><a href="32-trucos-claude-code/index.html">32 trucos</a></li>
      <li><a href="#cheatsheet">Referencia<span class="largo"> rápida</span></a></li>
    </ul>
  </nav>
  <button class="theme-toggle" type="button" aria-label="Cambiar tema">☾</button>
</header>

<div class="subbar">
  <button class="btn btn-indice-mobile" id="btn-indice-mobile" type="button" aria-expanded="false" aria-controls="sidebar">☰ Índice</button>
  <span class="subbar-titulo">Guía de Claude Code</span>
</div>

<div class="overlay-mobile" id="overlay-mobile"></div>

<div class="shell">
  <nav class="sidebar" id="sidebar" aria-label="Índice de la guía">
    <div class="sidebar-head">
      <span class="etiqueta">Guía de referencia</span>
      <p class="titulo">Claude Code para equipos de datos</p>
    </div>
%s
  </nav>

  <div class="contenido" id="contenido">
    <header class="guia-hero">
      <p class="eyebrow">Guía de referencia · equipo de datos</p>
      <h1>Claude Code, de la terminal a la BigQuery de todos los días.</h1>
      <p class="lede">Qué es cada pieza, cómo se usa y cuándo conviene, con ejemplos para Python, GCP, BigQuery, dbt y Airflow. Cada capítulo arranca con un resumen <strong>En 30 segundos</strong>: si te alcanza, seguí de largo.</p>
      <ol class="partes-chips" aria-label="Partes de la guía">
        %s
      </ol>
    </header>

    <main class="guia-main">
%s
      <footer class="pie">
        <p>Generada desde <a href="../docs/">docs/</a>, la fuente de verdad del contenido, verificada contra la documentación oficial de Claude Code. Esta página es la versión navegable.</p>
        <p><a href="index.html">Inicio</a> · <a href="32-trucos-claude-code/index.html">32 trucos</a> · <a href="../docs/cheatsheet.md">docs/cheatsheet.md</a> · <a href="../buenas-practicas/README.md">Buenas prácticas</a></p>
      </footer>
    </main>
  </div>
</div>
</body>
</html>
''' % ("\n".join(side), "\n        ".join(chips), "".join(contenido))


def main():
    faltan = [c[2] for _, _, caps in PARTES for c in caps if not os.path.exists(os.path.join(DOCS, c[2]))]
    if faltan:
        sys.exit("Faltan docs: " + ", ".join(faltan))
    salida = pagina()
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(salida)
    print("OK: %s (%d líneas)" % (os.path.relpath(SALIDA, RAIZ), salida.count("\n")))
    for a in AVISOS:
        print("AVISO:", a)


if __name__ == "__main__":
    main()
