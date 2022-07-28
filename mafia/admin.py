from django.contrib import admin
from django.contrib import messages

from user.models import BlacklistedIp

from . models import Mafia, Message, Reaction, Rule, Moderator, BanUserFromMafia
# Register your models here.


class RulesInline(admin.StackedInline):
    """
        displays the rules in the same page specified in the admin model
    """
    model = Rule


@admin.register(Mafia)
class MafiaAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'icon', 'created_datetime']
    list_filter = ['created_datetime']
    ordering = ['-created_datetime']
    search_fields = ['id', 'name', 'created_by__name']

    inlines = [RulesInline]

    @admin.action(description='delete and ban users')
    def remove_mafia_ban_members(self, request, queryset):
        """
            bans all the users who participated in the mafia and deletes the mafia
        """

        for x in queryset:
            message = Message.objects.filter(mafia=x.id).distinct('user')
            
            for mss in message:
                BlacklistedIp.objects.create(ip_address=mss.user.ip_address)

                mss.user.delete() # deletes the user

        Mafia.objects.filter(mafia=queryset).delete() # removes the mafia

        self.message_user(request, 'user was successfully blacklisted and ', messages.SUCCESS)

@admin.register(Rule)
class RulesAdmin(admin.ModelAdmin):

    list_display = ['id', 'rule', 'mafia']
    search_fileds = ['rule', 'mafia__name']

    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(Moderator)
class ModeratorAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'mafia']
    search_fields = ['user__name', 'mafia__name']


@admin.register(BanUserFromMafia)
class BannedUserFromMafiaAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'mafia']
    search_fields = ['user__name', 'mafia__name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'mafia']
    ordering = ['-datetime']

    search_fields = ['user__name', 'message', 'mafia__name']


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    
    list_display = ['id', 'reaction', 'user', 'message', 'get_mafia']

    search_fields = ['user__name', 'reaction', 'message__message']

    @admin.display(description='mafia')
    def get_mafia(self, obj):
        return obj.message.mafia