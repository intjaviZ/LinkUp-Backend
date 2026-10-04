from core.repositories import aplicar_cambios

from .models import User


class UserRepository:
    def email_existe(self, email):
        return User.objects.filter(email__iexact=email).exists()

    def crear(self, *, email, password, **extra):
        return User.objects.create_user(email=email, password=password, **extra)  # hashea

    def actualizar(self, usuario, **cambios):
        return aplicar_cambios(usuario, **cambios)