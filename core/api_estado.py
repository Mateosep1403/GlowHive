"""Endpoints para ver y accionar el sistema distribuido desde el navegador.

  GET  /api/v1/estado/               estado de cada servicio (monolito, microservicio, infraestructura)
  POST /api/v1/reportes/             encola el reporte de ventas en Celery y devuelve el id de la tarea
  GET  /api/v1/reportes/<task_id>/   consulta el estado de la tarea y, si terminó, el enlace de descarga
"""
import os
import time
from pathlib import Path

import requests
from django.conf import settings
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView

from core.infra.servicio_aliado import ServicioAliadoClient
from core.infra.tasa_cambio import crear_conversor


def _medir(fn):
    """Ejecuta fn() y devuelve (estado, detalle, milisegundos). Nunca lanza."""
    inicio = time.perf_counter()
    try:
        estado, detalle = fn()
    except Exception as exc:  # un servicio caído no debe tumbar el panel
        estado, detalle = "caido", str(exc)[:120]
    return estado, detalle, round((time.perf_counter() - inicio) * 1000)


def _servicio(clave, nombre, tipo, fn):
    estado, detalle, ms = _medir(fn)
    return {"clave": clave, "nombre": nombre, "tipo": tipo, "estado": estado, "detalle": detalle, "ms": ms}


def _chequear_django():
    return "ok", "gunicorn / Django"


def _chequear_db():
    with connection.cursor() as c:
        c.execute("SELECT 1")
    return "ok", connection.vendor


def _chequear_redis():
    if not os.environ.get("REDIS_URL"):
        return "no_configurado", "modo local (tareas síncronas)"
    import redis

    redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1).ping()
    return "ok", "broker y resultados de Celery"


def _chequear_celery():
    if not os.environ.get("REDIS_URL"):
        return "no_configurado", "modo local (sin worker)"
    from beautycommerce.celery import app

    workers = app.control.inspect(timeout=1).ping() or {}
    if not workers:
        return "caido", "ningún worker responde"
    return "ok", f"{len(workers)} worker(s)"


def _chequear_flask():
    base = os.environ.get("NOTIFICACIONES_SERVICE_URL", "http://localhost:5000")
    resp = requests.get(f"{base}/api/v2/notificaciones/salud", timeout=2)
    resp.raise_for_status()
    return "ok", "microservicio de notificaciones"


def _chequear_aliado():
    cliente = ServicioAliadoClient()
    if not cliente.url:
        return "no_configurado", "sin ALIADO_API_URL"
    resp = requests.get(cliente.url, timeout=2)
    resp.raise_for_status()
    return "ok", "servicio del equipo aliado"


def _chequear_tasas():
    tasa = crear_conversor().tasa("COP", "USD")
    if tasa is None:
        return "caido", "API de terceros no responde"
    return "ok", f"1 COP = {tasa} USD"


class EstadoSistemaView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        servicios = [
            _servicio("nginx", "Nginx (API Gateway)", "gateway", lambda: ("ok", "recibió esta petición")),
            _servicio("django", "Django (monolito)", "monolito", _chequear_django),
            _servicio("flask", "Flask · notificaciones", "microservicio", _chequear_flask),
            _servicio("db", "Base de datos", "infraestructura", _chequear_db),
            _servicio("redis", "Redis", "infraestructura", _chequear_redis),
            _servicio("celery", "Celery worker", "infraestructura", _chequear_celery),
            _servicio("aliado", "Servicio aliado", "externo", _chequear_aliado),
            _servicio("tasas", "API de tasas de cambio", "externo", _chequear_tasas),
        ]
        return Response({"servicios": servicios})


def _datos_tarea(resultado):
    data = {"task_id": resultado.id, "estado": resultado.state}
    if resultado.state == "SUCCESS":
        nombre = Path(str(resultado.result)).name
        data["archivo"] = nombre
        data["url"] = f"{settings.MEDIA_URL}reportes/{nombre}"
    elif resultado.state == "FAILURE":
        data["error"] = str(resultado.result)[:200]
    return data


class ReporteView(APIView):
    """POST: encola el reporte. Con Redis responde 202 de inmediato y el worker hace el trabajo.
    Sin Redis (modo local) la tarea corre en el momento y la respuesta ya trae el resultado."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        from core.tasks import generar_reporte_ventas

        tarea = generar_reporte_ventas.delay()
        if settings.CELERY_TASK_ALWAYS_EAGER:
            return Response(_datos_tarea(tarea), status=200)
        return Response({"task_id": tarea.id, "estado": tarea.state}, status=202)


class ReporteEstadoView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, task_id):
        from celery.result import AsyncResult

        return Response(_datos_tarea(AsyncResult(task_id)))
