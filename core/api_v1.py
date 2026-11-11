from django.db import connection
from django.http import JsonResponse
from django.utils.translation import gettext as _
from rest_framework.views import APIView
from rest_framework.response import Response
from core.infra.tasa_cambio import crear_conversor

from core.ranking import productos_con_ranking, mejor_resena
from tienda.models import Producto


class TopSemanaView(APIView):
    """GET /api/v1/top-semana/?limit=10"""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            limite = max(1, min(int(request.query_params.get("limit", 10)), 50))
        except ValueError:
            return Response({"error": _("El parámetro limit debe ser un número entero.")}, status=400)

        productos = list(
            productos_con_ranking(Producto.objects.select_related("marca", "categoria"))[:limite]
        )
        items = []
        for posicion, p in enumerate(productos, start=1):
            resena = mejor_resena(p)
            items.append({
                "posicion": posicion,
                "id": p.id,
                "nombre": p.nombre,
                "precio": float(p.precio),
                "marca": p.marca.nombre if p.marca_id else None,
                "categoria": p.categoria.nombre if p.categoria_id else None,
                "imagen": request.build_absolute_uri(p.imagen.url) if p.imagen else None,
                "rating_promedio": round(p.rating_promedio, 2) if p.rating_promedio else None,
                "total_resenas": p.total_resenas,
                "resenas_creadoras": p.resenas_creadoras,
                "mejor_resena": resena.comentario if resena else None,
            })
        return Response({"total": len(items), "items": items})

class TasaCambioView(APIView):
    """GET /api/v1/tasa-cambio/?monto=45000"""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            monto = float(request.query_params.get("monto", 1))
        except ValueError:
            return Response({"error": _("El parámetro monto debe ser numérico.")}, status=400)
        convertido = crear_conversor().convertir(monto, "COP", "USD")
        if convertido is None:
            return Response({"error": _("Servicio de tasas no disponible.")}, status=503)
        return Response({"monto_cop": monto, "monto_usd": float(convertido)})

def salud(request):
    """Health check para Docker y Nginx."""
    try:
        with connection.cursor() as c:
            c.execute("SELECT 1")
        return JsonResponse({"estado": "ok", "db": "ok"})
    except Exception:
        return JsonResponse({"estado": "degradado", "db": "error"}, status=503)