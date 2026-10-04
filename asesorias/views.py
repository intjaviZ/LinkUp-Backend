from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import AsesorMateriaFilter, AsesoriaFilter, ReseniaFilter
from .permissions import EsDueno
from .repositories import (
    AsesorMateriaRepository,
    AsesorRepository,
    AsesoriaRepository,
    ReseniaRepository,
    SkillRepository,
)
from .serializers import (
    ActualizarAsesorMateriaSerializer,
    AsesorMateriaSerializer,
    AsesorPerfilSerializer,
    AsesoriaSerializer,
    CambioEstadoSerializer,
    CotizacionSerializer,
    CotizarSerializer,
    CrearReseniaSerializer,
    CrearSkillSerializer,
    PublicarAsesorMateriaSerializer,
    ReseniaSerializer,
    SkillSerializer,
    SolicitarAsesoriaSerializer,
)
from .services import AsesorMateriaService, AsesoriaService, ReseniaService, SkillService


class AsesorMateriaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AsesorMateriaSerializer
    filterset_class = AsesorMateriaFilter
    search_fields = ["usuario__nombre", "materia__nombre"]
    ordering_fields = ["precio_hora", "rating_promedio", "materia__nombre"]
    lookup_value_regex = r"\d+"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    repository = AsesorMateriaRepository()
    service = AsesorMateriaService()

    def get_permissions(self):
        if self.action in ("partial_update", "destroy"):
            return [IsAuthenticated(), EsDueno()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return self.repository.visibles_para(self.request.user)

    def filter_queryset(self, queryset):
        # Filtros, búsqueda y orden solo aplican al listado (no al detalle ni a PATCH/DELETE)
        return super().filter_queryset(queryset) if self.action == "list" else queryset

    @extend_schema(request=PublicarAsesorMateriaSerializer, responses={201: AsesorMateriaSerializer})
    def create(self, request):
        serializer = PublicarAsesorMateriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        oferta = self.service.publicar(request.user, **serializer.validated_data)
        return Response(self.get_serializer(oferta).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ActualizarAsesorMateriaSerializer, responses=AsesorMateriaSerializer)
    def partial_update(self, request, pk=None):
        oferta = self.get_object()  # aquí se aplica EsDueno -> 403
        serializer = ActualizarAsesorMateriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        oferta = self.service.actualizar(oferta, **serializer.validated_data)
        return Response(self.get_serializer(oferta).data)

    def destroy(self, request, pk=None):
        self.service.desactivar(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class AsesorViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Perfil público de un asesor: biografía, skills, materias activas y reputación."""
    serializer_class = AsesorPerfilSerializer
    lookup_value_regex = r"\d+"
    repository = AsesorRepository()

    def get_queryset(self):
        return self.repository.perfiles()


class SkillViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Skills del usuario autenticado."""
    serializer_class = SkillSerializer
    pagination_class = None
    lookup_value_regex = r"\d+"
    repository = SkillRepository()
    service = SkillService()

    def get_queryset(self):
        return self.repository.de_usuario(self.request.user)  # solo las propias -> las ajenas dan 404

    @extend_schema(request=CrearSkillSerializer, responses={201: SkillSerializer})
    def create(self, request):
        serializer = CrearSkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        skill = self.service.agregar(request.user, serializer.validated_data["skill"])
        return Response(self.get_serializer(skill).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        self.service.eliminar(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class AsesoriaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AsesoriaSerializer
    filterset_class = AsesoriaFilter
    ordering_fields = ["fecha", "created_at", "precio_total"]
    lookup_value_regex = r"\d+"
    repository = AsesoriaRepository()
    service = AsesoriaService()

    def get_queryset(self):
        return self.repository.de_participante(self.request.user)

    @extend_schema(request=SolicitarAsesoriaSerializer, responses={201: AsesoriaSerializer})
    def create(self, request):
        serializer = SolicitarAsesoriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asesoria = self.service.solicitar(request.user, **serializer.validated_data)
        return Response(self.get_serializer(asesoria).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=CotizarSerializer, responses=CotizacionSerializer)
    @action(detail=False, methods=["post"])
    def cotizar(self, request):
        serializer = CotizarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cotizacion = self.service.cotizar(**serializer.validated_data)
        return Response(CotizacionSerializer(cotizacion).data)

    @extend_schema(request=CambioEstadoSerializer, responses=AsesoriaSerializer)
    @action(detail=True, methods=["patch"], url_path="estado")
    def estado(self, request, pk=None):
        asesoria = self.get_object()  # 404 si no participas
        serializer = CambioEstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asesoria = self.service.cambiar_estado(asesoria.pk, request.user, serializer.validated_data["estado"])
        return Response(self.get_serializer(asesoria).data)


class ReseniaViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ReseniaSerializer
    filterset_class = ReseniaFilter
    ordering_fields = ["created_at", "puntuacion"]
    repository = ReseniaRepository()
    service = ReseniaService()

    def get_queryset(self):
        return self.repository.listar()

    @extend_schema(request=CrearReseniaSerializer, responses={201: ReseniaSerializer})
    def create(self, request):
        serializer = CrearReseniaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resenia = self.service.calificar(request.user, **serializer.validated_data)
        return Response(self.get_serializer(resenia).data, status=status.HTTP_201_CREATED)