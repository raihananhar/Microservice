from django.urls import path
from .views import CloseAuctionView, DeleteAuctionView, ApproveAuctionView, AuctionListView, AuctionDetailView, CreateBidView, BuyItNowView, CreateItemView, CreateAuctionView, EditAuctionView

urlpatterns = [

    path('', AuctionListView.as_view(), name='auction_list'),
    path('items/', CreateItemView.as_view(), name='create_item'),
    path('create/', CreateAuctionView.as_view(), name='create_auction'),
    path('<int:auction_id>/', AuctionDetailView.as_view(), name='auction_detail'),
    path('<int:auction_id>/edit/', EditAuctionView.as_view(), name='edit_auction'),
    path('<int:auction_id>/bid/', CreateBidView.as_view(), name='create_bid'),
    path('<int:auction_id>/buy-it-now/', BuyItNowView.as_view(), name='buy_it_now'),
    path('<int:auction_id>/approve/', ApproveAuctionView.as_view(), name='approve_auction'),
    path('<int:auction_id>/delete/', DeleteAuctionView.as_view(), name='delete_auction'),
    path('<int:auction_id>/close/', CloseAuctionView.as_view(), name='close_auction'),
]

