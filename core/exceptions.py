import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.db import IntegrityError
from django.http import Http404
from rest_framework import exceptions as drf
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


# ---------- Excepciones de dominio (los services las lanzan, no conocen DRF) ----------
class DomainError(Exception):
    status_code = 400
    code = "domain_error"
    message = "No se pudo completar la operación."

    def __init__(self, message=None, *, code=None, details=None):
        self.message = message or self.message
        self.code = code or self.code
        self.details = details
        super().__init__(self.message)


class ValidationFailed(DomainError):
    status_code = 400
    code = "validation_error"
    message = "Los datos enviados no son válidos."


class ForbiddenAction(DomainError):
    status_code = 403
    code = "permission_denied"
    message = "No tienes permiso para realizar esta acción."


class ResourceNotFound(DomainError):
    status_code = 404
    code = "not_found"
    message = "El recurso solicitado no existe."


class Conflict(DomainError):
    status_code = 409
    code = "conflict"
    message = "La operación entra en conflicto con el estado actual del recurso."


class AlreadyExists(Conflict):
    code = "already_exists"
    message = "El recurso ya existe."


class InvalidStateTransition(Conflict):
    code = "invalid_state_transition"
    message = "La transición de estado no es válida."


# ---------- Formato único de error ----------
# {"error": {"status": 401, "code": "...", "message": "...", "details": {...}}}
def _cuerpo(status_code, code, message, details=None):
    error = {"status": status_code, "code": code, "message": message}
    if details:
        error["details"] = details
    return {"error": error}


_ERRORES_DRF = (
    (drf.ValidationError, "validation_error", "Los datos enviados no son válidos."),
    (drf.ParseError, "parse_error", "El cuerpo de la petición está mal formado."),
    (drf.NotAuthenticated, "not_authenticated",
     "Falta el token. Envía el header Authorization: Bearer <access>."),
    (drf.AuthenticationFailed, "authentication_failed", "Credenciales o token inválidos o expirados."),
    (drf.PermissionDenied, "permission_denied", "No tienes permiso para realizar esta acción."),
    (drf.NotFound, "not_found", "El recurso solicitado no existe."),
    (drf.MethodNotAllowed, "method_not_allowed", "Método no permitido en este endpoint."),
    (drf.UnsupportedMediaType, "unsupported_media_type", "Tipo de contenido no soportado."),
    (drf.Throttled, "throttled", "Demasiadas peticiones. Intenta más tarde."),
)


def _resolver(exc):
    for clase, codigo, mensaje in _ERRORES_DRF:
        if isinstance(exc, clase):
            return codigo, mensaje
    return "api_error", "Ocurrió un error al procesar la petición."


def _mensaje(exc, por_defecto):
    """Usa el mensaje propio de la excepción si lo trae; si no, el de la tabla."""
    detalle = getattr(exc, "detail", None)
    if isinstance(detalle, str) and str(detalle) != str(getattr(exc, "default_detail", "")):
        return str(detalle)
    return por_defecto


def _codigo_autenticacion(exc, data):
    """Conserva códigos de SimpleJWT como 'token_not_valid' para que el front sepa cuándo refrescar."""
    if isinstance(data, dict) and isinstance(data.get("code"), str):
        return str(data["code"])
    codes = exc.get_codes()
    return codes if isinstance(codes, str) else None


def _dar_formato(exc, response):
    codigo, mensaje = _resolver(exc)
    detalles = None
    if isinstance(exc, drf.ValidationError):
        data = response.data
        detalles = data if isinstance(data, dict) else {"non_field_errors": data}
    else:
        mensaje = _mensaje(exc, mensaje)
        if isinstance(exc, drf.AuthenticationFailed):
            codigo = _codigo_autenticacion(exc, response.data) or codigo
    response.data = _cuerpo(response.status_code, codigo, mensaje, detalles)
    return response  # conserva headers como WWW-Authenticate en los 401


def api_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return Response(
            _cuerpo(exc.status_code, exc.code, exc.message, exc.details),
            status=exc.status_code,
        )

    if isinstance(exc, IntegrityError):  # red de seguridad ante condiciones de carrera
        logger.warning("IntegrityError: %s", exc)
        return Response(
            _cuerpo(409, "integrity_error", "La operación entra en conflicto con datos existentes."),
            status=409,
        )

    if isinstance(exc, Http404):
        exc = drf.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = drf.PermissionDenied()

    response = drf_exception_handler(exc, context)
    if response is None:  # error no previsto
        logger.error("Error no controlado en %s", context.get("view"), exc_info=exc)
        return Response(_cuerpo(500, "server_error", "Error interno del servidor."), status=500)

    return _dar_formato(exc, response)