from django.contrib import admin
from django.contrib import messages

from user.models import BlacklistedIp

from . models import Space, Message, Reaction, Rule, Moderator, BanUserFromSpace
# Register your models here.


class RulesInline(admin.StackedInline):
    """
        displays the rules in the same page specified in the admin model
    """
    model = Rule


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'icon', 'created_datetime']
    list_filter = ['created_datetime']
    ordering = ['-created_datetime']
    search_fields = ['id', 'name', 'created_by__name']

    inlines = [RulesInline]

    @admin.action(description='delete and ban users')
    def remove_space_ban_members(self, request, queryset):
        """
            bans all the users who participated in the space and deletes the space
        """

        for x in queryset:
            message = Message.objects.filter(space=x.id).distinct('user')
            
            for mss in message:
                BlacklistedIp.objects.create(ip_address=mss.user.ip_address)

                mss.user.delete() # deletes the user

        Space.objects.filter(space=queryset).delete() # removes the space

        self.message_user(request, 'user was successfully blacklisted and ', messages.SUCCESS)

@admin.register(Rule)
class RulesAdmin(admin.ModelAdmin):

    list_display = ['id', 'rule', 'space']
    search_fileds = ['rule', 'space__name']

    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(Moderator)
class ModeratorAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'space']
    search_fields = ['user__name', 'space__name']


@admin.register(BanUserFromSpace)
class BannedUserFromSpaceAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'space']
    search_fields = ['user__name', 'space__name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = ['id', 'user']
    ordering = ['-datetime']

    search_fields = ['user__name', 'message']


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    
    list_display = ['id', 'reaction', 'user']

    search_fields = ['user__name', 'reaction', 'message__message']

