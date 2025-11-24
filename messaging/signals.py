from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Conversation

@receiver(post_save, sender=Message)
def update_conversation_timestamp(sender, instance, created, **kwargs):
    """
    Actualiza el campo last_message_at de la conversación
    cada vez que se crea un nuevo mensaje.
    """
    if created:
        conversation = instance.conversation
        conversation.last_message_at = instance.timestamp
        conversation.save()