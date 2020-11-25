"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from project import settings as media_settings
from django.conf.urls.static import static
from django.urls import path, include, reverse_lazy
from django.views.generic.base import RedirectView
from landing import views as landing_views

admin.site.site_title = "Library Administration"
admin.site.site_header = "Library Administration"
admin.site.site_index = "Library "

urlpatterns = [
    path('admin_panel/', RedirectView.as_view(url=reverse_lazy('admin:index')), name='admin'),
    path('admin/', admin.site.urls),
    path('', landing_views.home, name='landing-home'),
    path('user/', include('users.urls')),
    path('book/', include('books.urls')),
] 

if settings.DEBUG:
    urlpatterns += static(media_settings.MEDIA_URL, document_root=media_settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)