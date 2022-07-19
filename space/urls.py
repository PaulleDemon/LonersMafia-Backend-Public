from django.urls import path

from . import views


urlpatterns = [
    
    path('create/', views.CreateSpaceView.as_view(), name='create-space'),
    path('update/<int:id>/', views.UpdateSpaceView.as_view(), name='update-space'),
    path('list/', views.ListSpaceView.as_view(), name='list-space'),
    path('<str:name>/get/', views.ListSpaceView.as_view(), name='get-space'),
    
    path('assign-mod/', views.AssignModView.as_view(), name='assign-mod'),
    path('delete-and-ban/', views.ModOptionsView.as_view(), name='delete-ban-user'),

    path('message/create/', views.MessageCreateView.as_view(), name='message-create'),
    path('message/delete/<int:id>/', views.MessageDeleteView.as_view(), name='message-delete'),
    path('<path:space>/messages/', views.MessageListView.as_view(), name='message-list'),
    
    path('messages/<int:id>/react/', views.MessageReactionCreateView.as_view()),
    path('messages/react/<int:id>/delete/', views.MessageDeleteView.as_view()),

] 
