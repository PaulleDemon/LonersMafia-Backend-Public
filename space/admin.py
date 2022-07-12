from django.contrib import admin

from . models import Space, Message, Reaction
# Register your models here.


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'icon', 'created_datetime']
    list_filter = ['created_datetime']
    ordering = ['-created_datetime']
    search_fields = ['id', 'name']


@admin.resgiter(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = ['id', 'user']
    ordering = ['-datetime']

    search_fields = ['user__name', 'message']


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    
    list_display = ['id' 'reaction', 'user__name']

    search_fields = ['user__name', 'reaction', 'message__message']
