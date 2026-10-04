from enum import Enum

from .models import Asesoria

Estado = Asesoria.Estado


class Rol(str, Enum):
    ESTUDIANTE = "estudiante"
    ASESOR = "asesor"


# estado actual -> {estado destino: roles que pueden hacer el cambio}
TRANSICIONES = {
    Estado.PENDIENTE: {
        Estado.ACEPTADA: {Rol.ASESOR},
        Estado.CANCELADA: {Rol.ESTUDIANTE, Rol.ASESOR},
    },
    Estado.ACEPTADA: {
        Estado.FINALIZADA: {Rol.ASESOR},
        Estado.CANCELADA: {Rol.ESTUDIANTE, Rol.ASESOR},
    },
    # FINALIZADA y CANCELADA son terminales
}


def rol_en(asesoria, usuario):
    if asesoria.estudiante_id == usuario.id:
        return Rol.ESTUDIANTE
    if asesoria.asesor_materia.usuario_id == usuario.id:
        return Rol.ASESOR
    return None


def transiciones_para(asesoria, usuario):
    """Estados a los que `usuario` puede mover la asesoría (el front los usa para pintar botones)."""
    rol = rol_en(asesoria, usuario)
    destinos = TRANSICIONES.get(asesoria.estado, {})
    return [estado.value for estado, roles in destinos.items() if rol in roles]