from django.db import models
from django.utils import timezone
# Create your models here.

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Auction(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    status = models.CharField(max_length=255, default='PENDING')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reserve_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    winner_id = models.CharField(max_length=255, null=True, blank=True)  # Store user ID from the user service
    winner_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    buy_it_now_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field for BIN
    owner_id = models.CharField(max_length=255, null=True, blank=True)

    def is_active(self):
        return self.status == 'APPROVED' and (self.start_time <= timezone.now() <= self.end_time)

    def is_buy_it_now(self):
        return self.buy_it_now_price is not None

    def __str__(self):
        return f"Auction for {self.item.name}"


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    user_id = models.CharField(max_length=255)  # Store user ID from the user service
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('auction', 'user_id', 'amount')  # Prevent duplicate bids of the same amount

    def __str__(self):
        return f"Bid by User ID {self.user_id} for {self.auction.item.name}: {self.amount}"
