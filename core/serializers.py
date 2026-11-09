from rest_framework import serializers
from tienda.models import Orden, Producto, Categoria, Resena, DireccionEnvio, Pago


class CrearOrdenSerializer(serializers.Serializer):
    """Entrada: valida el shape del request antes de tocar el Service Layer."""
    usuario_id = serializers.IntegerField(min_value=1)
    productos_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion"]


class ProductoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source="marca.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True, default=None)

    class Meta:
        model = Producto
        fields = ["id", "nombre", "precio", "stock", "marca", "marca_nombre", "categoria", "categoria_nombre"]


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ["id", "orden", "monto", "metodo", "estado", "fecha"]


class OrdenSerializer(serializers.ModelSerializer):
    """Salida: representación de una Orden ya creada."""
    productos = ProductoSerializer(many=True, read_only=True)
    pago = PagoSerializer(read_only=True)

    class Meta:
        model = Orden
        fields = ["id", "usuario", "productos", "estado", "fecha", "total", "pago"]


class ResenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resena
        fields = ["id", "usuario", "producto", "calificacion", "comentario", "fecha"]


class DireccionEnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = DireccionEnvio
        fields = ["id", "usuario", "calle", "ciudad", "codigoPostal", "pais", "esPrincipal"]