from django.db import models


class Balance(models.Model):
    user_id = models.CharField(max_length=255, unique=True)  # User ID as CharField
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"User {self.user_id} - Balance: {self.amount}"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('topup', 'Top-Up'),
        ('withdraw', 'Withdraw'),
        ('purchase', 'Purchase')
    ]

    user_id = models.CharField(max_length=255)  # User ID as CharField
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    auction_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} - {self.transaction_type.capitalize()} - {self.amount}"
