from rest_framework import serializers
from .models import Item, Auction


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'owner_id']


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['id', 'item', 'starting_price', 'reserve_price', 'bid_price', 'buy_it_now_price', 'start_time', 'end_time', 'owner_id', 'status']
