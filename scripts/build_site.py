#!/usr/bin/env python3
"""Genera site/ (HTML estático) a partir de los .md de la wiki y chequea links.

    python3 scripts/build_site.py           # genera site/
    python3 scripts/build_site.py --check   # solo chequea links; exit 1 si hay rotos

- Fuente: README.md, los .md de la raíz y concepts/, tools/ (ver PAGINAS).
- Una página .html por .md, en la misma ruta (README.md -> index.html).
- El orden del menú sale de los links del README.
- Links a .md -> .html; se chequea que exista el archivo y el ancla (#slug).
- Stdlib, sin CDNs: se abre con doble clic (file://).

Convertidor de Markdown mínimo para el subconjunto que usa la wiki
(encabezados, párrafos, listas anidadas, tablas, código cercado, blockquotes,
código inline, negrita, cursiva, links).
"""

import html
import json
import os
import re
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "site")
EXCLUIDOS = {"CLAUDE.md", "PREGUNTAS.md"}
RE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
RE_FENCE = re.compile(r"^(\s*)(`{3,})\s*([\w+-]*)\s*$")
RE_LI = re.compile(r"^([-*]|\d+\.)\s+(.*)$")


def paginas():
    """Rutas relativas de los .md a publicar."""
    rutas = [f for f in os.listdir(RAIZ) if f.endswith(".md") and f not in EXCLUIDOS]
    for carpeta in ("concepts", "tools"):
        d = os.path.join(RAIZ, carpeta)
        if os.path.isdir(d):
            rutas += ["%s/%s" % (carpeta, f) for f in os.listdir(d) if f.endswith(".md")]
    # sin symlinks: no publicar archivos de fuera del repo
    return sorted(r for r in rutas if not os.path.islink(os.path.join(RAIZ, r)))


PAGINAS = paginas()


def leer(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        return f.read()


def a_html(ruta):
    return "index.html" if ruta == "README.md" else ruta[:-3] + ".html"


def slug(texto):
    """Ancla estilo GitHub: minúsculas, sin puntuación, espacios -> guiones."""
    t = re.sub(r"<[^>]+>|`", "", texto).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t, flags=re.UNICODE)
    return t.replace(" ", "-")


def anclas(ruta):
    return {slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.*)$", leer(ruta), re.M)}


ANCLAS = {r: anclas(r) for r in PAGINAS}
ROTOS = []


# --------------------------------------------------------------------------
# Links e inline
# --------------------------------------------------------------------------

def resolver_link(url, ruta):
    """href para la página generada; registra el link si está roto."""
    m = re.match(r"^([a-zA-Z][\w+.-]*):", url)
    if m:
        if m.group(1).lower() in ("http", "https", "mailto"):
            return url
        ROTOS.append("%s: esquema no permitido %s" % (ruta, url))
        return None
    destino, _, frag = url.partition("#")
    destino = os.path.normpath(os.path.join(os.path.dirname(ruta), destino)) if destino else ruta
    destino = destino.replace(os.sep, "/")
    if os.path.isabs(destino) or destino.startswith(".."):
        ROTOS.append("%s: link fuera del repo %s" % (ruta, url))
        return None
    if destino in ANCLAS:
        if frag and frag not in ANCLAS[destino]:
            ROTOS.append("%s: ancla inexistente %s" % (ruta, url))
        href = os.path.relpath(a_html(destino), os.path.dirname(a_html(ruta)) or ".")
    elif os.path.exists(os.path.join(RAIZ, destino)):
        # archivo del repo que no se publica: link al .md fuera de site/
        href = os.path.relpath(os.path.join("..", destino), os.path.dirname(a_html(ruta)) or ".")
    else:
        ROTOS.append("%s: link roto %s" % (ruta, url))
        return None
    return href.replace(os.sep, "/") + ("#" + frag if frag else "")


