from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.serializers import (
    ProductoSerializer,
    CategoriaSerializer,
    ResenaSerializer,
    DireccionEnvioSerializer,
)
from core.services import (
    CategoriaService,
    DireccionEnvioService,
    ProductoService,
    ResenaService,
)


class ProductoListView(APIView):
    """Endpoint de solo lectura para listar productos (catálogo).
    Sin lógica de negocio: solo consulta y serializa.
    """

    def get(self, request):
        productos = ProductoService.listar()
        return Response(ProductoSerializer(productos, many=True).data, status=status.HTTP_200_OK)


class CategoriaListView(APIView):
    """Listado simple de categorías. Sin lógica de negocio."""

    def get(self, request):
        categorias = CategoriaService.listar()
        return Response(CategoriaSerializer(categorias, many=True).data, status=status.HTTP_200_OK)


class ResenaListCreateView(APIView):
    def get(self, request):
        resenas = ResenaService.listar()
        return Response(ResenaSerializer(resenas, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ResenaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        resena = ResenaService.crear(serializer.validated_data)
        return Response(ResenaSerializer(resena).data, status=status.HTTP_201_CREATED)


class DireccionEnvioListCreateView(APIView):
    """Listar y crear direcciones de envío de un usuario."""

    def get(self, request):
        direcciones = DireccionEnvioService.listar()
        return Response(DireccionEnvioSerializer(direcciones, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DireccionEnvioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        direccion = DireccionEnvioService.crear(serializer.validated_data)
        return Response(DireccionEnvioSerializer(direccion).data, status=status.HTTP_201_CREATED)