import os
import requests


class Notificador:
    def enviar_confirmacion(self, orden):
        raise NotImplementedError


class EmailNotificador(Notificador):
    def enviar_confirmacion(self, orden):
        print(f"[EMAIL REAL] Confirmación enviada para orden #{orden.id}")


class ConsolaNotificador(Notificador):
    def enviar_confirmacion(self, orden):
        print(f"[DEV] Orden #{orden.id} creada (simulado).")

class HTTPNotificador(Notificador):
    """ llamar al microservicio flask de notificaciones para enviar la confirmación de la orden """
    def __init__(self):
        base_url = os.environ.get("NOTIFICACIONES_SERVICE_URL", "http://localhost:5000")
        self.url = f"{base_url}/api/v2/notificaciones/confirmar"

    def enviar_confirmacion(self, orden):
        try:
            response = requests.post(
                self.url,
                json={
                    "orden_id": orden.id,
                    "usuario_nombre": orden.usuario.nombre,
                    "total": float(orden.total),
                },
                timeout=5,
            )
            response.raise_for_status()
            print(f"[MICROSERVICIO] {response.json()}")
        except requests.RequestException as exc:
            print(f"[MICROSERVICIO] Error al notificar: {exc}")   


class NotificadorFactory:
    @staticmethod
    def crear():
        env = os.environ.get("ENV_TYPE", "DEV")
        if env == "MICROSERVICIO":
            return HTTPNotificador()
        if env == "REAL":
            return EmailNotificador()
        return ConsolaNotificador()