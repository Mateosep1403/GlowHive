
from decimal import Decimal


def validar_stock(producto) -> bool:
    """Regla de negocio: un producto es comprable si tiene stock > 0."""
    return producto.stock > 0


def calcular_total_orden(productos) -> Decimal:
    """Suma el precio de una colección de productos."""
    return sum((p.precio for p in productos), Decimal("0.00"))


def calcular_comision_marca(producto) -> Decimal:
    """Calcula la comisión que le corresponde a la marca de un producto."""
    return producto.precio * (producto.marca.comisionPorcentaje / Decimal("100"))