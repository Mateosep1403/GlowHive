"""Ayudas de presentación para las plantillas.

Solo formatean datos para mostrarlos; no contienen reglas de negocio.
"""
import re
from decimal import Decimal, InvalidOperation

from django import template

from tienda.models import Categoria

register = template.Library()

_TIKTOK_VIDEO_ID = re.compile(r"/video/(\d+)")
_TIKTOK_USUARIO = re.compile(r"tiktok\.com/(@[\w.\-]+)")


@register.filter
def cop(valor):
    """45000.00 -> $45.000 (pesos colombianos, sin decimales)."""
    try:
        entero = int(Decimal(str(valor)).quantize(Decimal("1")))
    except (InvalidOperation, TypeError, ValueError):
        return ""
    return "$" + f"{entero:,}".replace(",", ".")


@register.filter
def tono(producto_id, cantidad=5):
    """Número de 0 a cantidad-1 para variar el color del fondo cuando no hay foto."""
    try:
        return int(producto_id) % int(cantidad)
    except (TypeError, ValueError):
        return 0


@register.filter
def inicial(texto):
    texto = (texto or "").strip()
    return texto[:1].upper() if texto else "G"


@register.filter
def pct(calificacion):
    """Calificación de 0 a 5 -> porcentaje de estrellas llenas (0 a 100)."""
    try:
        return round(float(calificacion) * 20)
    except (TypeError, ValueError):
        return 0


@register.filter
def tiktok_id(url):
    """Id numérico del video si el enlace es de la forma .../@usuario/video/123."""
    coincidencia = _TIKTOK_VIDEO_ID.search(url or "")
    return coincidencia.group(1) if coincidencia else ""


@register.filter
def tiktok_usuario(url):
    """@usuario del enlace de TikTok, o cadena vacía si no se puede leer."""
    coincidencia = _TIKTOK_USUARIO.search(url or "")
    return coincidencia.group(1) if coincidencia else ""


@register.inclusion_tag("tienda/_nav_categorias.html", takes_context=True)
def nav_categorias(context):
    request = context.get("request")
    return {
        "categorias": Categoria.objects.all(),
        "ruta": request.path if request else "",
    }
