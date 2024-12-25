from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from fileapp import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.file_list, name='file_list'),
    path('upload/', views.upload_file, name='upload_file'),
    path('generate-shareable-link/<int:file_id>/', views.generate_shareable_link, name='generate_share_link'),
    path('file/share/<str:token>/', views.access_shared_file, name='access_shared_file'),
    path('share/<int:file_id>/', views.share_file, name='share_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)