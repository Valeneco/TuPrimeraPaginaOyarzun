from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser

# Formulario para registrarse
class SignUpForm(UserCreationForm):
    avatar = forms.ImageField(required=False)
    email = forms.EmailField(required=True)
    birth_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    USER_TYPE_CHOICES = (
        ('C', 'Customer'),
        ('V', 'Vendor'),
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='C',
        label="I am a"
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'bio',
            'birth_date',
        )

# Formulario para editar el perfil
class EditProfileForm(UserChangeForm):
    password = None  # opcional, no mostrar el campo password por defecto

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'bio',
            'birth_date',
        )

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class CustomUserUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar'] 