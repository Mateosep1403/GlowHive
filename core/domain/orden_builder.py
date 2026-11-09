from tienda.models import Orden
from core.domain.reglas_negocio import validar_stock
from core.domain.excepciones import OrdenBuilderError, StockInsuficienteError


class OrdenBuilder:
    """Patrón Builder: construye paso a paso la entidad más compleja del
    sistema (Orden), garantizando que nunca se persista una orden inválida.
    """

    def __init__(self):
        self._usuario = None
        self._productos = []

    def para_usuario(self, usuario):
        self._usuario = usuario
        return self

    def con_productos(self, productos):
        self._productos = list(productos)
        return self

    def _validar(self):
        if self._usuario is None:
            raise OrdenBuilderError("La orden requiere un usuario.")
        if not self._productos:
            raise OrdenBuilderError("La orden requiere al menos un producto.")
        for producto in self._productos:
            if not validar_stock(producto):
                raise StockInsuficienteError(
                    f"Sin stock suficiente para '{producto.nombre}'."
                )

    def build(self) -> Orden:
        self._validar()
        orden = Orden(usuario=self._usuario, estado="PENDIENTE")
        orden.save()
        orden.productos.set(self._productos)
        return orden