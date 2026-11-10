(function () {
  "use strict";
  var _ = window.gettext || function (s) { return s; };

  var NOMBRES_TIPO = {
    gateway: _("Gateway"), monolito: _("Monolito"), microservicio: _("Microservicio"),
    infraestructura: _("Infraestructura"), externo: _("Externo")
  };
  var NOMBRES_ESTADO = { ok: _("Activo"), caido: _("Caído"), no_configurado: _("No configurado") };

  function el(tag, clase, texto) {
    var nodo = document.createElement(tag);
    if (clase) nodo.className = clase;
    if (texto !== undefined) nodo.textContent = texto;
    return nodo;
  }

  /* ---------- Estado de los servicios ---------- */
  function pintarServicios(servicios) {
    var lista = document.getElementById("lista-servicios");
    lista.innerHTML = "";
    servicios.forEach(function (s) {
      var li = el("li", "servicio servicio-" + s.estado);
      li.appendChild(el("span", "servicio-punto"));
      var cuerpo = el("div", "servicio-cuerpo");
      cuerpo.appendChild(el("strong", "", s.nombre));
      cuerpo.appendChild(el("span", "servicio-detalle", s.detalle));
      li.appendChild(cuerpo);
      var meta = el("div", "servicio-meta");
      meta.appendChild(el("span", "servicio-tipo", NOMBRES_TIPO[s.tipo] || s.tipo));
      meta.appendChild(el("span", "servicio-estado", (NOMBRES_ESTADO[s.estado] || s.estado) + " · " + s.ms + " ms"));
      li.appendChild(meta);
      lista.appendChild(li);
    });
  }

  function cargarEstado() {
    var boton = document.getElementById("btn-estado");
    boton.disabled = true;
    return fetch("/api/v1/estado/", { headers: { Accept: "application/json" } })
      .then(function (r) { return r.json(); })
      .then(function (d) { pintarServicios(d.servicios); })
      .catch(function () {
        var lista = document.getElementById("lista-servicios");
        lista.innerHTML = "";
        lista.appendChild(el("li", "vacio", _("No se pudo consultar el estado de los servicios.")));
      })
      .then(function () { boton.disabled = false; });
  }

  /* ---------- Registro de peticiones ---------- */
  var registro = document.getElementById("registro");
  var hayRegistros = false;

  function anotar(metodo, ruta, estado, servidoPor, ms, extra) {
    if (!hayRegistros) { registro.innerHTML = ""; hayRegistros = true; }
    var li = el("li", "registro-fila " + (estado >= 200 && estado < 400 ? "registro-ok" : "registro-error"));
    li.appendChild(el("code", "", metodo + " " + ruta));
    li.appendChild(el("span", "", estado + " · " + ms + " ms"));
    li.appendChild(el("strong", "registro-servicio", _("Respondió:") + " " + (servidoPor || _("(sin gateway)"))));
    if (extra) li.appendChild(el("span", "registro-extra", extra));
    registro.insertBefore(li, registro.firstChild);
  }

  function pedir(metodo, ruta, cuerpo) {
    var inicio = performance.now();
    var opciones = { method: metodo, headers: { Accept: "application/json" } };
    if (cuerpo) {
      opciones.headers["Content-Type"] = "application/json";
      opciones.body = JSON.stringify(cuerpo);
    }
    return fetch(ruta, opciones).then(function (r) {
      var ms = Math.round(performance.now() - inicio);
      var servidoPor = r.headers.get("X-Servido-Por");
      return r.json().catch(function () { return {}; }).then(function (datos) {
        return { respuesta: r, datos: datos, ms: ms, servidoPor: servidoPor };
      });
    });
  }

  function fallo(metodo, ruta) {
    anotar(metodo, ruta, 0, null, 0, _("No hubo respuesta del servidor."));
  }

  /* ---------- Acciones ---------- */
  function accionTop() {
    var ruta = "/api/v1/top-semana/?limit=3";
    return pedir("GET", ruta).then(function (x) {
      var nombres = (x.datos.items || []).map(function (i) { return i.nombre; }).join(", ");
      anotar("GET", ruta, x.respuesta.status, x.servidoPor, x.ms, nombres);
    }).catch(function () { fallo("GET", ruta); });
  }

  function accionNotificar() {
    var ruta = "/api/v2/notificaciones/confirmar";
    var cuerpo = { orden_id: 0, usuario_nombre: _("Prueba desde el navegador"), total: 1 };
    return pedir("POST", ruta, cuerpo).then(function (x) {
      var extra = x.datos.status ? (x.datos.status + " · " + (x.datos.canal || "")) : (x.datos.error || "");
      anotar("POST", ruta, x.respuesta.status, x.servidoPor, x.ms, extra);
    }).catch(function () { fallo("POST", ruta); });
  }

  function mostrarEnlaceReporte(datos) {
    var enlace = document.getElementById("reporte-enlace");
    enlace.textContent = "";
    var a = el("a", "enlace", datos.archivo);
    a.href = datos.url;
    enlace.appendChild(document.createTextNode(_("Reporte listo:") + " "));
    enlace.appendChild(a);
    enlace.hidden = false;
  }

  function accionReporte() {
    document.getElementById("reporte-enlace").hidden = true;
    return pedir("POST", "/api/v1/reportes/").then(function (x) {
      anotar("POST", "/api/v1/reportes/", x.respuesta.status, x.servidoPor, x.ms,
        _("Tarea encolada en Redis:") + " " + (x.datos.task_id || "") + " · " + (x.datos.estado || ""));
      if (x.datos.estado === "SUCCESS") return mostrarEnlaceReporte(x.datos);
      if (!x.datos.task_id) return;
      return esperarReporte(x.datos.task_id, 0);
    }).catch(function () { fallo("POST", "/api/v1/reportes/"); });
  }

  function esperarReporte(id, intento) {
    var ruta = "/api/v1/reportes/" + id + "/";
    return pedir("GET", ruta).then(function (x) {
      var estado = x.datos.estado;
      anotar("GET", ruta, x.respuesta.status, x.servidoPor, x.ms, _("Estado de la tarea:") + " " + estado);
      if (estado === "SUCCESS") return mostrarEnlaceReporte(x.datos);
      if (estado === "FAILURE") return;
      if (intento < 10) {
        return new Promise(function (ok) { setTimeout(ok, 1000); })
          .then(function () { return esperarReporte(id, intento + 1); });
      }
    }).catch(function () { fallo("GET", ruta); });
  }

  var ACCIONES = { top: accionTop, notificar: accionNotificar, reporte: accionReporte };

  document.querySelectorAll("[data-accion]").forEach(function (boton) {
    boton.addEventListener("click", function () {
      boton.disabled = true;
      ACCIONES[boton.getAttribute("data-accion")]().then(function () { boton.disabled = false; });
    });
  });

  document.getElementById("btn-estado").addEventListener("click", cargarEstado);
  cargarEstado();
})();
