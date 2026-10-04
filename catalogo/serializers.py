from rest_framework import serializers

from .models import Materia, PlanEstudiantil


class PlanEstudiantilSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanEstudiantil
        fields = ("id", "carrera", "numero_cuatrimestres")
        read_only_fields = fields


class MateriaSerializer(serializers.ModelSerializer):
    carrera = serializers.CharField(source="plan_estudiantil.carrera", read_only=True, allow_null=True)

    class Meta:
        model = Materia
        fields = ("id", "nombre", "cuatrimestre", "es_tronco_comun", "plan_estudiantil", "carrera")
        read_only_fields = fields