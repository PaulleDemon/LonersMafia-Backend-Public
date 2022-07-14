from django.urls import path


urlpatterns = [
    
    path('create/'),
    path('update/'),
    path('delete/'),

    path('<path:space>/messages/create/'),
    path('<path:space>/messages/delete/'),
    path('<path:space>/messages/'),
    path('/messages/<int:id>/react/'),
    path('/messages/react/<int:id>/'),

]
