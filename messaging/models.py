from django.db import models
from django.conf import settings # Para referenciar el modelo de usuario (AUTH_USER_MODEL)

# Obtener el modelo de usuario personalizado de tu proyecto (asumimos que está en settings.py)
User = settings.AUTH_USER_MODEL 

# ----------------------------------------------------
# 3.1 Modelo: Conversation (El Hilo de Mensajes)
# ----------------------------------------------------
class Conversation(models.Model):
    """Representa un hilo de conversación entre dos o más usuarios."""
    
    # Participantes: Usamos ManyToManyField para incluir a todos los usuarios
    # que participan en esta conversación (Admin, Customer, Vendor).
    participants = models.ManyToManyField(
        User, 
        related_name='conversations',
        # Puedes añadir un límite si siempre son solo 2 (ej: limit_choices_to={'user_type__in': ['C', 'V']})
    )
    
    # Campo para ordenar las conversaciones: será la fecha del último mensaje
    last_message_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Último Mensaje"
    )

    class Meta:
        ordering = ('-last_message_at',)
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"

    def __str__(self):
        # Muestra a los participantes en el admin
        usernames = ", ".join([user.username for user in self.participants.all()])
        return f"Conversación: {usernames}"


# ----------------------------------------------------
# 3.2 Modelo: Message (El Mensaje Individual)
# ----------------------------------------------------
class Message(models.Model):
    """Representa un único mensaje dentro de una conversación."""
    
    # La conversación a la que pertenece este mensaje (ForeignKey)
    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE
    )
    
    # El remitente del mensaje (ForeignKey)
    sender = models.ForeignKey(
        User, 
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    
    content = models.TextField(verbose_name="Contenido")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ('timestamp',)
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"

    def __str__(self):
        return f"Mensaje de {self.sender.username} en {self.conversation.id}"
