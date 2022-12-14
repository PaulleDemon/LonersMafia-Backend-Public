from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User, BlacklistedIp



class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('name', )


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('name', )


# Register your models here.
@admin.register(User)
class UserAdmin(UserAdmin):

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ['id', 'name', 'ip_address', 'date_joined']
    ordering = ['-date_joined']

    fieldsets = (
        ('user details', {'fields': ('id', 'email', 'name', 'tag_line',  
                                        'date_joined',  'avatar', 'ip_address', 'password')}),
        ('permissions', {'fields': ('is_staff', 'is_active', 'is_admin')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')}
        ),
    )

    readonly_fields = ['id', 'date_joined']
    actions = ['blacklist_user', 'destroy_and_blacklistuser']

    @admin.action(description='Black list the user')
    def blacklist_user(self, request, queryset):
        """ blacklists the user ip """

        for x in queryset:
            BlacklistedIp.objects.create(user=x, ip_address=x.ip_address)

        self.message_user(request, 'user was successfully blacklisted', messages.SUCCESS)

    @admin.action(description='Black list and destroy user')
    def destroy_and_blacklistuser(self, request, queryset):

        self.blacklist_user(request, queryset)

        User.objects.filter(id__in=queryset).delete()

        self.message_user(request, 'user was successfully blacklisted and removed', messages.SUCCESS)



@admin.register(BlacklistedIp)
class BlackListAdmin(admin.ModelAdmin):

    list_display = ['id', 'ip_address', 'user']
    search_fields = ['ip_address', 'user__name']
