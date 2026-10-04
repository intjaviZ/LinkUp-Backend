from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from core.exceptions import (
    AlreadyExists,
    Conflict,
    ForbiddenAction,
    InvalidStateTransition,
    ValidationFailed,
)

from . import domain
from .models import Asesoria
from .repositories import (
    AsesorMateriaRepository,
    AsesoriaRepository,
    ReseniaRepository,
    SkillRepository,
)

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


class AsesorMateriaService:
    def __init__(self, ofertas=None):
        self.ofertas = ofertas or AsesorMateriaRepository()

    def publicar(self, usuario, materia, precio_hora):
        if self.ofertas.existe(usuario.id, materia.id):
            raise AlreadyExists("Ya registraste esta materia. Edítala o reactívala con PATCH.")
        oferta = self.ofertas.crear(usuario=usuario, materia=materia, precio_hora=precio_hora)
        return self.ofertas.get(oferta.pk)  # recarga con rating y relaciones

    def actualizar(self, oferta, **cambios):
        self.ofertas.actualizar(oferta, **cambios)
        return self.ofertas.get(oferta.pk)

    def desactivar(self, oferta):
        self.ofertas.actualizar(oferta, activo=False)


class SkillService:
    def __init__(self, skills=None):
        self.skills = skills or SkillRepository()

    def agregar(self, usuario, texto):
        texto = " ".join(texto.split())
        if self.skills.existe(usuario, texto):
            raise AlreadyExists("Ya tienes registrada esa skill.")
        return self.skills.crear(usuario=usuario, skill=texto)

    def eliminar(self, skill):
        self.skills.eliminar(skill)


class AsesoriaService:
    def __init__(self, asesorias=None, ahora=timezone.now):
        self.asesorias = asesorias or AsesoriaRepository()
        self.ahora = ahora  # inyectable para tests

    def cotizar(self, asesor_materia, horas):
        self._validar_disponible(asesor_materia)
        montos = calcular_montos(asesor_materia.precio_hora, horas)
        return {**montos, "horas": horas, "porcentaje_comision": settings.COMISION_PLATAFORMA * 100}

    def solicitar(self, estudiante, asesor_materia, fecha, horas):
        self._validar_disponible(asesor_materia)
        if asesor_materia.usuario_id == estudiante.id:
            raise ValidationFailed(details={
                "asesor_materia": ["No puedes solicitarte una asesoría a ti mismo."]
            })
        if fecha <= self.ahora():
            raise ValidationFailed(details={"fecha": ["La fecha debe ser futura."]})

        # El precio SIEMPRE sale de la oferta, nunca del cliente
        montos = calcular_montos(asesor_materia.precio_hora, horas)
        asesoria = self.asesorias.crear(
            estudiante=estudiante, asesor_materia=asesor_materia, fecha=fecha, horas=horas, **montos
        )
        return self.asesorias.get(asesoria.pk)

    @transaction.atomic
    def cambiar_estado(self, asesoria_id, actor, nuevo_estado):
        asesoria = self.asesorias.bloquear(asesoria_id)

        rol = domain.rol_en(asesoria, actor)
        if rol is None:
            raise ForbiddenAction("No participas en esta asesoría.")

        roles_autorizados = domain.TRANSICIONES.get(asesoria.estado, {}).get(nuevo_estado)
        if roles_autorizados is None:
            raise InvalidStateTransition(f"No se puede pasar de {asesoria.estado} a {nuevo_estado}.")
        if rol not in roles_autorizados:
            raise ForbiddenAction(f"Como {rol.value} no puedes cambiar la asesoría a {nuevo_estado}.")

        self.asesorias.cambiar_estado(asesoria, nuevo_estado)
        return self.asesorias.get(asesoria.pk)

    @staticmethod
    def _validar_disponible(asesor_materia):
        if not asesor_materia.activo:
            raise Conflict("Este asesor ya no ofrece esta materia.", code="offer_inactive")


class ReseniaService:
    def __init__(self, resenias=None):
        self.resenias = resenias or ReseniaRepository()

    def calificar(self, estudiante, asesoria, puntuacion, comentario=""):
        if asesoria.estudiante_id != estudiante.id:
            raise ForbiddenAction("Solo el estudiante de la asesoría puede calificarla.")
        if asesoria.estado != Asesoria.Estado.FINALIZADA:
            raise Conflict("Solo puedes calificar asesorías FINALIZADAS.", code="asesoria_not_finalized")
        if self.resenias.existe_para(asesoria.pk):
            raise AlreadyExists("Esta asesoría ya fue calificada.")
        return self.resenias.crear(asesoria=asesoria, puntuacion=puntuacion, comentario=comentario)