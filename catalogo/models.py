from django.core.exceptions import ValidationError
from django.db import models


class PlanEstudiantil(models.Model):
    carrera = models.CharField(max_length=150)
    numero_cuatrimestres = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = "planes estudiantiles"

    def __str__(self):
        return self.carrera


class Materia(models.Model):
    nombre = models.CharField(max_length=150)
    cuatrimestre = models.PositiveSmallIntegerField()
    es_tronco_comun = models.BooleanField(default=False)
    plan_estudiantil = models.ForeignKey(
        PlanEstudiantil, on_delete=models.PROTECT,
        related_name="materias", null=True, blank=True,  # null si es tronco común
    )

    def clean(self):
        if self.es_tronco_comun and self.plan_estudiantil_id:
            raise ValidationError("Una materia de tronco común no pertenece a un solo plan.")
        if not self.es_tronco_comun and not self.plan_estudiantil_id:
            raise ValidationError("Una materia de especialidad requiere un plan.")

    def __str__(self):
        return f"{self.nombre} (cuat. {self.cuatrimestre})"