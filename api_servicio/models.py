import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from itertools import cycle

def validar_rut_chileno(value):
    # 1. Limpieza total y normalización
    rut = str(value).upper().replace("-", "").replace(".", "").strip()
    
    # 2. Validación de formato básico (7 u 8 números + 1 dígito/K)
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        raise ValidationError("Formato de RUT inválido. Solo números y termina en dígito o 'K'.")
    
    cuerpo = rut[:-1]
    dv_ingresado = rut[-1]
    
    # Cálculo del Módulo 11
    reverso = map(int, reversed(cuerpo))
    factores = cycle([2, 3, 4, 5, 6, 7])
    suma = sum(d * f for d, f in zip(reverso, factores))
    residuos = 11 - (suma % 11)
    
    if residuos == 11:
        dv_esperado = "0"
    elif residuos == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(residuos)
    
    if dv_ingresado != dv_esperado:
        raise ValidationError(f"El RUT ingresado no es válido (Dígito verificador incorrecto).")
    
    return value

class Usuario(AbstractUser):
    rut = models.CharField(
        max_length=12, 
        unique=True, 
        validators=[validar_rut_chileno],
        help_text="Formato: 12345678-K o 12345678K"
    )

    def __str__(self):
        return f"{self.username} ({self.rut})"