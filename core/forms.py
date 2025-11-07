from django import forms
from .models import Page

class ContactForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    email = forms.EmailField()
    mensaje = forms.CharField(widget=forms.Textarea)

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title','content',]
