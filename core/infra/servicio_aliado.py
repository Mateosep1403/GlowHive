"""Cliente del servicio del equipo aliado.

Variables de entorno:
  ALIADO_API_URL      URL completa del endpoint JSON del aliado (vacío = desactivado)
  ALIADO_API_TIMEOUT  segundos de espera (por defecto 3)

Acepta una lista de objetos, o un objeto que traiga la lista en
items / results / data / productos / products, y mapea los campos
más comunes a: nombre, descripcion, imagen, url, precio.
"""
import logging
import os

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

_CLAVES_LISTA = ("items", "results", "data", "productos", "products")


def _primero(d, *claves):
    for c in claves:
        if d.get(c) not in (None, ""):
            return d[c]
    return None


def normalizar(payload):
    if isinstance(payload, dict):
        for c in _CLAVES_LISTA:
            if isinstance(payload.get(c), list):
                payload = payload[c]
                break
    if not isinstance(payload, list):
        return []
    items = []
    for raw in payload:
        if not isinstance(raw, dict):
            continue
        nombre = _primero(raw, "nombre", "name", "title", "titulo")
        if not nombre:
            continue
        items.append({
            "nombre": str(nombre),
            "descripcion": _primero(raw, "descripcion", "description", "resumen") or "",
            "imagen": _primero(raw, "imagen", "image", "image_url", "foto", "thumbnail") or "",
            "url": _primero(raw, "url", "link", "enlace") or "",
            "precio": _primero(raw, "precio", "price"),
        })
    return items


class ServicioAliadoClient:
    CACHE_KEY = "aliado:items"
    TTL = 60  # segundos en caché

    def __init__(self, url=None, timeout=None):
        self.url = url if url is not None else os.environ.get("ALIADO_API_URL", "")
        self.timeout = timeout or float(os.environ.get("ALIADO_API_TIMEOUT", "3"))

    def listar(self, limite=6):
        if not self.url:
            return []
        cacheado = cache.get(self.CACHE_KEY)
        if cacheado is not None:
            return cacheado[:limite]
        try:
            resp = requests.get(self.url, timeout=self.timeout)
            resp.raise_for_status()
            items = normalizar(resp.json())
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Servicio aliado no disponible: %s", exc)
            return []
        cache.set(self.CACHE_KEY, items, self.TTL)
        return items[:limite]