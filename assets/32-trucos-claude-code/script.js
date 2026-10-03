/* Lógica propia de la página de trucos: progreso, filtro por nivel, buscador y
   expandir/colapsar. Tema, copiar código e índice lateral viven en ../js/site.js. */
(function () {
  "use strict";

  var STORAGE_KEY = "claudeTrucosProgreso";
  var TOTAL_TRUCOS = 32;

  var checks = Array.prototype.slice.call(document.querySelectorAll(".ficha-check"));
  var filtroBtns = Array.prototype.slice.call(document.querySelectorAll(".filtro-btn"));
  var buscadorInput = document.getElementById("buscador-input");
  var btnExpandir = document.getElementById("btn-expandir");
  var progresoEl = document.getElementById("progreso-contador");
  var barraEl = document.getElementById("progreso-barra");
  var sinResultados = document.getElementById("sin-resultados");
  var nivelSecciones = Array.prototype.slice.call(document.querySelectorAll(".nivel-seccion"));

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
    if (barraEl) barraEl.style.width = Math.round((marcados / TOTAL_TRUCOS) * 100) + "%";
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
  // Init
  // ------------------------------------------------------------------

  document.addEventListener("DOMContentLoaded", function () {
    inicializarProgreso();
    inicializarFiltros();
    inicializarBuscador();
    inicializarExpandir();
  });
})();
