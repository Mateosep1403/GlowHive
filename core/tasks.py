"""Tareas asíncronas (Celery + Redis)."""
import csv
import logging
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.db.models import Count
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True,
             retry_kwargs={"max_retries": 4})
def enviar_confirmacion_orden(self, orden_id):
    """Notifica al microservicio Flask. Reintenta con espera creciente si falla."""
    import requests
    from tienda.models import Orden
    from core.infra.notificador_factory import HTTPNotificador

    orden = Orden.objects.select_related("usuario").get(pk=orden_id)
    notificador = HTTPNotificador()
    resp = requests.post(
        notificador.url,
        json={
            "orden_id": orden.id,
            "usuario_nombre": orden.usuario.nombre,
            "total": float(orden.total),
        },
        timeout=5,
    )
    resp.raise_for_status()
    logger.info("Notificación enviada orden #%s: %s", orden.id, resp.json())
    return resp.json()


@shared_task
def generar_reporte_ventas():
    """Reporte CSV de ventas por producto en media/reportes/."""
    from tienda.models import Producto

    filas = (
        Producto.objects.annotate(unidades=Count("ordenes"))
        .values_list("id", "nombre", "stock", "unidades")
        .order_by("-unidades", "id")
    )
    carpeta = Path(settings.MEDIA_ROOT) / "reportes"
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"ventas_{timezone.now():%Y%m%d_%H%M%S}.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["producto_id", "nombre", "stock", "ordenes"])
        w.writerows(filas)
    logger.info("Reporte generado: %s", ruta)
    return str(ruta)