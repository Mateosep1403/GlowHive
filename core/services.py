from tienda.models import Categoria, DireccionEnvio, Producto, Resena, Usuario
from core.domain.orden_builder import OrdenBuilder
from core.domain.reglas_negocio import calcular_total_orden, calcular_comision_marca
from core.domain.excepciones import UsuarioNoEncontradoError, ProductoNoEncontradoError
from core.infra.notificador_factory import NotificadorFactory
from core.infra.pasarela_pago import PasarelaPago


class OrdenService:
    """Orquesta el flujo completo de creación de una orden (SRP: esta es su
    única responsabilidad). Nada de esto vive en la View ni en el Model.
    Las dependencias externas (notificador, pasarela de pago) se inyectan,
    lo que facilita testear el service con mocks/fakes.
    """

    def __init__(self, notificador=None, pasarela_pago=None):
        self.notificador = notificador or NotificadorFactory.crear()
        self.pasarela_pago = pasarela_pago or PasarelaPago()

    def crear_orden(self, usuario_id: int, productos_ids: list[int]):
        usuario = self._obtener_usuario(usuario_id)
        productos = self._obtener_productos(productos_ids)

        # 1. Construcción validada de la orden (Builder)
        orden = OrdenBuilder().para_usuario(usuario).con_productos(productos).build()

        # 2. Cálculo del total (regla de negocio, no vive en el Model)
        total = calcular_total_orden(productos)
        orden.guardar_total(total)

        # 3. Reparto de comisiones por marca (regla de negocio)
        for producto in productos:
            comision = calcular_comision_marca(producto)
            print(f"Comisión para {producto.marca.nombre}: {comision}")

        # 4. Procesamiento de pago (delegado a un colaborador de infraestructura)
        self.pasarela_pago.procesar(orden)

        # 5. Confirmación de la orden
        orden.marcar_como("CONFIRMADA")

        # 6. Notificación (Factory: Email en prod, Consola en dev)
        self.notificador.enviar_confirmacion(orden)

        return orden

    def _obtener_usuario(self, usuario_id: int) -> Usuario:
        try:
            return Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            raise UsuarioNoEncontradoError(f"Usuario {usuario_id} no existe.")

    def _obtener_productos(self, productos_ids: list[int]):
        productos = list(Producto.objects.filter(id__in=productos_ids))
        encontrados_ids = {p.id for p in productos}
        faltantes = set(productos_ids) - encontrados_ids
        if faltantes:
            raise ProductoNoEncontradoError(f"Productos no encontrados: {sorted(faltantes)}")
        return productos


class ProductoService:
    """Casos de uso del catalogo de productos."""

    @staticmethod
    def listar():
        return Producto.objects.select_related("marca", "categoria").all()


class CategoriaService:
    """Casos de uso del catalogo de categorias."""

    @staticmethod
    def listar():
        return Categoria.objects.all()


class ResenaService:
    """Casos de uso de consulta y creacion de resenas."""

    @staticmethod
    def listar():
        return Resena.objects.select_related("usuario", "producto").all()

    @staticmethod
    def crear(datos):
        return Resena.objects.create(**datos)


class DireccionEnvioService:
    """Casos de uso de consulta y creacion de direcciones de envio."""

    @staticmethod
    def listar():
        return DireccionEnvio.objects.select_related("usuario").all()

    @staticmethod
    def crear(datos):
        return DireccionEnvio.objects.create(**datos)