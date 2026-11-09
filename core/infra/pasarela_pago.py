
from tienda.models import Pago


class PasarelaPago:
    def procesar(self, orden) -> Pago:
        # Placeholder: aquí iría la integración real con la pasarela de pago.
        # Lo que SÍ es real: dejamos un registro persistente del pago (Pago).
        print(f"Pago procesado para orden #{orden.id} — total: {orden.total}")
        return Pago.objects.create(
            orden=orden,
            monto=orden.total,
            metodo="TARJETA",
            estado="APROBADO",
        )