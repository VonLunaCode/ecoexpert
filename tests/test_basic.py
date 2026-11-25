import unittest
from fastapi.testclient import TestClient
from ecoexpert.app import app
from ecoexpert.engine import evaluar, Motor, REGLAS
from ecoexpert.models import Consulta


class BasicTests(unittest.TestCase):
    def test_four_classroom_examples(self):
        for objeto, limpio, contacto, expected in [
            ("restos_comida", None, "no", "organico"),
            ("botella_plastico", "si", "no", "reciclable"),
            ("celular", None, "no", "electronico"),
            ("lata", "no", "si", "revision_contacto"),
        ]:
            with self.subTest(objeto=objeto):
                result = evaluar(Consulta(objeto=objeto, limpio=limpio, contacto_quimicos=contacto))
                self.assertEqual(result["codigo"], expected)
                if objeto == "celular":
                    self.assertEqual([p["id"] for p in result["pasos"]], ["R3", "R6"])

    def test_real_forward_chain(self):
        result = evaluar(Consulta(objeto="hojas_papel", limpio="si", contacto_quimicos="no"))
        self.assertEqual([p["id"] for p in result["pasos"]], ["R2", "R4"])

    def test_known_or_unknown_chemical_contact_blocks_recycling(self):
        for contacto in ["si", "desconocido"]:
            result = evaluar(Consulta(objeto="botella_plastico", limpio="si", contacto_quimicos=contacto))
            self.assertEqual(result["codigo"], "revision_contacto")
            self.assertNotIn("R4", [p["id"] for p in result["pasos"]])

    def test_missing_information_does_not_become_safe(self):
        self.assertEqual(evaluar(Consulta(objeto="hojas_papel", contacto_quimicos="no"))["codigo"], "revision_condiciones")
        self.assertEqual(evaluar(Consulta(objeto="desconocido", contacto_quimicos="no"))["codigo"], "sin_determinar")

    def test_queries_are_independent(self):
        first = evaluar(Consulta(objeto="lata", limpio="si", contacto_quimicos="si"))
        second = evaluar(Consulta(objeto="restos_comida", contacto_quimicos="no"))
        self.assertEqual(first["codigo"], "revision_contacto")
        self.assertEqual([p["id"] for p in second["pasos"]], ["R1", "R5"])

    def test_api_and_rule_catalog(self):
        client = TestClient(app)
        self.assertEqual(client.get("/").status_code, 200)
        self.assertEqual(client.get("/healthz").json()["rules"], 8)
        self.assertEqual(len(Motor().get_rules()), len(REGLAS))
        self.assertEqual(client.post("/api/evaluate", json={"objeto": "inventado"}).status_code, 422)
        result = client.post("/api/evaluate", json={"objeto": "frasco_vidrio", "limpio": "si", "contacto_quimicos": "no"})
        self.assertEqual(result.json()["codigo"], "reciclable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
