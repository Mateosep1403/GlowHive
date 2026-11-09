
class UsuarioNoEncontradoError(Exception):
    """El usuario referenciado no existe. -> HTTP 404"""


class ProductoNoEncontradoError(Exception):
    """Alguno de los productos referenciados no existe. -> HTTP 404"""


class OrdenBuilderError(Exception):
    """Datos inválidos para construir la orden (falta usuario/productos). -> HTTP 400"""


class StockInsuficienteError(Exception):
    """Un producto de la orden no tiene stock suficiente. -> HTTP 409 (conflicto)"""