from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from catalogo.models import PlanEstudiantil

from .models import User


# ---- Salida ----
class UserSerializer(serializers.ModelSerializer):
    carrera = serializers.CharField(source="plan_estudiantil.carrera", read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ("id", "email", "nombre", "plan_estudiantil", "carrera", "cuatrimestre_actual", "biografia")


class AuthResponseSerializer(serializers.Serializer):  # solo documentación del register
    user = UserSerializer()
    access = serializers.CharField()
    refresh = serializers.CharField()


class LoginSerializer(TokenObtainPairSerializer):
    """Login con email + password; además de los tokens devuelve el usuario."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


# ---- Entrada ----
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    nombre = serializers.CharField(max_length=150)
    plan_estudiantil = serializers.PrimaryKeyRelatedField(queryset=PlanEstudiantil.objects.all())
    cuatrimestre_actual = serializers.IntegerField(min_value=1)
    biografia = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate_email(self, value):
        return value.lower()

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value


class UserUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150, required=False)
    biografia = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    cuatrimestre_actual = serializers.IntegerField(min_value=1, required=False)