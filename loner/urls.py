from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView

from . import views

admin.site.site_header = 'Loners Mafia'
admin.site.site_title = 'Loners Mafia Admin'
admin.site.site_url = 'lonersmafia.com'

# admin.site.login_template = 
admin.autodiscover()
# admin.site.login = staff_member_required(admin.site.login)


urlpatterns = [
    path('admin/login/', views.admin_login, name='admin-login'),
    path('admin/', admin.site.urls, name='admin'),
    path('user/', include('user.urls')),
    path('mafia/', include('mafia.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

else:
    urlpatterns += [re_path(r'(?P<path>,*)', TemplateView.as_view(template_name='index.html'))]