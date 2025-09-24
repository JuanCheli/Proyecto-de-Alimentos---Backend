# API Nutricional con Asistente de IA

Este proyecto es una **API REST** construida con **FastAPI** para consultar información nutricional de alimentos y generar recetas usando IA. Utiliza **Supabase** como base de datos y se integra con **Google GenAI (gemini-2.5-flash)** para procesamiento de lenguaje natural y generación de recetas.

---

## Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración](#configuración)
- [Routers y Endpoints](#routers-y-endpoints)
- [Ejemplos de Peticiones](#ejemplos-de-peticiones)
- [Servicios de IA](#servicios-de-ia)


---

## Características

- Consulta alimentos y sus propiedades nutricionales.
- Buscador de alimentos con filtros.
- Traducción de preguntas en lenguaje natural a SQL seguro.
- Generación de recetas inventadas y consistentes a partir de un conjunto de ingredientes.
- Cálculo de nutrición total de la receta.
- Healthcheck básico para validar conexión con la base de datos.
- Manejo de errores y logging completo.
- Compatible con CORS.

---

## Tecnologías

- **Python 3.11+**
- **FastAPI** (API REST)
- **Pydantic** (validación de datos)
- **Supabase** (Base de datos PostgreSQL gestionada)
- **Google GenAI** (`gemini-2.5-flash`) para:
  - Traducción de lenguaje natural a SQL
  - Generación de recetas
- **Uvicorn** (servidor ASGI)
- **Logging** integrado
- **CORS Middleware**

---

## Estructura del Proyecto

```
nippy_backend/
├── api/
│ ├── config/
│ │ ├── config.py
│ ├── db/
│ │ ├── connection.py
│ │ ├── session.py
│ │ ├── sql.py
│ │ ├── models/
│ │ │ ├── alimento_model.py
│ │ └── repositories/
│ │   ├── alimento_repo.py
│ ├── routes/
│ │ ├── alimentos.py
│ │ ├── asistente_ia.py
│ │ └── receta_ia.py
│ ├── schemas/
│ │ ├── alimento_schema.py
│ ├── services/
│ │ ├── asistente_service.py
│ │ ├── alimento_service.py
│ │ └── receta_service.py 
│ └── main.py 
├── requirements.txt 
└── README.md
```


---

## Configuración

1. Clonar el repositorio:
```bash
git clone <repo_url>
cd nippy_backend

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```
(comentario del desarrolador: los requirements fueron hechos con el comando pip freeze > requirements.txt, por lo que puede haber varias dependencias extra que no se usen)

4. Configurar variables de entorno:
```bash
# Crear archivo .env
# Configurar variables de entorno
| Variable        | Descripción                                                  |
| --------------- | ------------------------------------------------------------ |
| `SUPABASE_URL`  | URL de tu proyecto Supabase                                  |
| `SUPABASE_KEY`  | API Key de Supabase                                          |
| `GENAI_API_KEY` | API Key de Google GenAI                                      |
| `CORS_ORIGINS`  | Opcional. Orígenes permitidos para CORS, separados por comas |

```

5. Iniciar el servidor usando uvicorn:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

# Routers y Endpoints

## Alimentos
- GET /alimentos → Listado de alimentos con paginación.
- GET /alimento/{codigo} → Obtener alimento por código.
- POST /buscar → Buscar alimentos por filtros.
- POST /alimento → Insertar un nuevo alimento.

## Asistente IA
- POST /ask → Traduce una pregunta en lenguaje natural a SQL seguro y ejecuta la query en la base de datos.

Ejemplo de payload:
```json
{
  "question": "Dame alimentos altos en proteína y bajos en grasa",
  "max_results": 10
}
```

Respuesta esperada de ejemplo:
```json
[
  {
    "codigomex2": 101,
    "nombre_del_alimento": "Huevo",
    "protein": 13,
    "lipid_tot": 10,
    "energ_kcal": 155
  }
]

```

## Receta IA
- POST /receta → Genera una receta inventada a partir de un conjunto de ingredientes y calcula nutrición total.

Ejemplo de payload:
```json
{
  "ingredientes": [
    {
      "codigomex2": 1000,
      "cantidad_g": 100
    },
    {
      "codigomex2": 2000,
      "cantidad_g": 100
    }
  ]
}
```

Respuesta esperada de ejemplo:
```json
{
  "titulo": "Quesadillas de haba y cheddar",
  "ingredientes": ["100g harina de haba", "50g queso cheddar"],
  "instrucciones": "Mezcla la harina con agua, forma tortillas, agrega queso cheddar y cocina.",
  "nutricion_total": {
    "energ_kcal": 578,
    "protein": 47.3,
    "fat": 34.2,
    "carbs": 66.5
  }
}
```

# Servicios de IA
1. asistente_service.py

- Traduce preguntas de lenguaje natural a SQL seguro.
- Valida columnas y evita comandos peligrosos (DROP, DELETE, ALTER).
- Ejecuta la query y devuelve resultados como lista de diccionarios.

- Manejo de errores:
    - LLMError → Problemas con LLM
    - SQLValidationError → SQL inválida o insegura
    - ExecutionError → Error al ejecutar la consulta

2. receta_service.py

- Consulta los alimentos por código desde la base de datos.
- Llama al LLM para generar receta inventada en JSON.
- Calcula nutrición total proporcional a las cantidades de los ingredientes.

- Manejo de errores:
    - RecetaError → Problemas al generar receta o JSON inválido del LLM