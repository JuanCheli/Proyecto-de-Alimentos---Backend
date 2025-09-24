from pydantic import BaseModel
from typing import Optional

# --- Base para todos los alimentos ---
class AlimentoBase(BaseModel):
    nombre_del_alimento: str
    energ_kcal: Optional[float] = None
    carbohydrt: Optional[float] = None
    lipid_tot: Optional[float] = None
    protein: Optional[float] = None
    fiber_td: Optional[float] = None
    calcium: Optional[float] = None
    iron: Optional[float] = None
    ironhem: Optional[float] = None
    ironnohem: Optional[float] = None
    zinc: Optional[float] = None
    vit_c: Optional[float] = None
    thiamin: Optional[float] = None
    riboflavin: Optional[float] = None
    niacin: Optional[float] = None
    panto_acid: Optional[float] = None
    vit_b6: Optional[float] = None
    folic_acid: Optional[float] = None
    food_folate: Optional[float] = None
    folate_dfe: Optional[float] = None
    vit_b12: Optional[float] = None
    vit_a_rae: Optional[float] = None
    vit_e: Optional[float] = None
    vit_d_iu: Optional[float] = None
    vit_k: Optional[float] = None
    fa_sat: Optional[float] = None
    fa_mono: Optional[float] = None
    fa_poly: Optional[float] = None
    chole: Optional[float] = None

# --- Para creación ---
class AlimentoCreate(AlimentoBase):
    pass

# --- Para lectura ---
class AlimentoRead(AlimentoBase):
    codigomex2: int

    class Config:
        orm_mode = True

# --- Para filtrar alimentos ---
class AlimentoFilter(BaseModel):
    max_calorias: Optional[float] = None
    min_calorias: Optional[float] = None
    max_carbohidratos: Optional[float] = None
    min_carbohidratos: Optional[float] = None
    max_proteina: Optional[float] = None
    min_proteina: Optional[float] = None
    max_lipidos: Optional[float] = None
    min_lipidos: Optional[float] = None
