from django.urls import path
from .views import sync_data, get_user_data

urlpatterns = [
    path('sync/', sync_data, name='sync_data'),
    path('user/<str:username>/', get_user_data, name='get_user_data'),
]
