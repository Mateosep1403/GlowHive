from django.core.management.base import BaseCommand
from tienda.models import Marca, Categoria, Usuario, Producto, Resena


class Command(BaseCommand):
    help = "Crea datos de prueba: marcas, categorías, usuarios, productos y reseñas."

    def handle(self, *args, **options):
        marca, _ = Marca.objects.get_or_create(
            nombre="GlowHive Basics", defaults={"comisionPorcentaje": 12}
        )

        cat_hair, _ = Categoria.objects.get_or_create(
            nombre="Hair Care", defaults={"descripcion": "Cuidado del cabello"}
        )
        cat_skin, _ = Categoria.objects.get_or_create(
            nombre="Skincare", defaults={"descripcion": "Rutina facial y corporal"}
        )
        cat_makeup, _ = Categoria.objects.get_or_create(
            nombre="Make Up", defaults={"descripcion": "Maquillaje para cada ocasión"}
        )

        usuario1, _ = Usuario.objects.get_or_create(nombre="Valentina Ríos", defaults={"tipoPiel": "Mixta"})
        usuario2, _ = Usuario.objects.get_or_create(nombre="Camila Torres", defaults={"tipoPiel": "Seca"})

        productos_data = [
            ("Shampoo reparador", 45000, 20, cat_hair, "Le devolvió la vida a mi cabello dañado por el tinte."),
            ("Aceite capilar nutritivo", 38000, 15, cat_hair, "Uso 3 gotas después del baño y mi pelo brilla todo el día."),
            ("Serum de vitamina C", 62000, 10, cat_skin, "En dos semanas mi piel se veía notablemente más luminosa."),
            ("Crema hidratante SPF 30", 55000, 25, cat_skin, "La textura es liviana, no deja la piel grasosa."),
            ("Labial mate larga duración", 32000, 30, cat_makeup, "Dura todo el día sin resecar los labios."),
            ("Base líquida cobertura media", 68000, 12, cat_makeup, "Se ve muy natural, como segunda piel."),
        ]

        for nombre, precio, stock, categoria, comentario in productos_data:
            producto, creado = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "precio": precio,
                    "stock": stock,
                    "marca": marca,
                    "categoria": categoria,
                },
            )
            if creado:
                Resena.objects.get_or_create(
                    usuario=usuario1,
                    producto=producto,
                    defaults={"calificacion": 5, "comentario": comentario, "es_creadora": True},
                )
                Resena.objects.get_or_create(
                    usuario=usuario2,
                    producto=producto,
                    defaults={"calificacion": 4, "comentario": "Buen producto, cumple lo que promete.", "es_creadora": False},
                )

        self.stdout.write(self.style.SUCCESS("Datos de prueba creados correctamente."))