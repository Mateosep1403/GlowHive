from django.shortcuts import render, get_object_or_404

from core.infra.tasa_cambio import crear_conversor
from tienda.models import Categoria, Producto
from core.ranking import (
    productos_con_ranking as _productos_con_ranking,
    mejor_resena as _mejor_resena,
)
def home(request):
    categorias = Categoria.objects.all()
    panels = []
    for categoria in categorias:
        productos = (
            Producto.objects.filter(categoria=categoria)
            .annotate(
                rating_promedio=Avg("resenas__calificacion"),
                total_resenas=Count("resenas"),
                resenas_creadoras=Count(
                    Case(When(resenas__es_creadora=True, then=1), output_field=IntegerField())
                ),
            )
            .order_by("-resenas_creadoras", "-rating_promedio")[:4]
        )
        panels.append({"categoria": categoria, "productos": productos})
    return render(request, "tienda/home.html", {"panels": panels})

from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count, Case, When, IntegerField

from tienda.models import Categoria, Producto


def _productos_con_ranking(queryset):
    return (
        queryset.annotate(
            rating_promedio=Avg("resenas__calificacion"),
            total_resenas=Count("resenas"),
            resenas_creadoras=Count(
                Case(When(resenas__es_creadora=True, then=1), output_field=IntegerField())
            ),
        ).order_by("-resenas_creadoras", "-rating_promedio", "-total_resenas")
    )


def _mejor_resena(producto):
    return (
        producto.resenas.exclude(comentario="")
        .order_by("-es_creadora", "-calificacion")
        .first()
    )


def home(request):
    categorias = Categoria.objects.all()

    top_productos = list(_productos_con_ranking(Producto.objects.all())[:10])
    for producto in top_productos:
        producto.mejor_resena = _mejor_resena(producto)

    # Nuevo: catálogo completo para la home (el Top 10 de arriba no cambia).
    productos = list(_productos_con_ranking(Producto.objects.all()))
    for producto in productos:
        producto.mejor_resena = _mejor_resena(producto)

    return render(request, "tienda/home.html", {
        "categorias": categorias,
        "top_productos": top_productos,
        "productos": productos,
    })


def categoria_detalle(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    productos = list(_productos_con_ranking(Producto.objects.filter(categoria=categoria)))
    for producto in productos:
        producto.mejor_resena = _mejor_resena(producto)

    return render(request, "tienda/categoria.html", {
        "categoria": categoria,
        "productos": productos,
    })


# ---------------------------------------------------------------------------
# Vistas nuevas de la interfaz (solo lectura; no tocan la lógica de negocio)
# ---------------------------------------------------------------------------

from collections import Counter

from django.db.models import Q

from tienda.models import Usuario


def producto_detalle(request, producto_id):
    queryset = _productos_con_ranking(Producto.objects.select_related("marca", "categoria"))
    producto = get_object_or_404(queryset, id=producto_id)

    resenas = list(
        producto.resenas.select_related("usuario").order_by("-es_creadora", "-calificacion", "-fecha")
    )
    conteos = Counter(r.calificacion for r in resenas)
    distribucion = [
        {
            "estrellas": n,
            "total": conteos.get(n, 0),
            "pct": round(conteos.get(n, 0) * 100 / len(resenas)) if resenas else 0,
        }
        for n in (5, 4, 3, 2, 1)
    ]
    mejor_resena = next((r for r in resenas if r.comentario), None)

    relacionados = []
    if producto.categoria_id:
        relacionados = list(
            _productos_con_ranking(
                Producto.objects.filter(categoria_id=producto.categoria_id).exclude(id=producto.id)
            )[:4]
        )
        for relacionado in relacionados:
            relacionado.mejor_resena = _mejor_resena(relacionado)

    return render(request, "tienda/producto.html", {
        "producto": producto,
        "resenas": resenas,
        "distribucion": distribucion,
        "mejor_resena": mejor_resena,
        "relacionados": relacionados,
        "precio_usd": crear_conversor().convertir(producto.precio, "COP", "USD"),
    })


def buscar(request):
    q = request.GET.get("q", "").strip()
    productos = []
    if q:
        filtro = (
            Q(nombre__icontains=q)
            | Q(marca__nombre__icontains=q)
            | Q(categoria__nombre__icontains=q)
        )
        productos = list(_productos_con_ranking(Producto.objects.filter(filtro)))
        for producto in productos:
            producto.mejor_resena = _mejor_resena(producto)

    return render(request, "tienda/buscar.html", {"q": q, "productos": productos})


def carrito(request):
    return render(request, "tienda/carrito.html", {"usuarios": Usuario.objects.all()})