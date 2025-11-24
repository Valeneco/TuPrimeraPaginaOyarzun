from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Dashboard principal del administrador (raíz del sitio)
    path('', core_views.home_view, name='admin_dashboard'),

    # Ruta intermedia para manejar redirección post-login
    path('dashboard-flow/', core_views.dashboard_flow_view, name='dashboard_flow'),

    # Páginas estáticas
    path('about/', core_views.about, name='about'),
    path('contact/', core_views.contact_view, name='contact'),

    # Otras apps
    path('accounts/', include('accounts.urls')),
    path('finance/', include('Finance.urls')),
    path('messages/', include('messaging.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
