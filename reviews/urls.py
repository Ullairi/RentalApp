from django.urls import path
from . import views

urlpatterns = [
    path('listings/<int:listing_id>/reviews/', views.ListingReviewsView.as_view(), name='listing-reviews'),

    path('reviews/my/', views.MyReviewsView.as_view(), name='my-reviews'),
    path('reviews/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:pk>/', views.ReviewManageView.as_view(), name='review-detail'),
]