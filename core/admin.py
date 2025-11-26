from django.contrib import admin
from .models import Page 
from .models import ContactMessage

# Clase personalizada para administrar el modelo Page
class PageAdmin(admin.ModelAdmin):
    # Campos que se muestran en la lista de páginas del administrador
    list_display = ('title', 'subtitle', 'date_display') 
    
    # Campos de filtrado y búsqueda
    list_filter = ('date',)
    search_fields = ('title', 'subtitle', 'content') 
    
    # Configuración de los campos en el formulario de edición/creación
    fieldsets = (
        (None, {
            # Se muestran todos los campos del modelo
            'fields': ('title', 'subtitle', 'content', 'image'),
        }),
        ('Información de Fecha', {
            # La fecha es auto_now_add, por lo que puede ser solo de lectura o estar en un grupo
            'fields': ('date',),
            'classes': ('collapse',), 
        }),
    )
    
    # Campo de fecha de solo lectura en el formulario de edición
    readonly_fields = ('date',)

    # Método para formatear la fecha en el listado
    def date_display(self, obj):
        return obj.date.strftime("%Y-%m-%d")
    date_display.short_description = 'Fecha'

# Registrar el modelo Page con la clase de administración personalizada
admin.site.register(Page, PageAdmin)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('name', 'email', 'subject', 'message')