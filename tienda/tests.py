from django.test import TestCase

from core.services import (
	CategoriaService,
	DireccionEnvioService,
	ProductoService,
	ResenaService,
)
from tienda.models import Categoria, DireccionEnvio, Marca, Producto, Usuario


class CatalogoServiceTests(TestCase):
	def setUp(self):
		self.usuario = Usuario.objects.create(nombre="Ana", tipoPiel="Mixta")
		self.marca = Marca.objects.create(nombre="Glow", comisionPorcentaje=10)
		self.categoria = Categoria.objects.create(nombre="Rostro")
		self.producto = Producto.objects.create(
			nombre="Crema hidratante",
			precio="25.00",
			stock=5,
			marca=self.marca,
			categoria=self.categoria,
		)

	def test_lista_productos_y_categorias(self):
		self.assertQuerySetEqual(ProductoService.listar(), [self.producto])
		self.assertQuerySetEqual(CategoriaService.listar(), [self.categoria])

	def test_crea_resena_mediante_service(self):
		resena = ResenaService.crear(
			{
				"usuario": self.usuario,
				"producto": self.producto,
				"calificacion": 5,
				"comentario": "Excelente",
			}
		)

		self.assertEqual(resena.usuario, self.usuario)
		self.assertEqual(resena.producto, self.producto)

	def test_crea_direccion_mediante_service(self):
		direccion = DireccionEnvioService.crear(
			{
				"usuario": self.usuario,
				"calle": "Calle 1",
				"ciudad": "Bogota",
				"codigoPostal": "110111",
				"pais": "Colombia",
				"esPrincipal": True,
			}
		)

		self.assertEqual(direccion.usuario, self.usuario)
		self.assertTrue(direccion.esPrincipal)
