from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Materia


class MateriaFilter(filters.FilterSet):
    # carrera_id devuelve las materias de esa carrera MÁS las de tronco común
    carrera_id = filters.NumberFilter(method="filtrar_carrera")
    tronco_comun = filters.BooleanFilter(field_name="es_tronco_comun")
    cuatrimestre = filters.NumberFilter(field_name="cuatrimestre")

    class Meta:
        model = Materia
        fields = []

    def filtrar_carrera(self, queryset, name, value):
        return queryset.filter(Q(plan_estudiantil_id=value) | Q(es_tronco_comun=True))