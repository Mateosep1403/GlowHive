from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)


class NotificacionError(Exception):
    def __init__(self, mensaje, codigo=400):
        self.mensaje = mensaje
        self.codigo = codigo


@app.errorhandler(NotificacionError)
def manejar_error_notificacion(error):
    return jsonify({"error": error.mensaje}), error.codigo


@app.errorhandler(Exception)
def manejar_error_generico(error):
    return jsonify({"error": "Error interno del servicio de notificaciones"}), 500


@app.route("/api/v2/notificaciones/confirmar", methods=["POST"])
def confirmar_orden():
    data = request.get_json(silent=True)

    if not data:
        raise NotificacionError("Se requiere un cuerpo JSON válido.", 400)

    orden_id = data.get("orden_id")
    usuario_nombre = data.get("usuario_nombre")
    total = data.get("total")

    if orden_id is None or not usuario_nombre or total is None:
        raise NotificacionError(
            "Faltan campos requeridos: orden_id, usuario_nombre, total.", 400
        )

    # Aquí iría la integración real (SendGrid, Twilio, etc.)
    print(f"[FLASK] Notificación enviada a {usuario_nombre} — Orden #{orden_id} — Total: ${total}")

    return jsonify({
        "status": "enviado",
        "orden_id": orden_id,
        "canal": "email",
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


@app.route("/api/v2/notificaciones/salud", methods=["GET"])
def salud():
    return jsonify({"status": "ok", "servicio": "notificaciones"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)