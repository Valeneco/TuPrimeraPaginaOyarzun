from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'timestamp', 'is_read')
    can_delete = False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_participants', 'last_message_at')
    filter_horizontal = ('participants',) # Para un mejor manejo del M2M
    inlines = [MessageInline]
    search_fields = ('participants__username',)
    ordering = ('-last_message_at',)
    
    # Método para mostrar los nombres de usuario en la lista
    def display_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    display_participants.short_description = 'Participants'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read', 'sender')
    search_fields = ('content', 'sender__username')
    raw_id_fields = ('conversation', 'sender') # Útil para buscar IDs rápidamente

