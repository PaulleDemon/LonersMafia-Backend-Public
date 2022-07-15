from django.urls import path

from . import views


urlpatterns = [
    
    path('create/', views.CreateSpaceView.as_view(), name='create-space'),
    path('update/', views.UpdateSpaceView.as_view(), name='update-space'),
    path('delete/', views.MessageDeleteView.as_view(), name='delete-space'),

    path('<path:space>/messages/create/', views.MessageCreateView.as_view(), name='message-create'),
    path('<path:space>/messages/delete/', views.MessageDeleteView.as_view(), name='message-delete'),
    path('<path:space>/messages/', views.MessageListView.as_view(), name='message-list'),

    path('/messages/<int:id>/react/', views.MessageReactionCreateView.as_view()),
    path('/messages/react/<int:id>/delete/', views.MessageDeleteView.as_view()),

] 
