from django.urls import path, include
from .views import (
    CustomTokenObtainPairView, register_user, LogoutView, PartnerRequestView, ApprovePartnerRequestView, ValidateTokenView
)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', register_user, name='register_user'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('partner-request/', PartnerRequestView.as_view(), name='partner-request'),
    path('approve-partner/<int:user_id>/', ApprovePartnerRequestView.as_view(), name='approve-partner'),
    path('validate-token/', ValidateTokenView.as_view(), name='validate_token'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]