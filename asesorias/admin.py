from django.contrib import admin

from .models import AsesorMateria, Asesoria, Resenia, SkillAsesor
from .services import calcular_montos


@admin.register(AsesorMateria)
class AsesorMateriaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "materia", "precio_hora", "activo")
    list_filter = ("activo", "materia__plan_estudiantil")
    search_fields = ("usuario__nombre", "usuario__email", "materia__nombre")


@admin.register(SkillAsesor)
class SkillAsesorAdmin(admin.ModelAdmin):
    list_display = ("usuario", "skill")
    search_fields = ("skill", "usuario__nombre")


@admin.register(Asesoria)
class AsesoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "estudiante", "asesor_materia", "fecha", "horas", "precio_total", "estado")
    list_filter = ("estado",)
    readonly_fields = ("precio_hora", "monto_base", "comision_plataforma", "precio_total", "created_at")

    def save_model(self, request, obj, form, change):
        if not change:  # al crear, calcula los montos igual que lo hará la API
            for campo, valor in calcular_montos(obj.asesor_materia.precio_hora, obj.horas).items():
                setattr(obj, campo, valor)
        super().save_model(request, obj, form, change)


@admin.register(Resenia)
class ReseniaAdmin(admin.ModelAdmin):
    list_display = ("asesoria", "puntuacion", "created_at")