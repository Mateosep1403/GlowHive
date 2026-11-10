"""Adapter para una API de terceros (tasas de cambio).

Inversión de dependencias:
  * ProveedorTasaCambio: abstracción que conoce el servicio.
  * ExchangeRateApiAdapter: adapta open.er-api.com a esa interfaz.
  * TasaFijaAdapter: doble para pruebas / modo sin internet.
ConversorMoneda solo depende de la abstracción.
"""
import logging
import os
from decimal import Decimal

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)


class TasaCambioNoDisponible(Exception):
    """El proveedor externo no pudo entregar una tasa."""


class ProveedorTasaCambio:
    def obtener_tasa(self, origen: str, destino: str) -> Decimal:
        raise NotImplementedError


class ExchangeRateApiAdapter(ProveedorTasaCambio):
    def __init__(self, base_url=None, timeout=3):
        self.base_url = base_url or os.environ.get(
            "TASA_CAMBIO_URL", "https://open.er-api.com/v6/latest"
        )
        self.timeout = timeout

    def obtener_tasa(self, origen, destino):
        try:
            resp = requests.get(f"{self.base_url}/{origen}", timeout=self.timeout)
            resp.raise_for_status()
            return Decimal(str(resp.json()["rates"][destino]))
        except (requests.RequestException, KeyError, ValueError) as exc:
            raise TasaCambioNoDisponible(str(exc)) from exc


class TasaFijaAdapter(ProveedorTasaCambio):
    def __init__(self, tasas=None):
        self.tasas = tasas or {("COP", "USD"): Decimal("0.00025")}

    def obtener_tasa(self, origen, destino):
        try:
            return self.tasas[(origen, destino)]
        except KeyError as exc:
            raise TasaCambioNoDisponible(f"{origen}->{destino}") from exc


class ConversorMoneda:
    TTL = 3600  # la tasa se guarda 1 hora en caché

    def __init__(self, proveedor: ProveedorTasaCambio):
        self.proveedor = proveedor

    def tasa(self, origen="COP", destino="USD"):
        clave = f"tasa:{origen}:{destino}"
        valor = cache.get(clave)
        if valor is not None:
            return Decimal(valor)
        try:
            tasa = self.proveedor.obtener_tasa(origen, destino)
        except TasaCambioNoDisponible as exc:
            logger.warning("Tasa de cambio no disponible: %s", exc)
            return None
        cache.set(clave, str(tasa), self.TTL)
        return tasa

    def convertir(self, monto, origen="COP", destino="USD"):
        tasa = self.tasa(origen, destino)
        if tasa is None:
            return None
        return (Decimal(str(monto)) * tasa).quantize(Decimal("0.01"))


def crear_conversor():
    """Fábrica: el proveedor se elige por variable de entorno."""
    modo = os.environ.get("TASA_CAMBIO_PROVIDER", "real").lower()
    proveedor = TasaFijaAdapter() if modo == "fija" else ExchangeRateApiAdapter()
    return ConversorMoneda(proveedor)