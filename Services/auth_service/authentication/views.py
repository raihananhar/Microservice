from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

from .authentication import JWTAuthentication
from .permissions import IsUser, IsAdmin
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, LogoutSerializer, PartnerRequestSerializer
from .utils import rate_limit
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@api_view(['POST'])
def register_user(request):
    rate_limit(f"register:{request.META['REMOTE_ADDR']}", limit=5, period=3600)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class PartnerRequestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUser]

    def post(self, request):
        user = User.objects.filter(id=request.user.id).first()

        if user.partner_request_status != 'NONE':
            return Response(
                {"error": "You have already submitted a partner request"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PartnerRequestSerializer(data=request.data)
        if serializer.is_valid():
            user.partner_request_status = 'PENDING'
            user.partner_request_date = timezone.now()

            if 'partner_documents' in serializer.data:
                user.partner_documents = serializer.data['partner_documents']

            user.save()
            return Response({"message": "Partner request submitted successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApprovePartnerRequestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if user.partner_request_status != 'PENDING':
                return Response(
                    {"error": "No pending partner request found for this user"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            action = request.data.get('action')
            if action not in ['approve', 'reject']:
                return Response(
                    {"error": "Invalid action. Use 'approve' or 'reject'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if action == 'approve':
                user.role = 'PARTNER'
                user.partner_request_status = 'APPROVED'
            else:
                user.partner_request_status = 'REJECTED'

            user.save()
            return Response(
                {"message": f"Partner request {action}d successfully"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class ValidateTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.filter(id=request.user.id).first()
        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        })
