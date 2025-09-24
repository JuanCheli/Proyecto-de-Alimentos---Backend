from typing import List, Dict, Any
from api.db.repositories.alimento_repo import get_by_codigos
from api.config import settings

class RecetaError(Exception):
    pass

def generar_receta_llm(ingredientes: List[Dict[str, Any]], modelo: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """
    ingredientes: [{"nombre": "haba", "cantidad_g": 100}, ...]
    Devuelve receta con título, instrucciones, lista de ingredientes y nutrición total.
    """
    try:
        from google import genai
    except ImportError:
        raise RecetaError("No se puede importar genai. Instalá la librería.")

    client = genai.Client(api_key=settings.GENAI_API_KEY)

    # Preparamos la lista para el prompt
    ingredientes_txt = "\n".join([f"{i['cantidad_g']}g de {i['nombre']}" for i in ingredientes])

    prompt = f"""
    Eres un chef que genera recetas inventadas pero consistentes.
    Recibís la siguiente lista de ingredientes con cantidades:
    {ingredientes_txt}

    Devuelve un JSON EXACTO con el siguiente formato:
    {{
      "titulo": "Nombre de la receta",
      "ingredientes": ["100g harina de haba", "50g queso cheddar"],
      "instrucciones": "Texto de preparación paso a paso",
      "nutricion_total": {{
          "energ_kcal": ...,
          "protein": ...,
          "fat": ...,
          "carbs": ...
      }}
    }}
    """
    try:
        response = client.models.generate_content(model=modelo, contents=prompt)
    except Exception as e:
        raise RecetaError("Error llamando al LLM") from e

    # Extraemos texto
    text = getattr(response, "text", str(response))

    import json

    text_clean = text.strip()
    if text_clean.startswith("```json"):
        text_clean = text_clean[7:]
    if text_clean.endswith("```"):
        text_clean = text_clean[:-3]
    text_clean = text_clean.strip()

    try:
        receta_json = json.loads(text_clean)
    except Exception as e:
        raise RecetaError(f"LLM no devolvió JSON válido: {text_clean}") from e

    return receta_json

def crear_receta(ingredientes_codigos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    1. Consultamos los alimentos en DB
    2. Creamos objeto con nombre y cantidad
    3. Llamamos a LLM para generar receta
    4. Calculamos nutrición total sumando nutrientes proporcional a cantidad
    """
    codigos = [i["codigomex2"] for i in ingredientes_codigos]
    alimentos = get_by_codigos(codigos)  # devuelve lista de dicts con columnas de nutrición

    if not alimentos:
        raise RecetaError("No se encontraron alimentos con esos códigos.")

    # Asociamos cantidad a cada alimento
    ingredientes = []
    for i in ingredientes_codigos:
        alimento = next((a for a in alimentos if a["codigomex2"] == i["codigomex2"]), None)
        if alimento:
            cantidad = i.get("cantidad_g", 100)
            ingredientes.append({"nombre": alimento["nombre_del_alimento"], "cantidad_g": cantidad, "nutricion": alimento})

    # Preparamos lista para prompt LLM
    receta = generar_receta_llm(ingredientes)

    # Calculamos nutrición total real sumando nutrientes proporcional a cantidad
    nutricion_total = {"energ_kcal": 0, "protein": 0, "fat": 0, "carbs": 0}
    for ing in ingredientes:
        factor = ing["cantidad_g"] / 100
        nutricion_total["energ_kcal"] += float(ing["nutricion"].get("energ_kcal") or 0) * factor
        nutricion_total["protein"] += float(ing["nutricion"].get("protein") or 0) * factor
        nutricion_total["fat"] += float(ing["nutricion"].get("lipid_tot") or 0) * factor
        nutricion_total["carbs"] += float(ing["nutricion"].get("carbohydrt") or 0) * factor

    receta["nutricion_total"] = {k: round(v, 2) for k, v in nutricion_total.items()}

    return receta
