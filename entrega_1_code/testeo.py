import grpc
import distance_unary_pb2_grpc as pb2_grpc
import distance_unary_pb2 as pb2
import unittest


def print_result(response, id):
    print(f"---------------------------Prueba: {id} inicio -------------------------------------")
    print(f"Distance: {response.distance:.2f} Unit: {response.unit} (Method: {response.method})")


class TestDistanceService(unittest.TestCase):
    def setUp(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = pb2_grpc.DistanceServiceStub(self.channel)


   # Probar con coordenadas válidas en kilómetros
    def test_valid_coordinates_km(self):
        id = 1
        message = pb2.SourceDest(
            source=pb2.Position(latitude=-33.0351516, longitude=-70.5955963),
            destination=pb2.Position(latitude=-33.0348327, longitude=-71.5980458),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        self.assertIsNotNone(response)
        self.assertGreater(response.distance, 0)
        print_result(response, id)

    # Probar con latitudes en los límites ( 90)
    def test_boundary_latitudes(self):
        id = 2
        message_south = pb2.SourceDest(
            source=pb2.Position(latitude=-90, longitude=0),  # polo sur
            destination=pb2.Position(latitude=0, longitude=0),  # punto en el ecuador
            unit="km"
        )
        response_south = self.stub.geodesic_distance(message_south)
        self.assertIsNotNone(response_south)
        self.assertGreater(response_south.distance, 0)
        print_result(response_south, id)

        message_north = pb2.SourceDest(
            source=pb2.Position(latitude=90, longitude=0),  # polo norte
            destination=pb2.Position(latitude=0, longitude=0),  # punto en el ecuador
            unit="km"
        )
        response_north = self.stub.geodesic_distance(message_north)
        self.assertIsNotNone(response_north)
        self.assertGreater(response_north.distance, 0)
        print_result(response_north, id)

    def test_latitude_out_of_range(self):
        id = 3

        # Test con latitud fuera del rango en este caso -91
        message1 = pb2.SourceDest(
            source=pb2.Position(latitude=-90, longitude=0),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="km"
        )

        res = self.stub.geodesic_distance(message1)

        # Esperar que falle si devuelve valores incorrectos
        self.assertIsNotNone(res)


        #Forzamos fallos en las siguientes condiciones       
        self.assertNotEqual(res.distance, -1)  
        self.assertNotEqual(res.unit, "invalid")  
        self.assertEqual(res.method, "geodesic")
        print_result(res, id)

        # Test con latitud fuera del rango en este caso 91
        message2 = pb2.SourceDest(
            source=pb2.Position(latitude=90, longitude=0),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="km"
        )

        res2 = self.stub.geodesic_distance(message2)

        # Esperar que falle si devuelve valores incorrectos
        self.assertIsNotNone(res2)
        self.assertNotEqual(res2.distance, -1) 
        self.assertNotEqual(res2.unit, "invalid")  
        self.assertEqual(res2.method, "geodesic")

        print_result(res2, id)
        


    # Probar con longitudes en los límites (-180 y 180)
    def test_longitude_boundary_values(self):
        id = 4
        message = pb2.SourceDest(
            source=pb2.Position(latitude=40, longitude=-180),
            destination=pb2.Position(latitude=70, longitude=180),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        self.assertIsNotNone(response)

        if response.distance <= 0.0:
            raise ValueError("Distancia es invalida, se devolvio 0.0 o menos")

        self.assertGreater(response.distance, 0.0)
        print_result(response, id)

        message = pb2.SourceDest(
            source=pb2.Position(latitude=70, longitude=180),
            destination=pb2.Position(latitude=50, longitude=-180),
            unit="km"
        )
        response = self.stub.geodesic_distance(message)
        self.assertIsNotNone(response)

        if response.distance <= 0.0:
            raise ValueError("Distancia es invalida, se devolvio 0.0 o menos")

        self.assertGreater(response.distance, 0.0)
        print_result(response, id)


    # Probar con unidad de medida vacía (debe devolver en km por defecto)
    def test_distance_with_empty_unit(self):
        id = 5

        message = pb2.SourceDest(
            source=pb2.Position(latitude=-33.0351516, longitude=-70.5955963),
            destination=pb2.Position(latitude=-33.0348327, longitude=-70.5980458),
            unit=""
        )

        response = self.stub.geodesic_distance(message)
        self.assertIsNotNone(response)

        self.assertGreater(response.distance, 0.0, msg="La distancia debe ser mayor a 0.0")
        self.assertEqual(response.unit, "km", msg="La unidad de medida esperada es km o nm")

        print_result(response, id)

# Probar con longitudes fuera del rango  en este caso con -181 y 181

    def test_longitude_out_of_range(self):
        id = 6
        message1 = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=-181),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="km"
        )
        res = self.stub.geodesic_distance(message1)
        self.assertIsNotNone(res)
        self.assertEqual(res.method, "geodesic")
        self.assertEqual(res.unit, "km")
        print_result(res, id)


        message2 = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=181),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="km"
        )

        response2 = self.stub.geodesic_distance(message2)
        self.assertIsNotNone(response2)
        self.assertEqual(response2.method, "geodesic")
        self.assertEqual(response2.unit, "invalid")
        print_result(response2, id)

