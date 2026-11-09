from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    comisionPorcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=10)

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    tipoPiel = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name="productos")
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name="productos"
    )
    imagen = models.ImageField(upload_to="productos/", null=True, blank=True)
    video_url = models.URLField(
        max_length=300,
        blank=True,
        default="",
        help_text="Enlace al video de TikTok de una creadora (ej. https://www.tiktok.com/@usuario/video/123...). Opcional.",
    )
    

    def __str__(self):
        return self.nombre


class Orden(models.Model):
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("CONFIRMADA", "Confirmada"),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="ordenes")
    productos = models.ManyToManyField(Producto, related_name="ordenes")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="PENDIENTE")
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def marcar_como(self, estado: str) -> None:
        """Único método permitido en el Model: es persistencia pura
        (cambia y guarda un campo), no calcula ni decide nada de negocio."""
        self.estado = estado
        self.save(update_fields=["estado"])

    def guardar_total(self, total) -> None:
        """Persistencia pura: guarda un total ya calculado por el Service Layer."""
        self.total = total
        self.save(update_fields=["total"])

    def __str__(self):
        return f"Orden #{self.id} - {self.estado}"


class Pago(models.Model):
   
    ESTADOS_PAGO = [
        ("APROBADO", "Aprobado"),
        ("RECHAZADO", "Rechazado"),
        ("PENDIENTE", "Pendiente"),
    ]
    orden = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name="pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=50, default="TARJETA")
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default="PENDIENTE")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago #{self.id} - Orden #{self.orden_id} - {self.estado}"


class Resena(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="resenas")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="resenas")
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.CharField(max_length=500, blank=True)
    es_creadora = models.BooleanField(default=False)  # NUEVO
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "producto")
        verbose_name_plural = "Reseñas"

    def __str__(self):
        return f"Reseña de {self.usuario.nombre} a {self.producto.nombre} ({self.calificacion}/5)"

class DireccionEnvio(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="direcciones")
    calle = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    codigoPostal = models.CharField(max_length=20, blank=True)
    pais = models.CharField(max_length=100, default="Colombia")
    esPrincipal = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Direcciones de envío"

    def __str__(self):
        return f"{self.calle}, {self.ciudad} ({self.usuario.nombre})"