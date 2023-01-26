"""ventAl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from home import views as home_views
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', core_views.signup, name='signup'),
    path('', home_views.showHome, name='home'),
    path('dashboard/', core_views.showDashboard, name='dashboard'),
    path('stage/<str:album_id>/', core_views.stage, name='stage'),
    path('album/<str:album_ref>/', core_views.album, name='album'),
    path('delete/image/<str:username>/<str:album_id>/<str:image_id>/', core_views.deleteImage, name='deleteImage'),
    path('delete/album/<str:username>/<str:album_id>/', core_views.deleteAlbum, name='deleteAlbum'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)