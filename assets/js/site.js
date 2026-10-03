/* ==========================================================================
   Comportamiento compartido de las páginas de assets/.
   Se carga en <head> SIN defer: aplica el tema antes de pintar (evita parpadeo)
   y registra el resto al terminar de cargar el DOM.
   - Tema claro/oscuro (toggle + localStorage, respeta prefers-color-scheme)
   - Botón "Copiar" en bloques de código
   - Índice lateral: abrir/cerrar en mobile + resaltado de la sección visible
   Funciona con file:// (sin módulos, sin fetch, sin dependencias).
   ========================================================================== */
(function () {
  "use strict";

  var THEME_KEY = "claudioTema";
  var root = document.documentElement;

  function leerTema() {
    try { return window.localStorage.getItem(THEME_KEY); } catch (e) { return null; }
  }
  function guardarTema(valor) {
    try { window.localStorage.setItem(THEME_KEY, valor); } catch (e) { /* sin storage: no persiste */ }
  }

  // 1) Aplicar tema guardado lo antes posible
  var guardado = leerTema();
  if (guardado === "light" || guardado === "dark") {
    root.setAttribute("data-theme", guardado);
  }

  function temaActual() {
    var attr = root.getAttribute("data-theme");
    if (attr === "light" || attr === "dark") return attr;
    var prefiereClaro = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches;
    return prefiereClaro ? "light" : "dark";
  }

  function pintarToggle(btn) {
    var actual = temaActual();
    var siguiente = actual === "dark" ? "claro" : "oscuro";
    btn.textContent = actual === "dark" ? "☀" : "☾";
    btn.setAttribute("aria-label", "Cambiar a tema " + siguiente);
    btn.setAttribute("title", "Cambiar a tema " + siguiente);
  }

  function initTema() {
    var btns = Array.prototype.slice.call(document.querySelectorAll(".theme-toggle"));
    btns.forEach(function (btn) {
      pintarToggle(btn);
      btn.addEventListener("click", function () {
        var nuevo = temaActual() === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", nuevo);
        guardarTema(nuevo);
        btns.forEach(pintarToggle);
      });
    });
    if (window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: light)");
      var alCambiar = function () { btns.forEach(pintarToggle); };
      if (mq.addEventListener) mq.addEventListener("change", alCambiar);
      else if (mq.addListener) mq.addListener(alCambiar);
    }
  }

  // 2) Copiar código
  function copiarFallback(texto) {
    var ta = document.createElement("textarea");
    ta.value = texto;
    ta.setAttribute("readonly", "");
    ta.style.position = "absolute";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) { /* el usuario puede seleccionar a mano */ }
    document.body.removeChild(ta);
  }

  function initCopiar() {
    // Envuelve los <pre> sueltos de .prosa en un .bloque-codigo con botón
    Array.prototype.slice.call(document.querySelectorAll(".prosa pre")).forEach(function (pre) {
      if (pre.parentElement && pre.parentElement.classList.contains("bloque-codigo")) return;
      var wrap = document.createElement("div");
      wrap.className = "bloque-codigo";
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);
    });
    Array.prototype.slice.call(document.querySelectorAll(".bloque-codigo")).forEach(function (bloque) {
      if (!bloque.querySelector(".btn-copiar")) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "btn-copiar";
        b.textContent = "Copiar";
        bloque.insertBefore(b, bloque.firstChild);
      }
    });

    document.addEventListener("click", function (ev) {
      var btn = ev.target.closest ? ev.target.closest(".btn-copiar") : null;
      if (!btn) return;
      var bloque = btn.closest(".bloque-codigo");
      var code = bloque && (bloque.querySelector("code") || bloque.querySelector("pre"));
      if (!code) return;
      var texto = code.textContent;

      function marcar() {
        btn.textContent = "Copiado";
        btn.classList.add("copiado");
        window.setTimeout(function () {
          btn.textContent = "Copiar";
          btn.classList.remove("copiado");
        }, 1600);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(texto).then(marcar, function () { copiarFallback(texto); marcar(); });
      } else {
        copiarFallback(texto);
        marcar();
      }
    });
  }

  // 3) Índice lateral: mobile + scrollspy
  function initIndice() {
    var sidebar = document.getElementById("sidebar");
    var btn = document.getElementById("btn-indice-mobile");
    var overlay = document.getElementById("overlay-mobile");
    var links = Array.prototype.slice.call(document.querySelectorAll(".indice-link"));

    if (sidebar && btn) {
      var abrir = function () {
        sidebar.classList.add("abierto");
        if (overlay) overlay.classList.add("visible");
        btn.setAttribute("aria-expanded", "true");
      };
      var cerrar = function () {
        sidebar.classList.remove("abierto");
        if (overlay) overlay.classList.remove("visible");
        btn.setAttribute("aria-expanded", "false");
      };
      btn.addEventListener("click", function () {
        if (sidebar.classList.contains("abierto")) cerrar(); else abrir();
      });
      if (overlay) overlay.addEventListener("click", cerrar);
      links.forEach(function (l) { l.addEventListener("click", cerrar); });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && sidebar.classList.contains("abierto")) { cerrar(); btn.focus(); }
      });
    }

    // Scrollspy: marca como activo el último objetivo cuyo borde superior
    // ya pasó una línea a ~25% de la altura de la ventana.
    if (!links.length) return;
    var pares = [];
    links.forEach(function (l) {
      var id = (l.getAttribute("href") || "").replace(/^#/, "");
      var el = id && document.getElementById(id);
      if (el) pares.push({ link: l, el: el });
    });
    if (!pares.length) return;
    var actual = null;
    var pendiente = false;
    function marcar() {
      pendiente = false;
      var linea = window.innerHeight * 0.25 + 56;
      var elegido = null;
      for (var i = 0; i < pares.length; i++) {
        if (pares[i].el.offsetParent === null) continue; // oculto por un filtro
        if (pares[i].el.getBoundingClientRect().top <= linea) elegido = pares[i];
        else break;
      }
      if (!elegido) elegido = pares[0];
      if (elegido === actual) return;
      if (actual) { actual.link.classList.remove("activo"); actual.link.removeAttribute("aria-current"); }
      elegido.link.classList.add("activo");
      elegido.link.setAttribute("aria-current", "location");
      actual = elegido;
    }
    window.addEventListener("scroll", function () {
      if (!pendiente) { pendiente = true; window.requestAnimationFrame(marcar); }
    }, { passive: true });
    window.addEventListener("resize", marcar);
    marcar();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTema();
    initCopiar();
    initIndice();
  });
})();
