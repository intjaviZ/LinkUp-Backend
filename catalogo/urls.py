from rest_framework.routers import SimpleRouter

from .views import CarreraViewSet, MateriaViewSet

router = SimpleRouter()
router.register("carreras", CarreraViewSet, basename="carrera")
router.register("materias", MateriaViewSet, basename="materia")

urlpatterns = router.urls