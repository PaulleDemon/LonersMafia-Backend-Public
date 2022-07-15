from django.urls import path

from .views import BanUserFromNetworkView, CreateUserView, UpdateUserView

urlpatterns = [
    path('login/', CreateUserView.as_view(), name='login_user'),
    path('create/', CreateUserView.as_view(), name='create_user'),
    path('update/', UpdateUserView.as_view(), name='update_user'),
    
    path('ban/', BanUserFromNetworkView.as_view(), name='ban-user')
]
