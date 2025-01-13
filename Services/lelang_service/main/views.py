from decimal import Decimal

import requests
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.db import IntegrityError
from lelang_service import settings
from .models import Auction, Bid, Item
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .permissions import IsUser, IsPartner, IsAdmin, IsPartnerOrUser  # Import the custom permission
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ItemSerializer, AuctionSerializer
from .authentication import JWTAuthentication  # Import your custom class

class AuctionListView(View):
    def get(self, request):
        auctions = Auction.objects.filter(status='APPROVED')
        data = [
            {
                "id": auction.id,
                "item": auction.item.name,
                "starting_price": auction.starting_price,
                "reserve_price": auction.reserve_price,
                "bid_price": auction.bid_price,
                "buy_it_now_price": auction.buy_it_now_price,
                "start_time": auction.start_time,
                "end_time": auction.end_time,
                "status": auction.status,
                "winner_id": auction.winner_id
            }
            for auction in auctions]
        return JsonResponse(data, safe=False)

class AuctionDetailView(View):
    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        data = {
            "id": auction.id,
            "item": auction.item.name,
            "description": auction.item.description,
            "starting_price": auction.starting_price,
            "reserve_price": auction.reserve_price,
            "bid_price": auction.bid_price,
            "buy_it_now_price": auction.buy_it_now_price,
            "winner_price": auction.winner_price,
            "start_time": auction.start_time,
            "end_time": auction.end_time,
            "is_active": auction.is_active(),
            "winner_id": auction.winner_id,
            "bids": [{"user_id": bid.user_id, "amount": bid.amount} for bid in auction.bids.all().order_by("-amount")]
        }
        return JsonResponse(data)


