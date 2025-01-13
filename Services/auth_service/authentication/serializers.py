from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='USER'  # Default role is USER
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_role'] = user.role  # Assuming your user model has a role field
        token['partner_request_status'] = user.partner_request_status

        return token

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])

        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(self.get_token(user)),
            'user': UserSerializer(user).data
        }

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh_token']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError('Bad token')

class PartnerRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['partner_documents']