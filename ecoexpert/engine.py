"""Ocho reglas para explicar un sistema experto básico en clase."""
from . import compat
from experta import Fact, KnowledgeEngine, Rule, P
from .models import Consulta

APROVECHABLES = {"botella_plastico", "caja_carton", "hojas_papel", "frasco_vidrio", "lata"}
REGLAS = [
    {"id": "R1", "si": "Son restos de comida o vegetales.", "entonces": "Identificar la familia orgánica."},
    {"id": "R2", "si": "Es una botella de plástico, caja de cartón, hojas, frasco de vidrio o lata.", "entonces": "Identificar un material candidato a aprovechamiento."},
    {"id": "R3", "si": "Es un celular o una laptop.", "entonces": "Identificar la familia electrónica."},
    {"id": "R4", "si": "Es candidato a aprovechamiento, limpio/seco y sin contacto químico conocido.", "entonces": "Proponer una ruta de reciclaje sujeta a aceptación local."},
    {"id": "R5", "si": "Es de familia orgánica y no se conoce contacto químico.", "entonces": "Proponer separación de orgánicos."},
    {"id": "R6", "si": "Es de familia electrónica y no se conoce contacto químico.", "entonces": "Proponer revisión en un centro especializado."},
    {"id": "R7", "si": "Se conoce contacto químico o no se sabe si ocurrió.", "entonces": "Pedir revisión antes de proponer una ruta."},
    {"id": "R8", "si": "Es aprovechable, pero no está limpio/seco o no se sabe.", "entonces": "Pedir revisar sus condiciones de recepción."},
]


class Dato(Fact):
    pass


class Familia(Fact):
    pass


class Motor(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.pasos = []
        self.resultado = None

    def registrar(self, numero):
        regla = REGLAS[numero - 1]
        self.pasos.append({**regla, "paso": len(self.pasos) + 1})

    @Rule(Dato(objeto="restos_comida"))
    def organico(self):
        self.declare(Familia(tipo="organico"))
        self.registrar(1)

    @Rule(Dato(objeto=P(lambda o: o in APROVECHABLES)))
    def aprovechable(self):
        self.declare(Familia(tipo="aprovechable"))
        self.registrar(2)

    @Rule(Dato(objeto=P(lambda o: o in {"celular", "laptop"})))
    def electronico(self):
        self.declare(Familia(tipo="electronico"))
        self.registrar(3)

    @Rule(Familia(tipo="aprovechable"), Dato(limpio="si", contacto_quimicos="no"))
    def reciclaje(self):
        self.resultado = "reciclable"
        self.registrar(4)

    @Rule(Familia(tipo="organico"), Dato(contacto_quimicos="no"))
    def separacion_organica(self):
        self.resultado = "organico"
        self.registrar(5)

    @Rule(Familia(tipo="electronico"), Dato(contacto_quimicos="no"))
    def centro_especializado(self):
        self.resultado = "electronico"
        self.registrar(6)

    @Rule(Dato(contacto_quimicos=P(lambda v: v in {"si", "desconocido"})))
    def revisar_contacto(self):
        self.resultado = "revision_contacto"
        self.registrar(7)

    @Rule(Familia(tipo="aprovechable"), Dato(limpio=P(lambda v: v in {"no", "desconocido"}), contacto_quimicos="no"))
    def revisar_limpieza(self):
        self.resultado = "revision_condiciones"
        self.registrar(8)


RESULTADOS = {
    "organico": ("Orgánico", "Separa este material con los orgánicos y confirma su recepción local."),
    "reciclable": ("Candidato a reciclaje", "Confirma que el centro de acopio acepte ese material."),
    "electronico": ("Residuo electrónico", "Busca un punto de acopio de electrónicos en tu localidad."),
    "revision_contacto": ("Requiere revisión", "Aclara el contacto con productos químicos antes de decidir su manejo."),
    "revision_condiciones": ("Revisa sus condiciones", "Confirma si el material cumple las condiciones del centro de acopio."),
    "sin_determinar": ("Falta información o el material no está cubierto", "Esta demo no tiene una regla suficiente para concluir el caso."),
}


def evaluar(consulta: Consulta):
    motor = Motor()
    motor.reset()
    datos = consulta.model_dump()
    if consulta.objeto in APROVECHABLES and datos["limpio"] is None:
        datos["limpio"] = "desconocido"
    motor.declare(Dato(**{k: v for k, v in datos.items() if v is not None}))
    motor.run()
    codigo = motor.resultado or "sin_determinar"
    titulo, recomendacion = RESULTADOS[codigo]
    return {"codigo": codigo, "titulo": titulo, "recomendacion": recomendacion,
            "pasos": motor.pasos, "datos": consulta.model_dump()}
