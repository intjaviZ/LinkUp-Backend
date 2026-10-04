from rest_framework.routers import SimpleRouter

from .views import (
    AsesorMateriaViewSet,
    AsesorViewSet,
    AsesoriaViewSet,
    ReseniaViewSet,
    SkillViewSet,
)

router = SimpleRouter()
router.register("asesor-materias", AsesorMateriaViewSet, basename="asesor-materia")
router.register("asesores", AsesorViewSet, basename="asesor")
router.register("skills", SkillViewSet, basename="skill")
router.register("asesorias", AsesoriaViewSet, basename="asesoria")
router.register("resenas", ReseniaViewSet, basename="resenia")

urlpatterns = router.urls