class CreateItemView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPartner]

    def post(self, request):
        print(authentication_classes)
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save(owner_id=request.user.id)
            return Response({"message": "Item created successfully!", "item_id": item.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateAuctionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPartner]

    def post(self, request):
        # Ensure the auction's start and end time are in the future
        start_time = datetime.strptime(request.data.get('start_time'), '%Y-%m-%dT%H:%M:%SZ')
        end_time = datetime.strptime(request.data.get('end_time'), '%Y-%m-%dT%H:%M:%SZ')

        if start_time.tzinfo is None:
            start_time = timezone.make_aware(start_time, dt_timezone.utc)
        if end_time.tzinfo is None:
            end_time = timezone.make_aware(end_time, dt_timezone.utc)

        if timezone.now() >= start_time or timezone.now() >= end_time:
            return Response({"error": "Start and end times must be in the future."}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, id=request.data['item'])
        item = ItemSerializer(item)

        if str(item.data['owner_id']) != str(request.user.id):
            return Response({"message": "Unable to create Auction for this Item."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AuctionSerializer(data=request.data)
        if serializer.is_valid():
            auction = serializer.save(owner_id=request.user.id)
            return Response({"message": "Auction created successfully!", "auction_id": auction.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditAuctionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPartner]

    def post(self, request, auction_id):

        # Retrieve the auction object
        auction = get_object_or_404(Auction, id=auction_id)
        # Allow partial updates
        serializer = AuctionSerializer(auction, data=request.data, partial=True)
        if serializer.is_valid():
            # Ensure the owner is the same user making the request
            if str(auction.owner_id) != str(request.user.id):
                return Response({"message": "You are not allowed to update this auction."},status=status.HTTP_403_FORBIDDEN)

            if auction.status != 'PENDING':
                return Response({"message": "You can only update before auction is approved."},status=status.HTTP_403_FORBIDDEN)

            # Ensure the auction's start and end time are provided
            start_time_str = request.data.get('start_time')
            end_time_str = request.data.get('end_time')

            if start_time_str:
                start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%SZ')
                if start_time.tzinfo is None:
                    start_time = timezone.make_aware(start_time, dt_timezone.utc)

                if timezone.now() >= start_time:
                    return Response({"error": "Start and end times must be in the future."},
                                    status=status.HTTP_400_BAD_REQUEST)

            if end_time_str:
                end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M:%SZ')
                if end_time.tzinfo is None:
                    end_time = timezone.make_aware(end_time, dt_timezone.utc)

                if timezone.now() >= end_time:
                    return Response({"error": "Start and end times must be in the future."},
                                    status=status.HTTP_400_BAD_REQUEST)

            auction = serializer.save()  # Save the updated auction
            return Response({"message": "Auction updated successfully!", "auction_id": auction.id},
                        status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveAuctionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    def post(self, request, auction_id):

        # Retrieve the auction object
        auction = get_object_or_404(Auction, id=auction_id)

        # Allow partial updates
        serializer = AuctionSerializer(auction, data=request.data, partial=True)

        if serializer.is_valid():
            auction = serializer.save()  # Save the updated auction
            return Response({"message": "Auction approved!", "auction_id": auction.id},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAuctionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    def delete(self, request, auction_id):
        try:
            # Retrieve the auction instance
            auction = Auction.objects.get(id=auction_id)
        except Auction.DoesNotExist:
            return Response({"error": "Auction not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the auction
        auction.delete()
        return Response({"message": "Auction deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class CreateBidView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPartnerOrUser]

    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        bid_amount = request.data.get('amount')

        headers = {
            "Authorization": request.headers.get("Authorization"),  # Forward the JWT token
        }
        balance_service_url = f"{settings.BALANCE_SERVICE_URL}/api/balance/check-balance/"
        try:
            balance_response = requests.get(balance_service_url, headers=headers)
            balance_response.raise_for_status()
            balance_data = balance_response.json()
            user_balance = balance_data.get("balance")

            if user_balance is None or user_balance < bid_amount:
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

            if auction.is_active() and float(bid_amount) > auction.starting_price:
                if bid_amount % auction.bid_price != 0:
                    return Response(
                        {'error': f'Bid amount must be a multiple of {auction.bid_price}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user_id = request.user.id  # Retrieve user ID from JWT-based user instance
                if str(auction.owner_id) != str(user_id):
                    try:
                        bid = Bid(auction=auction, user_id=request.user.id, amount=bid_amount)
                        bid.save()
                        return Response(
                            {'message': 'Bid placed successfully!', 'amount': bid_amount},
                            status=status.HTTP_201_CREATED
                        )

                    except IntegrityError:
                        # Handle duplicate bid error
                        return Response(
                            {'error': 'Duplicate bid: You have already placed this bid amount on this auction.'},
                            status=status.HTTP_409_CONFLICT
                        )
                else:
                    return Response({'message': 'You are not allowed to place bid on this item'}, status=status.HTTP_403_FORBIDDEN)

            else:
                return Response({'error': 'Invalid bid or auction not active.'}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to check balance"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class BuyItNowView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPartnerOrUser]

    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)

        # Check if auction is active and has a buy it now price
        if auction.is_active() and auction.is_buy_it_now():
            user_id = request.user.id  # Retrieve user ID from JWT-based user instance
            if str(auction.owner_id) != str(user_id):
                highest_bid = Bid.objects.filter(auction=auction).order_by("-amount").first()
                if highest_bid:
                    if highest_bid.amount > auction.buy_it_now_price:
                        return Response(
                            {'message': 'Buy-it-now is unavailable now'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE
                        )

                headers = {
                    "Authorization": request.headers.get("Authorization"),  # Forward the JWT token
                }
                balance_service_url = f"{settings.BALANCE_SERVICE_URL}/api/balance/check-balance/"
                try:
                    balance_response = requests.get(balance_service_url, headers=headers)
                    balance_response.raise_for_status()
                    balance_data = balance_response.json()
                    user_balance = balance_data.get("balance")

                    if user_balance is None or user_balance < auction.buy_it_now_price:
                        return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

                    # Deduct balance from winner
                    headers = {
                        "Authorization": request.headers.get("Authorization"),
                    }
                    data = {
                        "user_id": user_id,
                        "amount": str(auction.buy_it_now_price),
                        "auction_id": auction_id
                    }
                    balance_service_url = f"{settings.BALANCE_SERVICE_URL}/api/balance/deduct-balance/"
                    try:
                        balance_response = requests.post(balance_service_url, json=data, headers=headers)
                        balance_response.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        return Response({"error": "Failed to deduct balance due to "+e.response.json().get('error')},
                                        status=status.HTTP_503_SERVICE_UNAVAILABLE)

                    auction.winner_id = user_id
                    auction.status = 'CLOSED'
                    auction.winner_price = auction.buy_it_now_price
                    auction.save()

                    return Response(
                        {
                            "message": "Buy-it-now successful, and balance deducted.",
                            "auction_id": auction.id,
                            "winner_id": auction.winner_id,
                        },
                        status=status.HTTP_200_OK
                    )

                except requests.exceptions.RequestException as e:
                    return Response({"error": "Failed to check balance"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            else:
                return Response(
                    {'message': 'You are not allowed to purchase this item'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {'error': 'This auction is no longer active or does not have a Buy It Now price.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CloseAuctionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPartner]

    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)
        user_id = request.user.id  # Retrieve user ID from JWT-based user instance
        if str(auction.owner_id) != str(user_id):
            return Response(
                {'message': 'You are not allowed to close this auction'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not auction.is_active():
            return Response({"error": "Auction is either not active yet or already closed."}, status=status.HTTP_400_BAD_REQUEST)

        highest_bid = Bid.objects.filter(auction=auction).order_by("-amount").first()

        if not highest_bid:
            auction.status = 'CANCELLED'
            auction.save()
            return Response({"message": "Auction closed without a winner as no bids found for this auction."}, status=status.HTTP_200_OK)

        # Deduct balance from winner
        headers = {
            "Authorization": request.headers.get("Authorization"),
        }

        data = {
            "user_id": highest_bid.user_id,
            "amount": str(highest_bid.amount),
            'auction_id': auction_id
        }
        balance_service_url = f"{settings.BALANCE_SERVICE_URL}/api/balance/deduct-balance/"
        try:
            balance_response = requests.post(balance_service_url, json=data, headers=headers)
            balance_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response({"error": "Failed to deduct balance"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        auction.winner_id = highest_bid.user_id
        auction.status = 'CLOSED'
        auction.winner_price = Decimal(highest_bid.amount)
        auction.save()
        return Response(
            {
                "message": "Close auction successful, and balance deducted.",
                "auction_id": auction.id,
                "winner_id": auction.winner_id,
            },
            status=status.HTTP_200_OK
        )

