from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Exists, OuterRef, Prefetch, Q
from django.db.models.functions import Coalesce

from core.repositories import aplicar_cambios

from .models import AsesorMateria, Asesoria, Resenia, SkillAsesor

User = get_user_model()

# La reputación es del ASESOR: promedio de todas las reseñas de todas sus materias.
RESENIAS_DEL_ASESOR = "usuario__materias_asesoradas__asesorias__resenia"


class AsesorMateriaRepository:
    def _base(self):
        return (
            AsesorMateria.objects
            .select_related("usuario", "materia", "materia__plan_estudiantil")
            .prefetch_related("usuario__skills")
            .annotate(
                rating_promedio=Coalesce(Avg(f"{RESENIAS_DEL_ASESOR}__puntuacion"), 0.0),
                total_resenas=Count(RESENIAS_DEL_ASESOR, distinct=True),
            )
            .order_by("materia__nombre", "precio_hora", "id")
        )

    def visibles_para(self, usuario):
        """Ofertas activas de todos + todas las propias (aunque estén desactivadas)."""
        return self._base().filter(Q(activo=True) | Q(usuario=usuario))

    def get(self, pk):
        return self._base().filter(pk=pk).first()

    def existe(self, usuario_id, materia_id):
        return AsesorMateria.objects.filter(usuario_id=usuario_id, materia_id=materia_id).exists()

    def crear(self, **datos):
        return AsesorMateria.objects.create(**datos)

    def actualizar(self, oferta, **cambios):
        return aplicar_cambios(oferta, **cambios)


class AsesorRepository:
    def perfiles(self):
        """Usuarios que tienen al menos una materia publicada, con su reputación."""
        ofertas_activas = Prefetch(
            "materias_asesoradas",
            queryset=(
                AsesorMateria.objects.filter(activo=True)
                .select_related("materia", "materia__plan_estudiantil")
                .order_by("materia__nombre")
            ),
            to_attr="ofertas_activas",
        )
        return (
            User.objects.filter(is_active=True)
            .filter(Exists(AsesorMateria.objects.filter(usuario=OuterRef("pk"))))
            .select_related("plan_estudiantil")
            .prefetch_related("skills", ofertas_activas)
            .annotate(
                rating_promedio=Coalesce(Avg("materias_asesoradas__asesorias__resenia__puntuacion"), 0.0),
                total_resenas=Count("materias_asesoradas__asesorias__resenia", distinct=True),
            )
        )


class SkillRepository:
    def de_usuario(self, usuario):
        return SkillAsesor.objects.filter(usuario=usuario).order_by("skill")

    def existe(self, usuario, texto):
        return SkillAsesor.objects.filter(usuario=usuario, skill__iexact=texto).exists()

    def crear(self, **datos):
        return SkillAsesor.objects.create(**datos)

    def eliminar(self, skill):
        skill.delete()


class AsesoriaRepository:
    def _base(self):
        return Asesoria.objects.select_related(
            "estudiante", "asesor_materia__usuario", "asesor_materia__materia", "resenia"
        )

    def de_participante(self, usuario):
        return self._base().filter(Q(estudiante=usuario) | Q(asesor_materia__usuario=usuario))

    def get(self, pk):
        return self._base().filter(pk=pk).first()

    def bloquear(self, pk):
        """Fila bloqueada para cambiar de estado sin carreras. Requiere transaction.atomic."""
        return (
            Asesoria.objects.select_for_update(of=("self",))
            .select_related("asesor_materia")
            .get(pk=pk)
        )

    def crear(self, **datos):
        return Asesoria.objects.create(**datos)

    def cambiar_estado(self, asesoria, estado):
        return aplicar_cambios(asesoria, estado=estado)


class ReseniaRepository:
    def listar(self):
        return Resenia.objects.select_related(
            "asesoria__estudiante", "asesoria__asesor_materia__materia"
        ).order_by("-created_at")

    def existe_para(self, asesoria_id):
        return Resenia.objects.filter(asesoria_id=asesoria_id).exists()

    def crear(self, **datos):
        return Resenia.objects.create(**datos)