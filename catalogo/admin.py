from django.contrib import admin

from .models import Materia, PlanEstudiantil


@admin.register(PlanEstudiantil)
class PlanEstudiantilAdmin(admin.ModelAdmin):
    list_display = ("carrera", "numero_cuatrimestres")


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cuatrimestre", "es_tronco_comun", "plan_estudiantil")
    list_filter = ("es_tronco_comun", "plan_estudiantil", "cuatrimestre")
    search_fields = ("nombre",)