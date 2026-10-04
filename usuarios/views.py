from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    AuthResponseSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .services import UserService


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # un token vencido no debe bloquear el registro
    service = UserService()

    @extend_schema(request=RegisterSerializer, responses={201: AuthResponseSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.service.registrar(**serializer.validated_data)
        refresh = RefreshToken.for_user(user)
        return Response(
            {"user": UserSerializer(user).data, "access": str(refresh.access_token), "refresh": str(refresh)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class MeView(APIView):
    service = UserService()

    @extend_schema(responses=UserSerializer)
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @extend_schema(request=UserUpdateSerializer, responses=UserSerializer)
    def patch(self, request):
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.service.actualizar_perfil(request.user, **serializer.validated_data)
        return Response(UserSerializer(user).data)