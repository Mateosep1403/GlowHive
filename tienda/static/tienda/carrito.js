/* Carrito de GlowHive.
 * Vive en el navegador (localStorage) y, al confirmar, usa la API que ya existía:
 * POST /api/ordenes/crear/ con { usuario_id, productos_ids }.
 * La orden no maneja cantidades, así que cada producto se agrega una sola vez. */
(function () {
  "use strict";

  // Traducciones: gettext/ngettext/interpolate vienen de /jsi18n/ (catálogo djangojs).
  var _ = window.gettext || function (s) { return s; };
  var _n = window.ngettext || function (s, p, n) { return n === 1 ? s : p; };
  var _f = window.interpolate || function (f, o) { return f.replace(/%\((\w+)\)s/g, function (m, k) { return o[k]; }); };

  var CLAVE = "glowhive_carrito";
  var memoria = [];

  function cop(n) {
    return "$" + Math.round(Number(n) || 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  function leer() {
    try {
      var datos = JSON.parse(window.localStorage.getItem(CLAVE));
      return Array.isArray(datos) ? datos : [];
    } catch (e) {
      return memoria.slice();
    }
  }

  function guardar(items) {
    memoria = items.slice();
    try { window.localStorage.setItem(CLAVE, JSON.stringify(items)); } catch (e) { /* sin almacenamiento: queda en memoria */ }
    actualizar();
  }

  function estaEnCarrito(id) {
    return leer().some(function (p) { return String(p.id) === String(id); });
  }

  function quitar(id) {
    guardar(leer().filter(function (p) { return String(p.id) !== String(id); }));
  }

  function alternar(boton) {
    var id = boton.getAttribute("data-id");
    if (estaEnCarrito(id)) { quitar(id); return; }
    var items = leer();
    items.push({
      id: Number(id),
      nombre: boton.getAttribute("data-nombre"),
      precio: Number(boton.getAttribute("data-precio")),
      imagen: boton.getAttribute("data-imagen") || "",
      url: boton.getAttribute("data-url") || ""
    });
    guardar(items);
  }

  function el(etiqueta, clase, texto) {
    var nodo = document.createElement(etiqueta);
    if (clase) nodo.className = clase;
    if (texto !== undefined) nodo.textContent = texto;
    return nodo;
  }

  /* ---------- Botones "Agregar" y contador del encabezado ---------- */

  function actualizar() {
    var items = leer();

    document.querySelectorAll("[data-carrito-cuenta]").forEach(function (nodo) {
      nodo.textContent = items.length;
      nodo.setAttribute("data-vacio", items.length === 0 ? "true" : "false");
    });

    document.querySelectorAll(".btn-agregar[data-id]").forEach(function (boton) {
      if (boton.disabled) return; // producto agotado: conserva su texto
      var dentro = estaEnCarrito(boton.getAttribute("data-id"));
      var nombre = boton.getAttribute("data-nombre") || "";
      boton.setAttribute("aria-pressed", dentro ? "true" : "false");
      boton.setAttribute("aria-label", _f(dentro ? _("Quitar %(nombre)s del carrito") : _("Agregar %(nombre)s al carrito"), { nombre: nombre }, true));
      boton.textContent = dentro ? _("En el carrito") : (boton.getAttribute("data-texto") || _("Agregar"));
      boton.title = dentro ? _("Quitar del carrito") : "";
    });

    pintarCarrito();
  }

  document.addEventListener("click", function (evento) {
    var boton = evento.target.closest(".btn-agregar[data-id]");
    if (boton && !boton.disabled) { alternar(boton); }
  });

  /* ---------- Página del carrito ---------- */

  function crearLinea(item) {
    var li = el("li", "linea-carrito");

    var foto = el("div", "foto tono-" + (Number(item.id) % 5));
    if (item.imagen) {
      var img = document.createElement("img");
      img.src = item.imagen;
      img.alt = "";
      foto.appendChild(img);
    } else {
      foto.appendChild(el("span", "foto-inicial", (item.nombre || "G").charAt(0).toUpperCase()));
    }
    foto.setAttribute("aria-hidden", "true");

    var info = el("div");
    var nombre = el("a", "linea-nombre", item.nombre);
    if (item.url) nombre.href = item.url;
    info.appendChild(nombre);
    info.appendChild(el("p", "linea-precio", cop(item.precio)));
    var quitarBtn = el("button", "btn-quitar", _("Quitar"));
    quitarBtn.type = "button";
    quitarBtn.setAttribute("aria-label", _f(_("Quitar %(nombre)s del carrito"), { nombre: item.nombre }, true));
    quitarBtn.addEventListener("click", function () { quitar(item.id); });
    info.appendChild(quitarBtn);

    li.appendChild(foto);
    li.appendChild(info);
    li.appendChild(el("strong", "", cop(item.precio)));
    return li;
  }

  function pintarCarrito() {
    var contenido = document.getElementById("carrito-contenido");
    if (!contenido) return;

    var vacio = document.getElementById("carrito-vacio");
    var confirmacion = document.getElementById("carrito-confirmacion");
    if (!confirmacion.hidden) return; // ya se confirmó la compra: no repintar

    var items = leer();
    var lista = document.getElementById("carrito-lista");
    lista.textContent = "";
    items.forEach(function (item) { lista.appendChild(crearLinea(item)); });

    var total = items.reduce(function (suma, p) { return suma + (Number(p.precio) || 0); }, 0);
    document.getElementById("carrito-total").textContent = cop(total);
    document.getElementById("carrito-cantidad").textContent =
      _f(_n("%(n)s producto", "%(n)s productos", items.length), { n: items.length }, true);

    contenido.hidden = items.length === 0;
    vacio.hidden = items.length !== 0;
  }

  function mostrarMensaje(texto, esError) {
    var caja = document.getElementById("carrito-mensaje");
    caja.textContent = texto;
    caja.className = "mensaje" + (esError ? " mensaje-error" : "");
    caja.hidden = !texto;
  }

  function textoDeError(datos) {
    if (!datos) return _("No pudimos crear la orden. Intenta de nuevo en unos minutos.");
    if (typeof datos.detail === "string") return datos.detail;
    var partes = [];
    Object.keys(datos).forEach(function (campo) {
      var valor = datos[campo];
      partes.push(Array.isArray(valor) ? valor.join(" ") : String(valor));
    });
    return partes.join(" ") || _("No pudimos crear la orden. Intenta de nuevo en unos minutos.");
  }

  function confirmarCompra(evento) {
    evento.preventDefault();
    var items = leer();
    var usuario = document.getElementById("usuario");
    var boton = document.getElementById("btn-confirmar");

    if (!usuario.value) {
      mostrarMensaje(_("Elige quién hace la compra para continuar."), true);
      usuario.focus();
      return;
    }
    if (items.length === 0) return;

    mostrarMensaje("", false);
    boton.disabled = true;
    boton.textContent = _("Creando tu orden…");

    fetch("/api/ordenes/crear/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        usuario_id: Number(usuario.value),
        productos_ids: items.map(function (p) { return p.id; })
      })
    })
      .then(function (respuesta) {
        return respuesta.json().catch(function () { return null; }).then(function (datos) {
          return { ok: respuesta.ok, datos: datos };
        });
      })
      .then(function (resultado) {
        if (!resultado.ok) {
          mostrarMensaje(textoDeError(resultado.datos), true);
          return;
        }
        var orden = resultado.datos;
        document.getElementById("confirmacion-numero").textContent = "#" + orden.id;
        document.getElementById("confirmacion-total").textContent = cop(orden.total);
        document.getElementById("carrito-contenido").hidden = true;
        document.getElementById("carrito-vacio").hidden = true;
        document.getElementById("carrito-confirmacion").hidden = false;
        guardar([]);
        document.getElementById("confirmacion-titulo").focus();
      })
      .catch(function () {
        mostrarMensaje(_("No pudimos conectar con la tienda. Revisa tu conexión e intenta de nuevo."), true);
      })
      .then(function () {
        boton.disabled = false;
        boton.textContent = _("Confirmar compra");
      });
  }

  var formulario = document.getElementById("form-compra");
  if (formulario) formulario.addEventListener("submit", confirmarCompra);

  actualizar();
  window.addEventListener("storage", actualizar);
})();