from ipaddress import ip_address
from django.contrib import admin
from django.contrib import messages
from .models import User, BlacklistedIp
from django.utils.translation import ngettext
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ['username', 'ip_address', 'date_joined']
    list_filter = ['-date_joined']

    @admin.action(description='Black list the user')
    def blacklist_user(self, request, queryset):
        """ blacklists the user ip """

        for x in queryset:
            BlacklistedIp.objects.create(ip_address=x.ip_address)

        self.message_user(request, 'users ip was successfully blacklisted', messages.SUCCESS)

    @admin.action(description='Black list and destroy user')
    def destroy_and_blacklistuser(self, request, queryset):

        self.blacklist_user(request, queryset)

        User.objects.filter(user__in=queryset).delete()

        self.message_user(request, 'user was successfully blacklisted and removed', messages.SUCCESS)
