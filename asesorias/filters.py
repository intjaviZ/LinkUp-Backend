from django.db.models import Q
from django_filters import rest_framework as filters

from .models import AsesorMateria, Asesoria, Resenia


class AsesorMateriaFilter(filters.FilterSet):
    materia_id = filters.NumberFilter(field_name="materia_id")
    carrera_id = filters.NumberFilter(method="filtrar_carrera")  # plan + tronco común
    cuatrimestre = filters.NumberFilter(field_name="materia__cuatrimestre")
    tronco_comun = filters.BooleanFilter(field_name="materia__es_tronco_comun")
    min_precio = filters.NumberFilter(field_name="precio_hora", lookup_expr="gte")
    max_precio = filters.NumberFilter(field_name="precio_hora", lookup_expr="lte")
    min_rating = filters.NumberFilter(field_name="rating_promedio", lookup_expr="gte")
    mias = filters.BooleanFilter(method="filtrar_mias")
    excluir_propias = filters.BooleanFilter(method="filtrar_excluir_propias")

    class Meta:
        model = AsesorMateria
        fields = []

    def filtrar_carrera(self, queryset, name, value):
        return queryset.filter(Q(materia__plan_estudiantil_id=value) | Q(materia__es_tronco_comun=True))

    def filtrar_mias(self, queryset, name, value):
        return queryset.filter(usuario=self.request.user) if value else queryset

    def filtrar_excluir_propias(self, queryset, name, value):
        return queryset.exclude(usuario=self.request.user) if value else queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if not self.form.cleaned_data.get("mias"):  # el catálogo público solo muestra ofertas activas
            queryset = queryset.filter(activo=True)
        return queryset


class AsesoriaFilter(filters.FilterSet):
    rol = filters.ChoiceFilter(
        choices=[("estudiante", "estudiante"), ("asesor", "asesor")], method="filtrar_rol"
    )
    estado = filters.ChoiceFilter(choices=Asesoria.Estado.choices)

    class Meta:
        model = Asesoria
        fields = []

    def filtrar_rol(self, queryset, name, value):
        usuario = self.request.user
        if value == "estudiante":
            return queryset.filter(estudiante=usuario)
        return queryset.filter(asesor_materia__usuario=usuario)


class ReseniaFilter(filters.FilterSet):
    asesor_id = filters.NumberFilter(field_name="asesoria__asesor_materia__usuario_id")
    asesor_materia_id = filters.NumberFilter(field_name="asesoria__asesor_materia_id")

    class Meta:
        model = Resenia
        fields = []