def inline(texto, ruta):
    codigos = []

    def guardar_code(m):
        codigos.append("<code>%s</code>" % html.escape(m.group(2)))
        return "\x00%d\x00" % (len(codigos) - 1)

    t = re.sub(r"(`+)(.+?)\1", guardar_code, texto)
    t = html.escape(t, quote=False)

    def link(m):
        etiqueta, url = m.group(1), m.group(2)
        href = resolver_link(html.unescape(url), ruta)
        if href is None:
            return etiqueta
        attrs = ' rel="noopener"' if href.startswith("http") else ""
        return '<a href="%s"%s>%s</a>' % (html.escape(href), attrs, etiqueta)

    t = RE_LINK.sub(link, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: codigos[int(m.group(1))], t)
    return t


# --------------------------------------------------------------------------
# Bloques
# --------------------------------------------------------------------------

def separar_celdas(linea):
    linea = linea.strip().strip("|")
    celdas, actual, en_code = [], "", False
    for ch in linea:
        if ch == "`":
            en_code = not en_code
        if ch == "|" and not en_code:
            celdas.append(actual.strip())
            actual = ""
        else:
            actual += ch
    celdas.append(actual.strip())
    return celdas


def es_inicio_bloque(ln):
    return RE_FENCE.match(ln) or re.match(r"^#{1,6}\s", ln) or ln.lstrip().startswith(("|", ">")) or RE_LI.match(ln)


def bloques(lineas, ruta):
    out = []
    i, n = 0, len(lineas)
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
                cuerpo.append(lineas[i][indent:])
                i += 1
            i += 1
            clase = ' class="lang-%s"' % lang if lang else ""
            out.append("<pre><code%s>%s</code></pre>" % (clase, html.escape("\n".join(cuerpo), quote=False)))
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            nivel = len(m.group(1))
            out.append('<h%d id="%s">%s</h%d>' % (nivel, slug(m.group(2)), inline(m.group(2), ruta), nivel))
            i += 1
            continue

        if ln.lstrip().startswith("|"):
            filas = []
            while i < n and lineas[i].lstrip().startswith("|"):
                filas.append(separar_celdas(lineas[i]))
                i += 1
            cuerpo = [f for f in filas[1:] if not all(re.match(r"^:?-{2,}:?$", c) for c in f)]
            th = "".join("<th>%s</th>" % inline(c, ruta) for c in filas[0])
            trs = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c, ruta) for c in f) for f in cuerpo)
            out.append('<div class="tabla"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, trs))
            continue

        if ln.startswith(">"):
            contenido = []
            while i < n and lineas[i].startswith(">"):
                contenido.append(lineas[i][1:].lstrip())
                i += 1
            out.append("<blockquote>%s</blockquote>" % bloques(contenido, ruta))
            continue

        m = RE_LI.match(ln)
        if m:
            ordenada = m.group(1)[0].isdigit()
            items = []
            while i < n:
                m = RE_LI.match(lineas[i])
                if not m or m.group(1)[0].isdigit() != ordenada:
                    break
                item = [m.group(2)]
                i += 1
                # continuación: líneas indentadas, o en blanco seguidas de indentadas
                while i < n:
                    if lineas[i].startswith("  ") and lineas[i].strip():
                        item.append(lineas[i])
                    elif not lineas[i].strip() and i + 1 < n and lineas[i + 1].startswith("  "):
                        item.append("")
                    else:
                        break
                    i += 1
                items.append(item)
                # una línea en blanco entre ítems no corta la lista
                if i + 1 < n and not lineas[i].strip() and RE_LI.match(lineas[i + 1]):
                    i += 1
            lis = []
            for item in items:
                resto = [re.sub(r"^ {2,4}", "", x) for x in item[1:]]
                primera = [item[0]]
                while resto and resto[0].strip() and not es_inicio_bloque(resto[0]):
                    primera.append(resto.pop(0).strip())
                lis.append("<li>%s%s</li>" % (inline(" ".join(primera), ruta), bloques(resto, ruta)))
            tag = "ol" if ordenada else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join(lis), tag))
            continue

        par = []
        while i < n and lineas[i].strip() and not es_inicio_bloque(lineas[i]):
            par.append(lineas[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(par), ruta))
    return "\n".join(out)


