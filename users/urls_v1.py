from rest_framework import routers
from django.urls import path, include
from .views import (
    UserRegistrationView, UserLoginView, UserProfileView,
    UserListView, UserDetailView, logout_view
)

router = routers.DefaultRouter()
# Add any viewsets here

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
