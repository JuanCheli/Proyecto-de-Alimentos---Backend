'''
Modelo creado principalmente por buenas practicas, en caso de que a futuro se quieran realizar migraciones o en caso de logica avanzada/compleja, pero no lo vamos a utilizar
'''


from sqlalchemy import Column, Text, BigInteger, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Alimento(Base):
    __tablename__ = "alimentos"

    # PK codigomex2
    codigomex2 = Column(BigInteger, primary_key=True, index=True, nullable=False)

    # nombre del alimento en texto
    nombre_del_alimento = Column(Text, nullable=False)

    # Valores nutricionales de tipo numeric
    energ_kcal = Column(Numeric(12, 4))
    carbohydrt = Column(Numeric(12, 4))
    lipid_tot = Column(Numeric(12, 4))
    protein = Column(Numeric(12, 4))
    fiber_td = Column(Numeric(12, 4))
    calcium = Column(Numeric(12, 4))
    iron = Column(Numeric(12, 4))
    ironhem = Column(Numeric(12, 4))
    ironnohem = Column(Numeric(12, 4))
    zinc = Column(Numeric(12, 4))
    vit_c = Column(Numeric(12, 4))
    thiamin = Column(Numeric(12, 4))
    riboflavin = Column(Numeric(12, 4))
    niacin = Column(Numeric(12, 4))
    panto_acid = Column(Numeric(12, 4))
    vit_b6 = Column(Numeric(12, 4))
    folic_acid = Column(Numeric(12, 4))
    food_folate = Column(Numeric(12, 4))
    folate_dfe = Column(Numeric(12, 4))
    vit_b12 = Column(Numeric(12, 4))
    vit_a_rae = Column(Numeric(12, 4))
    vit_e = Column(Numeric(12, 4))
    vit_d_iu = Column(Numeric(12, 4))
    vit_k = Column(Numeric(12, 4))
    fa_sat = Column(Numeric(12, 4))
    fa_mono = Column(Numeric(12, 4))
    fa_poly = Column(Numeric(12, 4))
    chole = Column(Numeric(12, 4))

    def __repr__(self):
        return f"<Alimento(codigomex2={self.codigomex2}, nombre='{self.nombre_del_alimento}')>"
