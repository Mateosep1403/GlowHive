from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from tienda.views_web import home, categoria_detalle, producto_detalle, buscar, carrito
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from core.api_estado import EstadoSistemaView, ReporteView, ReporteEstadoView


from core.views import CrearOrdenView
from tienda.views import (
    ProductoListView,
    CategoriaListView,
    ResenaListCreateView,
    DireccionEnvioListCreateView,
)
from core.api_v1 import TasaCambioView, TopSemanaView, salud


def status(request):
    return HttpResponse("""
    <h1>Beauty Commerce — Estado del servidor</h1>
    <p>El servidor de Django está funcionando correctamente.</p>
    <h2>Rutas disponibles</h2>
    <ul>
        <li><a href="/admin/">Panel de administración</a></li>
        <li><a href="/api/productos/">Listar productos (GET)</a></li>
        <li><a href="/api/categorias/">Listar categorías (GET)</a></li>
        <li><a href="/api/resenas/">Listar/crear reseñas (GET/POST)</a></li>
        <li><a href="/api/direcciones/">Listar/crear direcciones (GET/POST)</a></li>
        <li>Crear orden: POST /api/ordenes/crear/</li>
    </ul>
    """)


urlpatterns = [
    path("", home, name="inicio"),
    path("status/", status, name="status"),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="jsi18n"),
    path("api/ordenes/crear/", CrearOrdenView.as_view(), name="crear_orden"),
    path("api/productos/", ProductoListView.as_view(), name="listar_productos"),
    path("api/categorias/", CategoriaListView.as_view(), name="listar_categorias"),
    path("api/resenas/", ResenaListCreateView.as_view(), name="resenas"),
    path("api/direcciones/", DireccionEnvioListCreateView.as_view(), name="direcciones"),
    path("categoria/<int:categoria_id>/", categoria_detalle, name="categoria_detalle"),
    path("producto/<int:producto_id>/", producto_detalle, name="producto_detalle"),
    path("buscar/", buscar, name="buscar"),
    path("carrito/", carrito, name="carrito"),
    path("api/v1/top-semana/", TopSemanaView.as_view(), name="api_top_semana"),
    path("api/v1/salud/", salud, name="api_salud"),
    path("api/v1/tasa-cambio/", TasaCambioView.as_view(), name="api_tasa_cambio"),
    path("api/v1/estado/", EstadoSistemaView.as_view(), name="api_estado"),
    path("api/v1/reportes/", ReporteView.as_view(), name="api_reportes"),
    path("api/v1/reportes/<str:task_id>/", ReporteEstadoView.as_view(), name="api_reporte_estado"),
    path("arquitectura/", TemplateView.as_view(template_name="tienda/arquitectura.html"), name="arquitectura"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)