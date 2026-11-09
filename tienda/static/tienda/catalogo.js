/* Filtros por categoría y orden de las rejillas de productos.
 * Trabaja sobre los datos que ya vienen en cada tarjeta (data-*), sin pedir nada al servidor. */
(function () {
  "use strict";

  var rejilla = document.querySelector("[data-rejilla]");
  if (!rejilla) return;

  var tarjetas = Array.prototype.slice.call(rejilla.querySelectorAll(".tarjeta"));
  tarjetas.forEach(function (t, i) { t.setAttribute("data-posicion", i); });

  var conteo = document.getElementById("conteo");
  var aviso = document.getElementById("sin-resultados");
  var categoriaActiva = "";

  function numero(nodo, atributo) {
    var valor = parseFloat(nodo.getAttribute(atributo));
    return isNaN(valor) ? 0 : valor;
  }

  function aplicar() {
    var visibles = 0;
    tarjetas.forEach(function (t) {
      var coincide = !categoriaActiva || t.getAttribute("data-categoria") === categoriaActiva;
      t.hidden = !coincide;
      if (coincide) visibles += 1;
    });
    if (conteo) conteo.textContent = visibles === 1 ? "1 producto" : visibles + " productos";
    if (aviso) aviso.hidden = visibles !== 0;
  }

  document.querySelectorAll("[data-filtro]").forEach(function (chip) {
    chip.addEventListener("click", function () {
      categoriaActiva = chip.getAttribute("data-filtro");
      document.querySelectorAll("[data-filtro]").forEach(function (otro) {
        otro.setAttribute("aria-pressed", otro === chip ? "true" : "false");
      });
      aplicar();
    });
  });

  var orden = document.getElementById("orden");
  if (orden) {
    orden.addEventListener("change", function () {
      var criterio = orden.value;
      var copia = tarjetas.slice();
      copia.sort(function (a, b) {
        if (criterio === "precio-asc") return numero(a, "data-precio") - numero(b, "data-precio");
        if (criterio === "precio-desc") return numero(b, "data-precio") - numero(a, "data-precio");
        if (criterio === "calificacion") return numero(b, "data-calificacion") - numero(a, "data-calificacion");
        return numero(a, "data-posicion") - numero(b, "data-posicion");
      });
      copia.forEach(function (t) { rejilla.appendChild(t); });
    });
  }

  aplicar();
})();
