from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

DINERO = dict(max_digits=8, decimal_places=2)  # ajusta aquí si lo necesitas


class AsesorMateria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="materias_asesoradas"
    )
    materia = models.ForeignKey(
        "catalogo.Materia", on_delete=models.CASCADE, related_name="asesores"
    )
    precio_hora = models.DecimalField(**DINERO)
    activo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "materia"], name="uniq_asesor_materia")
        ]

    def __str__(self):
        return f"{self.usuario} - {self.materia}"


class SkillAsesor(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skills"
    )
    skill = models.CharField(max_length=100)

    def __str__(self):
        return self.skill


class Asesoria(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ACEPTADA = "ACEPTADA", "Aceptada"
        FINALIZADA = "FINALIZADA", "Finalizada"
        CANCELADA = "CANCELADA", "Cancelada"

    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="asesorias_solicitadas"
    )
    asesor_materia = models.ForeignKey(
        AsesorMateria, on_delete=models.PROTECT, related_name="asesorias"
    )
    fecha = models.DateTimeField()
    horas = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    precio_hora = models.DecimalField(**DINERO)           # congela el costo pactado
    monto_base = models.DecimalField(**DINERO)            # precio_hora * horas
    comision_plataforma = models.DecimalField(**DINERO)   # % de monto_base
    precio_total = models.DecimalField(**DINERO)          # monto_base + comisión
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Asesoría #{self.pk} ({self.estado})"


class Resenia(models.Model):
    asesoria = models.OneToOneField(
        Asesoria, on_delete=models.CASCADE, related_name="resenia"
    )
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de asesoría #{self.asesoria_id}: {self.puntuacion}★"