# --------------------------------------------------------------------------
# Páginas
# --------------------------------------------------------------------------

def titulo(ruta):
    m = re.search(r"^#\s+(.*)$", leer(ruta), re.M)
    return re.sub(r"`", "", m.group(1)) if m else ruta


def orden_menu():
    """Páginas en el orden en que las enlaza el README; el resto al final."""
    orden = ["README.md"]
    for _, url in RE_LINK.findall(leer("README.md")):
        destino = url.partition("#")[0]
        if destino in PAGINAS and destino not in orden:
            orden.append(destino)
    return orden + [r for r in PAGINAS if r not in orden]


def menu(actual):
    grupos = {}
    for r in orden_menu():
        grupo = "Conceptos" if r.startswith("concepts/") else "Herramientas" if r.startswith("tools/") else "Wiki"
        grupos.setdefault(grupo, []).append(r)
    out = []
    for grupo in ("Wiki", "Conceptos", "Herramientas"):
        lis = []
        for r in grupos.get(grupo, []):
            href = os.path.relpath(a_html(r), os.path.dirname(a_html(actual)) or ".").replace(os.sep, "/")
            activo = ' aria-current="page"' if r == actual else ""
            lis.append('<li><a href="%s"%s>%s</a></li>' % (href, activo, html.escape(titulo(r))))
        out.append("<h2>%s</h2><ul>%s</ul>" % (grupo, "".join(lis)))
    return "".join(out)


PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titulo)s · Coding agents</title>
<link rel="stylesheet" href="%(base)sassets/site.css">
</head>
<body>
<nav>
<input type="search" id="buscar" placeholder="Buscar…" aria-label="Buscar en la wiki">
<ol id="resultados"></ol>
%(menu)s
</nav>
<main>
%(cuerpo)s
</main>
<script>var BASE = "%(base)s";</script>
<script src="%(base)sassets/indice.js"></script>
<script src="%(base)sassets/site.js"></script>
</body>
</html>
"""


def render(ruta):
    base = "../" * a_html(ruta).count("/")
    return PLANTILLA % {
        "titulo": html.escape(titulo(ruta)),
        "base": base,
        "menu": menu(ruta),
        "cuerpo": bloques(leer(ruta).splitlines(), ruta),
    }


def indice_busqueda():
    """Texto plano de cada página para el buscador del cliente."""
    items = []
    for r in orden_menu():
        texto = re.sub(r"[`*#>|]|\]\([^)]*\)|\[", " ", leer(r))
        items.append({"t": titulo(r), "u": a_html(r), "x": re.sub(r"\s+", " ", texto)})
    return "var INDICE = %s;\n" % json.dumps(items, ensure_ascii=False)


def main():
    solo_chequeo = "--check" in sys.argv
    paginas_html = {r: render(r) for r in PAGINAS}
    for aviso in ROTOS:
        print("✗ " + aviso, file=sys.stderr)
    if solo_chequeo:
        print("%d páginas, %d links rotos" % (len(PAGINAS), len(ROTOS)))
        return 1 if ROTOS else 0
    if os.path.isdir(SALIDA):
        shutil.rmtree(SALIDA)
    shutil.copytree(os.path.join(RAIZ, "scripts", "site_assets"), os.path.join(SALIDA, "assets"))
    for r, contenido in paginas_html.items():
        destino = os.path.join(SALIDA, a_html(r))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(contenido)
    with open(os.path.join(SALIDA, "assets", "indice.js"), "w", encoding="utf-8") as f:
        f.write(indice_busqueda())
    print("site/: %d páginas, %d links rotos" % (len(PAGINAS), len(ROTOS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
