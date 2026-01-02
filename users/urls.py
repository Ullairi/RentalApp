from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('token/refresh/', views.refresh_token, name='token-refresh'),

    path('users/me/', views.current_user, name='user-me'),
    path('users/update-profile/', views.update_profile, name='user-update-profile'),
    path('users/statistics/', views.user_statistics, name='user-statistics'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),

    path('favorites/', views.FavoriteListCreateView.as_view(), name='favorite-list'),
    path('favorites/<int:pk>/', views.FavoriteDetailView.as_view(), name='favorite-detail'),
]