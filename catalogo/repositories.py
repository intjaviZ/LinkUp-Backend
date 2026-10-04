from .models import Materia, PlanEstudiantil


class PlanEstudiantilRepository:
    def listar(self):
        return PlanEstudiantil.objects.order_by("carrera")


class MateriaRepository:
    def listar(self):
        return Materia.objects.select_related("plan_estudiantil").order_by("cuatrimestre", "nombre")