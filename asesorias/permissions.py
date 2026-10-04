from rest_framework.permissions import BasePermission


class EsDueno(BasePermission):
    message = "Solo el dueño puede modificar este recurso."

    def has_object_permission(self, request, view, obj):
        return obj.usuario_id == request.user.id