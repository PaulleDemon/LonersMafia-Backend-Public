from django.urls import path

from .views import MessageListView


urlpatterns = [
    
    # path('create/'),
    # path('update/'),
    # path('delete/'),

    # path('<path:space>/messages/create/'),
    # path('<path:space>/messages/delete/'),
    path('<path:space>/messages/', MessageListView.as_view()),
    # path('/messages/<int:id>/react/'),
    # path('/messages/react/<int:id>/'),

] 
