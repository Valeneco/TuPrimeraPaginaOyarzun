# messaging/forms.py

from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    # Campo personalizado para el contenido del mensaje
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3', 
            'placeholder': 'Escribe tu mensaje...',
            'class': 'form-control' # Clase de Bootstrap
        })
    )

    class Meta:
        model = Message
        fields = ['content']