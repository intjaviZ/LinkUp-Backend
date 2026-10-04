from decimal import Decimal

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from catalogo.models import Materia
from catalogo.serializers import MateriaSerializer

from . import domain
from .models import DINERO, AsesorMateria, Asesoria, Resenia, SkillAsesor

User = get_user_model()


# ===================== Salida =====================
class ReputacionMixin(serializers.Serializer):
    rating_promedio = serializers.SerializerMethodField()
    total_resenas = serializers.IntegerField(read_only=True)

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_rating_promedio(self, obj):
        if not obj.total_resenas:
            return None  # sin reseñas = sin promedio
        return round(float(obj.rating_promedio), 2)


class UsuarioResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "nombre")


class AsesorResumenSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(many=True, read_only=True, slug_field="skill")

    class Meta:
        model = User
        fields = ("id", "nombre", "biografia", "skills")


class AsesorMateriaSerializer(ReputacionMixin, serializers.ModelSerializer):
    asesor = AsesorResumenSerializer(source="usuario", read_only=True)
    materia = MateriaSerializer(read_only=True)

    class Meta:
        model = AsesorMateria
        fields = ("id", "asesor", "materia", "precio_hora", "activo", "rating_promedio", "total_resenas")


class OfertaResumenSerializer(serializers.ModelSerializer):
    materia = MateriaSerializer(read_only=True)

    class Meta:
        model = AsesorMateria
        fields = ("id", "materia", "precio_hora")


class AsesorPerfilSerializer(ReputacionMixin, serializers.ModelSerializer):
    carrera = serializers.CharField(source="plan_estudiantil.carrera", read_only=True, allow_null=True)
    skills = serializers.SlugRelatedField(many=True, read_only=True, slug_field="skill")
    materias = OfertaResumenSerializer(source="ofertas_activas", many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "nombre", "biografia", "carrera", "cuatrimestre_actual",
            "skills", "materias", "rating_promedio", "total_resenas",
        )


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillAsesor
        fields = ("id", "skill")


class ReseniaBasicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resenia
        fields = ("id", "puntuacion", "comentario", "created_at")


class ReseniaSerializer(ReseniaBasicaSerializer):
    estudiante = UsuarioResumenSerializer(source="asesoria.estudiante", read_only=True)
    materia = serializers.CharField(source="asesoria.asesor_materia.materia.nombre", read_only=True)

    class Meta(ReseniaBasicaSerializer.Meta):
        fields = ReseniaBasicaSerializer.Meta.fields + ("asesoria", "estudiante", "materia")


class AsesoriaSerializer(serializers.ModelSerializer):
    estudiante = UsuarioResumenSerializer(read_only=True)
    asesor = UsuarioResumenSerializer(source="asesor_materia.usuario", read_only=True)
    materia = MateriaSerializer(source="asesor_materia.materia", read_only=True)
    resenia = ReseniaBasicaSerializer(read_only=True, allow_null=True)
    mi_rol = serializers.SerializerMethodField()
    transiciones_permitidas = serializers.SerializerMethodField()
    puede_resenar = serializers.SerializerMethodField()

    class Meta:
        model = Asesoria
        fields = (
            "id", "estudiante", "asesor", "asesor_materia", "materia", "fecha", "horas",
            "precio_hora", "monto_base", "comision_plataforma", "precio_total",
            "estado", "created_at", "resenia",
            "mi_rol", "transiciones_permitidas", "puede_resenar",
        )
        read_only_fields = fields

    def _usuario(self):
        return self.context["request"].user

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_mi_rol(self, obj):
        rol = domain.rol_en(obj, self._usuario())
        return rol.value if rol else None

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_transiciones_permitidas(self, obj):
        return domain.transiciones_para(obj, self._usuario())

    @extend_schema_field(serializers.BooleanField())
    def get_puede_resenar(self, obj):
        return (
            obj.estado == Asesoria.Estado.FINALIZADA
            and obj.estudiante_id == self._usuario().id
            and not hasattr(obj, "resenia")
        )


class CotizacionSerializer(serializers.Serializer):
    horas = serializers.IntegerField()
    precio_hora = serializers.DecimalField(**DINERO)
    monto_base = serializers.DecimalField(**DINERO)
    comision_plataforma = serializers.DecimalField(**DINERO)
    precio_total = serializers.DecimalField(**DINERO)
    porcentaje_comision = serializers.DecimalField(max_digits=5, decimal_places=2)


# ===================== Entrada =====================
class PublicarAsesorMateriaSerializer(serializers.Serializer):
    materia = serializers.PrimaryKeyRelatedField(queryset=Materia.objects.all())
    precio_hora = serializers.DecimalField(**DINERO, min_value=Decimal("1"))


class ActualizarAsesorMateriaSerializer(serializers.Serializer):
    precio_hora = serializers.DecimalField(**DINERO, min_value=Decimal("1"), required=False)
    activo = serializers.BooleanField(required=False)


class CrearSkillSerializer(serializers.Serializer):
    skill = serializers.CharField(max_length=100)


class SolicitarAsesoriaSerializer(serializers.Serializer):
    asesor_materia = serializers.PrimaryKeyRelatedField(queryset=AsesorMateria.objects.select_related("usuario"))
    fecha = serializers.DateTimeField()
    horas = serializers.IntegerField(min_value=1, max_value=12)


class CotizarSerializer(serializers.Serializer):
    asesor_materia = serializers.PrimaryKeyRelatedField(queryset=AsesorMateria.objects.select_related("usuario"))
    horas = serializers.IntegerField(min_value=1, max_value=12)


class CambioEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Asesoria.Estado.choices)


class CrearReseniaSerializer(serializers.Serializer):
    asesoria = serializers.PrimaryKeyRelatedField(queryset=Asesoria.objects.all())
    puntuacion = serializers.IntegerField(min_value=1, max_value=5)
    comentario = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")