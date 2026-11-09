from django.contrib import admin
from .models import Marca, Usuario, Producto, Orden, Categoria, Resena, DireccionEnvio, Pago

admin.site.register(Marca)
admin.site.register(Usuario)
admin.site.register(Producto)
admin.site.register(Orden)
admin.site.register(Categoria)
admin.site.register(Resena)
admin.site.register(DireccionEnvio)
admin.site.register(Pago)