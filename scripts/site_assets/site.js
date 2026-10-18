// Buscador: filtra INDICE (generado por build_site.py) por todas las palabras.
(function () {
  var input = document.getElementById("buscar");
  var lista = document.getElementById("resultados");
  input.addEventListener("input", function () {
    var palabras = input.value.toLowerCase().split(/\s+/).filter(Boolean);
    lista.innerHTML = "";
    if (!palabras.length) return;
    INDICE.forEach(function (p) {
      var texto = p.x.toLowerCase();
      if (!palabras.every(function (w) { return texto.indexOf(w) >= 0; })) return;
      var i = texto.indexOf(palabras[0]);
      var a = document.createElement("a");
      a.href = BASE + p.u;
      a.textContent = p.t;
      var s = document.createElement("small");
      s.textContent = "…" + p.x.slice(Math.max(0, i - 30), i + 60) + "…";
      a.appendChild(s);
      var li = document.createElement("li");
      li.appendChild(a);
      lista.appendChild(li);
    });
  });
})();
