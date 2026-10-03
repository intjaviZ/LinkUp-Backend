from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("El email es obligatorio")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)  # hashea la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=150)
    # null=True para poder crear el superusuario; el registro los exigirá en el serializer
    plan_estudiantil = models.ForeignKey(
        "catalogo.PlanEstudiantil", on_delete=models.PROTECT,
        related_name="usuarios", null=True, blank=True,
    )
    cuatrimestre_actual = models.PositiveSmallIntegerField(null=True, blank=True)
    biografia = models.TextField(blank=True)  # también hace de descripción del asesor

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]
    objects = UserManager()

    def get_full_name(self):
        return self.nombre

    def get_short_name(self):
        return self.nombre

    def __str__(self):
        return self.email