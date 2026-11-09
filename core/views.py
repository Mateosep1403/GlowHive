from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.services import OrdenService
from core.serializers import CrearOrdenSerializer, OrdenSerializer
from core.domain.excepciones import (
    UsuarioNoEncontradoError,
    ProductoNoEncontradoError,
    OrdenBuilderError,
    StockInsuficienteError,
)


class CrearOrdenView(APIView):
    """Capa de presentación (DRF): SOLO valida forma de entrada, delega al
    Service Layer y traduce excepciones de dominio a códigos HTTP.
    No hay cálculos ni reglas de negocio aquí.
    """

    def post(self, request):
        entrada = CrearOrdenSerializer(data=request.data)
        if not entrada.is_valid():
            return Response(entrada.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            orden = OrdenService().crear_orden(
                usuario_id=entrada.validated_data["usuario_id"],
                productos_ids=entrada.validated_data["productos_ids"],
            )
        except (UsuarioNoEncontradoError, ProductoNoEncontradoError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except OrdenBuilderError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except StockInsuficienteError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response(OrdenSerializer(orden).data, status=status.HTTP_201_CREATED)