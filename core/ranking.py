from django.db.models import Avg, Count, Case, When, IntegerField


def productos_con_ranking(queryset):
    return queryset.annotate(
        rating_promedio=Avg("resenas__calificacion"),
        total_resenas=Count("resenas"),
        resenas_creadoras=Count(
            Case(When(resenas__es_creadora=True, then=1), output_field=IntegerField())
        ),
    ).order_by("-resenas_creadoras", "-rating_promedio", "-total_resenas", "id")


def mejor_resena(producto):
    return (
        producto.resenas.exclude(comentario="")
        .order_by("-es_creadora", "-calificacion")
        .first()
    )