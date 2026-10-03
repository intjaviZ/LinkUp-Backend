from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings

CENTAVOS = Decimal("0.01")


def calcular_montos(precio_hora, horas):
    precio_hora = Decimal(precio_hora)
    base = (precio_hora * horas).quantize(CENTAVOS, ROUND_HALF_UP)
    comision = (base * settings.COMISION_PLATAFORMA).quantize(CENTAVOS, ROUND_HALF_UP)
    return {
        "precio_hora": precio_hora,
        "monto_base": base,
        "comision_plataforma": comision,
        "precio_total": base + comision,
    }