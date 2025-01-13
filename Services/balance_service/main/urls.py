from django.urls import path
from .views import TopUpView, WithdrawView, TransactionHistoryView, CheckBalanceView, DeductBalanceView

urlpatterns = [
    path('top-up/', TopUpView.as_view(), name='top_up'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('transactions/', TransactionHistoryView.as_view(), name='transaction_history'),
    path('check-balance/', CheckBalanceView.as_view(), name='check_balance'),
    path('deduct-balance/', DeductBalanceView.as_view(), name='deduct_balance'),

]
