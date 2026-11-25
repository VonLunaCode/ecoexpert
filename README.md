# EcoExpert

Sistema experto básico para clasificar residuos del hogar, hecho con [Experta](https://github.com/nilp0inter/experta) (motor de reglas en Python) y FastAPI. Proyecto de la materia de Inteligencia Artificial.

## Qué hace

Una pantalla y tres datos: objeto cotidiano, limpio/seco cuando corresponda y contacto conocido con productos químicos. El usuario no elige una clasificación técnica: las reglas de Experta **infieren la familia** del residuo y explican qué reglas se activaron.

La idea que se demuestra es el encadenamiento hacia adelante: una regla identifica una familia y otra usa ese hecho para proponer una clasificación.

Ejemplo: celular → **R3** (familia electrónica) → **R6** (revisión en centro especializado) → «Residuo electrónico».

## Las ocho reglas

| Regla | Si… | Entonces… |
|---|---|---|
| R1 | Son restos de comida o vegetales. | Identificar la familia orgánica. |
| R2 | Es una botella de plástico, caja de cartón, hojas, frasco de vidrio o lata. | Identificar un material candidato a aprovechamiento. |
| R3 | Es un celular o una laptop. | Identificar la familia electrónica. |
| R4 | Es candidato a aprovechamiento, limpio/seco y sin contacto químico conocido. | Proponer una ruta de reciclaje sujeta a aceptación local. |
| R5 | Es de familia orgánica y no se conoce contacto químico. | Proponer separación de orgánicos. |
| R6 | Es de familia electrónica y no se conoce contacto químico. | Proponer revisión en un centro especializado. |
| R7 | Se conoce contacto químico o no se sabe si ocurrió. | Pedir revisión antes de proponer una ruta. |
| R8 | Es aprovechable, pero no está limpio/seco o no se sabe. | Pedir revisar sus condiciones de recepción. |

Cuando falta información, el sistema no asume que el residuo es seguro: pide revisión o declara que no puede concluir.

## Alcance

Es una demo acotada al ámbito doméstico. No incluye pH, residuos biológico-infecciosos (RPBI), normativa detallada ni residuos de origen industrial. Las recomendaciones dependen de que el centro de acopio local acepte el material.

## Ejecutar

Con Python 3.12, crea un entorno virtual e instala `requirements.lock`. Después:

```text
python -m uvicorn ecoexpert.app:app --host 127.0.0.1 --port 8817
```

Abre `http://127.0.0.1:8817`.

## Pruebas

Instala también `httpx==0.28.1` y ejecuta:

```text
python -m unittest discover -s tests -v
```

Son seis pruebas: los cuatro ejemplos de clase, el encadenamiento, el bloqueo ante contacto químico conocido o desconocido, el manejo de información faltante, la independencia entre consultas y la API.

## Nota técnica

Experta 1.9.4 necesita un pequeño adaptador de compatibilidad con Python 3.12 (`collections.Mapping`), incluido en `ecoexpert/compat.py`.

## API

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/evaluate` | Evalúa un objeto y devuelve resultado y reglas activadas |
| `GET` | `/api/rules` | Lista las ocho reglas |
| `GET` | `/healthz` | Estado del servicio |
