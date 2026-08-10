(function () {
  "use strict";

  var STORAGE_KEY = "claudeTrucosProgreso";
  var TOTAL_TRUCOS = 32;

  var fichas = Array.prototype.slice.call(document.querySelectorAll(".ficha"));
  var checks = Array.prototype.slice.call(document.querySelectorAll(".ficha-check"));
  var filtroBtns = Array.prototype.slice.call(document.querySelectorAll(".filtro-btn"));
  var buscadorInput = document.getElementById("buscador-input");
  var btnExpandir = document.getElementById("btn-expandir");
  var progresoEl = document.getElementById("progreso-contador");
  var sinResultados = document.getElementById("sin-resultados");
  var nivelSecciones = Array.prototype.slice.call(document.querySelectorAll(".nivel-seccion"));
  var indiceLinks = Array.prototype.slice.call(document.querySelectorAll(".indice-link"));
  var sidebar = document.getElementById("sidebar");
  var btnIndiceMobile = document.getElementById("btn-indice-mobile");
  var overlay = document.getElementById("overlay-mobile");

  var estado = {
    nivel: "todos",
    busqueda: ""
  };

  // ------------------------------------------------------------------
  // Progreso (checkboxes + localStorage)
  // ------------------------------------------------------------------

  function cargarProgreso() {
    var raw = null;
    try {
      raw = window.localStorage.getItem(STORAGE_KEY);
    } catch (err) {
      raw = null;
    }
    var ids = [];
    if (raw) {
      try {
        ids = JSON.parse(raw);
      } catch (err) {
        ids = [];
      }
    }
    return Array.isArray(ids) ? ids : [];
  }

  function guardarProgreso(ids) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
    } catch (err) {
      // localStorage no disponible (modo privado, etc.) — se pierde el progreso, no rompemos nada.
    }
  }

  function actualizarContador() {
    var marcados = checks.filter(function (c) {
      return c.checked;
    }).length;
    progresoEl.textContent = marcados + " / " + TOTAL_TRUCOS;
  }

  function inicializarProgreso() {
    var guardados = cargarProgreso();
    checks.forEach(function (check) {
      var id = check.getAttribute("data-truco");
      check.checked = guardados.indexOf(id) !== -1;

      check.addEventListener("click", function (e) {
        e.stopPropagation();
      });

      check.addEventListener("change", function () {
        var actuales = cargarProgreso();
        if (check.checked) {
          if (actuales.indexOf(id) === -1) actuales.push(id);
        } else {
          actuales = actuales.filter(function (x) {
            return x !== id;
          });
        }
        guardarProgreso(actuales);
        actualizarContador();
      });
    });
    actualizarContador();
  }

  // ------------------------------------------------------------------
  // Copiar código
  // ------------------------------------------------------------------

  function inicializarCopiar() {
    var botones = Array.prototype.slice.call(document.querySelectorAll(".btn-copiar"));
    botones.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var bloque = btn.closest(".bloque-codigo");
        var codigo = bloque.querySelector("code");
        var texto = codigo.textContent;

        function marcarCopiado() {
          var original = btn.textContent;
          btn.textContent = "Copiado";
          btn.classList.add("copiado");
          window.setTimeout(function () {
            btn.textContent = original;
            btn.classList.remove("copiado");
          }, 1600);
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(texto).then(marcarCopiado, function () {
            copiarFallback(texto);
            marcarCopiado();
          });
        } else {
          copiarFallback(texto);
          marcarCopiado();
        }
      });
    });
  }

  function copiarFallback(texto) {
    var textarea = document.createElement("textarea");
    textarea.value = texto;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand("copy");
    } catch (err) {
      // sin soporte de copiado; el usuario puede seleccionar el texto a mano.
    }
    document.body.removeChild(textarea);
  }

  // ------------------------------------------------------------------
  // Filtro por nivel + buscador
  // ------------------------------------------------------------------

  function normalizar(str) {
    return str
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  }

  function aplicarFiltros() {
    var query = normalizar(estado.busqueda.trim());
    var totalVisibles = 0;

    nivelSecciones.forEach(function (seccion) {
      var nivelSeccion = seccion.getAttribute("data-nivel");
      var coincideNivel = estado.nivel === "todos" || estado.nivel === nivelSeccion;
      var visiblesEnSeccion = 0;

      var fichasSeccion = Array.prototype.slice.call(seccion.querySelectorAll(".ficha"));
      fichasSeccion.forEach(function (ficha) {
        var texto = normalizar(ficha.textContent);
        var coincideBusqueda = query === "" || texto.indexOf(query) !== -1;
        var visible = coincideNivel && coincideBusqueda;
        ficha.style.display = visible ? "" : "none";
        if (visible) {
          visiblesEnSeccion++;
          totalVisibles++;
        }
      });

      seccion.style.display = coincideNivel && visiblesEnSeccion > 0 ? "" : "none";
    });

    sinResultados.style.display = totalVisibles === 0 ? "block" : "none";
  }

  function inicializarFiltros() {
    filtroBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        filtroBtns.forEach(function (b) {
          b.setAttribute("aria-pressed", "false");
        });
        btn.setAttribute("aria-pressed", "true");
        estado.nivel = btn.getAttribute("data-filtro");
        aplicarFiltros();
      });
    });
  }

  function inicializarBuscador() {
    buscadorInput.addEventListener("input", function () {
      estado.busqueda = buscadorInput.value;
      aplicarFiltros();
    });
  }

  // ------------------------------------------------------------------
  // Expandir / colapsar todo
  // ------------------------------------------------------------------

  function inicializarExpandir() {
    var expandido = false;
    btnExpandir.addEventListener("click", function () {
      expandido = !expandido;
      var cajas = Array.prototype.slice.call(document.querySelectorAll(".ficha-caja"));
      cajas.forEach(function (caja) {
        caja.open = expandido;
      });
      btnExpandir.textContent = expandido ? "Colapsar todo" : "Expandir todo";
    });
  }

  // ------------------------------------------------------------------
  // Índice lateral: resaltado activo al scrollear
  // ------------------------------------------------------------------

  function inicializarScrollSpy() {
    if (!("IntersectionObserver" in window)) return;

    var mapa = {};
    indiceLinks.forEach(function (link) {
      var id = link.getAttribute("href").replace("#", "");
      mapa[id] = link;
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var link = mapa[entry.target.id];
          if (!link) return;
          if (entry.isIntersecting) {
            indiceLinks.forEach(function (l) {
              l.classList.remove("activo");
            });
            link.classList.add("activo");
          }
        });
      },
      {
        rootMargin: "-15% 0px -70% 0px",
        threshold: 0
      }
    );

    fichas.forEach(function (ficha) {
      var caja = ficha.querySelector(".ficha-caja");
      if (caja && caja.id) observer.observe(caja);
    });
  }

  // ------------------------------------------------------------------
  // Índice lateral en mobile
  // ------------------------------------------------------------------

  function inicializarIndiceMobile() {
    if (!btnIndiceMobile) return;

    function abrir() {
      sidebar.classList.add("abierto");
      overlay.classList.add("visible");
      btnIndiceMobile.setAttribute("aria-expanded", "true");
    }

    function cerrar() {
      sidebar.classList.remove("abierto");
      overlay.classList.remove("visible");
      btnIndiceMobile.setAttribute("aria-expanded", "false");
    }

    btnIndiceMobile.addEventListener("click", function () {
      if (sidebar.classList.contains("abierto")) {
        cerrar();
      } else {
        abrir();
      }
    });

    overlay.addEventListener("click", cerrar);

    indiceLinks.forEach(function (link) {
      link.addEventListener("click", cerrar);
    });
  }

  // ------------------------------------------------------------------
  // Init
  // ------------------------------------------------------------------

  document.addEventListener("DOMContentLoaded", function () {
    inicializarProgreso();
    inicializarCopiar();
    inicializarFiltros();
    inicializarBuscador();
    inicializarExpandir();
    inicializarScrollSpy();
    inicializarIndiceMobile();
  });
})();
