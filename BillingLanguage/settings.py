from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-8_p)1@4v6-rd1__b-&3@n&e-_f&bu+x!xaf99bs-!j#0$r3xy#'
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Finance',
    'core',
    'accounts',
    'blog', 
    'ckeditor',
    'messaging',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BillingLanguage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' /'templates'],  # puedes agregar BASE_DIR / 'templates' si quieres
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BillingLanguage.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # opcional si quieres carpeta global de static

# Media (para avatares, imágenes de posts)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ⚡ Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Redirects after login/logout
# CORRECCIÓN PARA ROMPER EL BUCLE DE RECURSIÓN
# El login redirige a esta nueva ruta intermedia, no a la raíz.
LOGIN_REDIRECT_URL = 'dashboard_flow' 
LOGOUT_REDIRECT_URL = 'login' 

# URL para el Login
LOGIN_URL = '/accounts/login/' 

# Media (para avatares, imágenes de posts)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

APPEND_SLASH = True

# ==============================
# Email settings para Contact Form
# ==============================

# Durante desarrollo: ver emails en consola
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Desde qué email se enviarán los mensajes
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# Lista de admins que recibirán los emails de contacto
ADMINS = [
    ('Admin', 'admin@example.com'),  # <-- reemplaza con tu email real
]