# Probar con unidad de medida inválida

    def test_invalid_unit(self):
        id = 7
        message = pb2.SourceDest(
            source=pb2.Position(latitude=10.0, longitude=20.0, altitude=0),
            destination=pb2.Position(latitude=30.0, longitude=40.0, altitude=0),
            unit="km"  # Unidad
        )

        res = self.stub.geodesic_distance(message)

        # Condición de validación correcta

        if res.unit != "km" and res.unit != "nm":
            raise ValueError("El valor debe ser válido")
        else:
            self.assertIsNotNone(res)

            self.assertEqual(res.unit, "unidad_invalida")  
            print_result(res, id)

    #  Probar con el mismo origen y destino

    def test_same_origin_and_destination(self):
        id = 8
        message = pb2.SourceDest(
            source=pb2.Position(latitude=10.0, longitude=20.0, altitude=0),
            destination=pb2.Position(latitude=10.0, longitude=20.0, altitude=0),
            unit="km"
        )

        res = self.stub.geodesic_distance(message)
        self.assertIsNotNone(res)
        self.assertEqual(res.distance, 0)
        self.assertEqual(res.method, "geodesic")
        self.assertEqual(res.unit, "km")
        print_result(res, id)

    #  Probar con latitud y longitud válidas pero con unidad de medida en "nm"

    def test_valid_coordinates_nautical_miles(self):
        id = 9
        message = pb2.SourceDest(
            source=pb2.Position(latitude=10.0, longitude=20.0, altitude=0),
            destination=pb2.Position(latitude=30.0, longitude=40.0, altitude=0),
            unit="nm"
        )

        res = self.stub.geodesic_distance(message)

        self.assertIsNotNone(res)
        expected_distance_nm = 1639.16 # valor esperado aprox. para la latitud y longitud dadas en nm
        self.assertAlmostEqual(res.distance, expected_distance_nm, delta=1.0)
        self.assertEqual(res.method, "geodesic")
        self.assertEqual(res.unit, "nm")
        print_result(res, id)

    #Probar el cálculo de distancia entre latitudes cercanas a los límites -90 y 90
    def test_near_limit_latitudes(self):
        id = 10
        message = pb2.SourceDest(
            source=pb2.Position(latitude=89.9999, longitude=0.0, altitude=0),
            destination=pb2.Position(latitude=-89.9999, longitude=0.0, altitude=0),
            unit="km"
        )

        res = self.stub.geodesic_distance(message)

        self.assertIsNotNone(res)
        expected_distance_km = 20003.91  # distancia aprox. en kilómetros entre los polos
        self.assertAlmostEqual(res.distance, expected_distance_km, delta=1.0)
        self.assertEqual(res.method, "geodesic")
        self.assertEqual(res.unit, "km")
        print_result(res, id)

    def tearDown(self):
        self.channel.close()


if __name__ == "__main__":
    unittest.main()