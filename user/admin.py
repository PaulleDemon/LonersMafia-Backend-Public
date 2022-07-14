from django.contrib import admin
from django.contrib import messages
from .models import User, BlacklistedIp
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'ip_address', 'date_joined']
    ordering = ['-date_joined']

    fieldsets = (
        ('user details', {'fields': ('id', 'email', 'name',   
                                        'date_joined',  'avatar', 'ip_address')}),
        ('permissions', {'fields': ('is_staff', 'is_active', 'is_admin')}),
    )

    readonly_fields = ['id', 'date_joined']

    @admin.action(description='Black list the user')
    def blacklist_user(self, request, queryset):
        """ blacklists the user ip """

        for x in queryset:
            BlacklistedIp.objects.create(user=x, ip_address=x.ip_address)

        self.message_user(request, 'users ip was successfully blacklisted', messages.SUCCESS)

    @admin.action(description='Black list and destroy user')
    def destroy_and_blacklistuser(self, request, queryset):

        self.blacklist_user(request, queryset)

        User.objects.filter(user__in=queryset).delete()

        self.message_user(request, 'user was successfully blacklisted and removed', messages.SUCCESS)


@admin.register(BlacklistedIp)
class BlackListAdmin(admin.ModelAdmin):

    list_display = ['ip_address', 'user']
    search_fields = ['ip_address', 'user__name']
