from core.exceptions import AlreadyExists, ValidationFailed

from .repositories import UserRepository


class UserService:
    def __init__(self, users=None):
        self.users = users or UserRepository()

    def registrar(self, *, email, password, nombre, plan_estudiantil, cuatrimestre_actual, biografia=""):
        self._validar_cuatrimestre(plan_estudiantil, cuatrimestre_actual)
        if self.users.email_existe(email):
            raise AlreadyExists("Ya existe una cuenta con ese email.")
        return self.users.crear(
            email=email,
            password=password,
            nombre=nombre,
            plan_estudiantil=plan_estudiantil,
            cuatrimestre_actual=cuatrimestre_actual,
            biografia=biografia,
        )

    def actualizar_perfil(self, usuario, **cambios):
        if "cuatrimestre_actual" in cambios:
            self._validar_cuatrimestre(usuario.plan_estudiantil, cambios["cuatrimestre_actual"])
        return self.users.actualizar(usuario, **cambios)

    @staticmethod
    def _validar_cuatrimestre(plan, cuatrimestre):
        if plan and cuatrimestre > plan.numero_cuatrimestres:
            raise ValidationFailed(details={
                "cuatrimestre_actual": [f"La carrera tiene {plan.numero_cuatrimestres} cuatrimestres."]
            })