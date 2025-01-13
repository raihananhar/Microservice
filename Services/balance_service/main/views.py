from decimal import Decimal

import jwt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import JWTAuthentication
from .models import Balance, Transaction
from .serializers import BalanceSerializer, TransactionSerializer, TopUpSerializer, WithdrawSerializer
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.shortcuts import get_object_or_404


def get_user_id_from_token(request):
    # Assuming Authorization: Bearer <token>
    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    return decoded['user_id']


class TopUpView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TopUpSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            user_id = get_user_id_from_token(request)  # Get user_id from JWT
            balance, created = Balance.objects.get_or_create(user_id=user_id)
            balance.amount += amount
            balance.save()

            Transaction.objects.create(user_id=user_id, transaction_type='topup', amount=amount)
            return Response({'message': 'Top-up successful', 'new_balance': balance.amount}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            user_id = get_user_id_from_token(request)  # Get user_id from JWT
            balance = get_object_or_404(Balance, user_id=user_id)
            if balance.amount >= Decimal(amount):
                balance.amount -= Decimal(amount)
                balance.save()

                Transaction.objects.create(user_id=user_id, transaction_type='withdraw', amount=amount)
                return Response({'message': 'Withdrawal successful', 'new_balance': balance.amount}, status=status.HTTP_200_OK)
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionHistoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = get_user_id_from_token(request)  # Get user_id from JWT
        transactions = Transaction.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckBalanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = get_user_id_from_token(request)  # Get user_id from JWT
        balance = get_object_or_404(Balance, user_id=user_id)
        return Response({'balance': balance.amount}, status=status.HTTP_200_OK)


class DeductBalanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get("user_id")
        deduction_amount = request.data.get("amount")
        auction_id = request.data.get('auction_id')

        balance = Balance.objects.filter(user_id=user_id).first()
        if not balance:
            return Response(
                {"error": "user balance not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if Decimal(balance.amount) < Decimal(deduction_amount):
            return Response(
                {"error": "insufficient balance "+str(deduction_amount)+" - "+str(balance.amount)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduct the balance
        balance.amount -= Decimal(deduction_amount)
        balance.save()

        Transaction.objects.create(user_id=user_id, transaction_type='purchase', amount=deduction_amount, auction_id=auction_id)
        return Response({"message": "Balance deducted successfully"}, status=status.HTTP_200_OK)