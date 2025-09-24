import re
import logging
from typing import Optional, Dict, Any, List
from api.db.sql import execute_sql
from api.config import settings

logger = logging.getLogger("asistente")
logger.addHandler(logging.NullHandler())

# Excepciones específicas
class LLMError(Exception):
    pass

class SQLValidationError(Exception):
    pass

class ExecutionError(Exception):
    pass

# Lista blanca de columnas (tu modelo SQLAlchemy)
ALLOWED_COLUMNS = {
    "codigomex2", "nombre_del_alimento", "energ_kcal", "carbohydrt", "lipid_tot",
    "protein", "fiber_td", "calcium", "iron", "ironhem", "ironnohem", "zinc",
    "vit_c", "thiamin", "riboflavin", "niacin", "panto_acid", "vit_b6",
    "folic_acid", "food_folate", "folate_dfe", "vit_b12", "vit_a_rae",
    "vit_e", "vit_d_iu", "vit_k", "fa_sat", "fa_mono", "fa_poly", "chole"
}

FORBIDDEN_KEYWORDS = {
    "drop", "delete", "update", "insert", "alter", "truncate", "grant", "revoke",
    "create", "replace", "merge", "call", "execute"
}

SELECT_FROM_REGEX = re.compile(r"(?is)^\s*select\b.*\bfrom\s+alimentos\b.*$")
IDENTIFIER_REGEX = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

def _extract_sql_from_text(text: str) -> Optional[str]:
    txt = text.strip()
    m = re.search(r"(?i)\bselect\b", txt)
    if not m:
        return None
    start = m.start()
    first_chunk = txt[start:]
    if ";" in first_chunk:
        first_chunk = first_chunk.split(";", 1)[0]
    return first_chunk.strip()

def _contains_forbidden_keyword(sql: str) -> bool:
    lower = sql.lower()
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", lower):
            return True
    return False

def _validate_sql(sql: str) -> Optional[str]:
    if not sql:
        return None
    sql_str = sql.strip()
    if sql_str.endswith(";"):
        sql_str = sql_str[:-1].strip()
    if ";" in sql_str:
        return None
    if not SELECT_FROM_REGEX.match(sql_str):
        return None
    if _contains_forbidden_keyword(sql_str):
        return None

    # Si el query usa "*", permitimos; si declara columnas, comprobamos que al menos las usadas están en allowed.
    if "*" not in sql_str:
        cols_found = set()
        # detecta nombres de columnas
        for col in ALLOWED_COLUMNS:
            if re.search(rf"\b{re.escape(col)}\b", sql_str, flags=re.IGNORECASE):
                cols_found.add(col)
        has_agg = bool(re.search(r"\b(count|avg|min|max|sum)\s*\(", sql_str, flags=re.IGNORECASE))
        if not cols_found and not has_agg:
            return None

    return sql_str

def translate_question_to_sql_with_llm(question: str, model: str = "gemini-2.5-flash", max_results: Optional[int] = 10) -> str:
    try:
        max_results = None if max_results is None else int(max_results)
    except Exception:
        max_results = 10
    if max_results is not None:
        max_results = max(1, min(500, max_results))  # capear entre 1 y 500

    try:
        from google import genai
    except Exception as e:
        logger.exception("genai import failed")
        raise LLMError("La librería genai no está disponible. Instalá e importá correctamente.") from e

    client = genai.Client(api_key=settings.GENAI_API_KEY)

    prompt = f"""
    Eres un traductor de lenguaje natural a SQL para una tabla Postgres llamada `alimentos`.
    DEVOLVÉ SOLO UNA SENTENCIA SQL válida (SELECT ... FROM alimentos ...), sin texto adicional.
    Reglas estrictas:
      - Usá sólo la tabla `alimentos`.
      - Permitidos: SELECT, FROM, WHERE, ORDER BY, GROUP BY, HAVING, LIMIT.
      - Prohibido: DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE, etc.
      - Columnas permitidas: {sorted(list(ALLOWED_COLUMNS))}
      - Si el usuario pide ranking (ej: "¿Qué alimento tiene más hierro?") devolvé ORDER BY iron DESC LIMIT 1.
      - Si el usuario pide "menos de 300 kcal" usá energ_kcal <= 300.
      - Si no mencionás columnas, devolvé columnas útiles: codigomex2, nombre_del_alimento, energ_kcal, protein, lipid_tot.
      - Respetá el parámetro max_results sugerido: {max_results}
    Ejemplos:
      Entrada: "Dame alimentos altos en proteína y bajos en grasa"
      Salida: SELECT codigomex2, nombre_del_alimento, protein, lipid_tot FROM alimentos WHERE protein >= 10 AND lipid_tot <= 10 ORDER BY protein DESC LIMIT {max_results}
      Entrada: "¿Qué alimento tiene más hierro?"
      Salida: SELECT codigomex2, nombre_del_alimento, iron FROM alimentos ORDER BY iron DESC LIMIT 1

    Traducí SOLO la siguiente pregunta a SQL:
    \"\"\"{question}\"\"\"
    """

    try:
        response = client.models.generate_content(model=model, contents=prompt)
    except Exception as e:
        logger.exception("Error llamando al LLM")
        raise LLMError("Error llamando al LLM (genai). Verificá credenciales y conexión.") from e

    text = getattr(response, "text", None) or str(response)
    logger.debug("LLM raw response: %s", text)

    candidate = _extract_sql_from_text(text)
    if not candidate:
        raise LLMError("El LLM no devolvió una sentencia SELECT válida.")

    validated = _validate_sql(candidate)
    if not validated:
        logger.debug("Candidate SQL failed validation: %s", candidate)
        raise SQLValidationError("La sentencia SQL generada no pasó las validaciones de seguridad.")

    if max_results:
        if not re.search(r"\blimit\b\s+\d+", validated, flags=re.IGNORECASE):
            validated = validated.rstrip() + f" LIMIT {int(max_results)}"

    return validated

def ask_llm_and_execute(question: str, max_results: Optional[int] = 10) -> List[Dict[str, Any]]:
    """
    pide SQL al LLM, valida, ejecuta y devuelve resultados (lista de dicts).
    Lanza LLMError / SQLValidationError / ExecutionError según corresponda.
    """
    sql = translate_question_to_sql_with_llm(question, max_results=max_results)
    logger.info("Executing SQL from LLM (truncated): %.200s", sql)
    try:
        rows = execute_sql(sql)  # execute_sql debe lanzar RuntimeError/Exception en fallos
    except Exception as e:
        logger.exception("Error ejecutando SQL")
        raise ExecutionError("Error al ejecutar la consulta generada.") from e
    return rows
