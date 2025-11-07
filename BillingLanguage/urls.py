from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from accounts import views as accounts_views  # ✅ importar login_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Página principal: login
    path('', accounts_views.login_view, name='login'),

    # Páginas estáticas / core
    path('about/', core_views.about, name='about'),
    path('contact/', core_views.contact_view, name='contact'),  # ✅ Agregado para Contact Form

    # URLs de apps
    path('accounts/', include('accounts.urls')),  # login/signup/profile
    path('finance/', include('Finance.urls')),   # todas las URLs de Finance
    path('home/', core_views.home_view, name='home'),  # home.html accesible solo por admin
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)