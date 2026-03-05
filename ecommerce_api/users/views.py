from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """POST /api/users/register/  — create a new account"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Auto-generate tokens on registration so user is immediately logged in
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/users/profile/  — view your profile
    PUT  /api/users/profile/  — update username or email
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """POST /api/users/change-password/  — update password"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password updated successfully.'})


class LogoutView(APIView):
    """
    POST /api/users/logout/  — blacklist the refresh token
    Body: { "refresh": "<your_refresh_token>" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except KeyError:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {'error': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserListView(generics.ListAPIView):
    """GET /api/users/  — staff only, list all users"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()