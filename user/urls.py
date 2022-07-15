from django.urls import path

from .views import CreateUserView

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create_user'),
    # path('update/', ),
    # path('ban/')
]
