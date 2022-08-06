from django.urls import path

from . import views


urlpatterns = [
    
    path('create/', views.CreateMafiaView.as_view(), name='create-mafia'),
    path('<int:id>/update/', views.UpdateMafiaView.as_view(), name='update-mafia'),
    path('list/', views.ListMafiaView.as_view(), name='list-mafia'),
    path('<str:name>/get/', views.ListMafiaView.as_view(), name='get-mafia'),
    
    path('assign-mod/', views.AssignModView.as_view(), name='assign-mod'),
    path('delete-and-ban/', views.ModOptionsView.as_view(), name='delete-ban-user'),

    path('message/create/', views.MessageCreateView.as_view(), name='message-create'),
    path('message/delete/<int:id>/', views.MessageDeleteView.as_view(), name='message-delete'),
    path('<int:mafia>/messages/', views.MessageListView.as_view(), name='message-list'),
    
    path('messages/react/', views.MessageReactionCreateView.as_view()),
    path('message/<int:message>/react/<str:reaction>/delete/', views.MessageReactionDeleteView.as_view()),

] 
