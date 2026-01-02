from django.urls import path
from . import views

urlpatterns = [
    path('amenities/', views.AmenityListView.as_view(), name='amenity-list'),

    path('listings/popular/', views.popular_listings, name='popular-listings'),
    path('listings/popular-searches/', views.popular_searches, name='popular-searches'),
    path('listings/my-search-history/', views.my_search_history, name='my-search-history'),
    path('listings/my-view-history/', views.my_view_history, name='my-view-history'),

    path('listings/create/', views.ListingCreateView.as_view(), name='listing-create'),
    path('listings/', views.ListingListView.as_view(), name='listing-list'),
    path('listings/<int:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),
    path('listings/<int:pk>/manage/', views.ListingManageView.as_view(), name='listing-manage'),
    path('listings/<int:pk>/toggle-status/', views.toggle_listing_status, name='listing-toggle'),
    path('listings/<int:pk>/add-image/', views.add_listing_image, name='listing-add-image'),
]