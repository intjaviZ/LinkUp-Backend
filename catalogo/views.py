from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .filters import MateriaFilter
from .repositories import MateriaRepository, PlanEstudiantilRepository
from .serializers import MateriaSerializer, PlanEstudiantilSerializer


class CarreraViewSet(viewsets.ReadOnlyModelViewSet):
    """Público: el registro lo necesita antes de tener token."""
    serializer_class = PlanEstudiantilSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None
    lookup_value_regex = r"\d+"
    repository = PlanEstudiantilRepository()

    def get_queryset(self):
        return self.repository.listar()


class MateriaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MateriaSerializer
    filterset_class = MateriaFilter
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "cuatrimestre"]
    lookup_value_regex = r"\d+"
    repository = MateriaRepository()

    def get_queryset(self):
        return self.repository.listar()