from django.urls import path

from .views import BanUserFromNetworkView, CreateUserView, UpdateUserView, LoginUserView, GetUserView

urlpatterns = [
    
    path('login/', LoginUserView.as_view(), name='login_user'),
    path('create/', CreateUserView.as_view(), name='create_user'),
    path('update/<int:id>/', UpdateUserView.as_view(), name='update_user'),
    path('ban/', BanUserFromNetworkView.as_view(), name='ban-user'),

    path('<str:name>/get/', GetUserView.as_view(), name="user-get-view"),
]
