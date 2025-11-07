from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django import forms
from .models import Page  # Modelo principal de páginas/posts
from .forms import PageForm  # Formulario para crear/editar páginas

# -----------------------------
# NUEVA VISTA: HOME / DASHBOARD
# -----------------------------
@login_required
def home_view(request):
    """
    Vista principal del sitio (Home / Dashboard).
    Redirige a profile.html para clientes/vendors.
    Admin ve home.html con links de gestión.
    """
    user = request.user

    if user.user_type == 'A':
        # Admin → mostrar home.html
        return render(request, 'core/home.html', {'user': user})
    elif user.user_type in ['C', 'V']:
        # Customer o Vendor → redirigir a profile
        return redirect('profile')
    else:
        # Si hubiera un user_type desconocido → logout o mensaje
        return redirect('login')

# -----------------------------
# VISTAS EXISTENTES DEL CORE
# -----------------------------
def index(request):
    return render(request, 'base.html')

def about(request):
    return render(request, 'core/about.html')

def pages_list(request):
    pages = Page.objects.all()
    context = {'pages': pages}
    return render(request, 'core/pages_list.html', context)

def pages_detail(request, pk):
    page = get_object_or_404(Page, pk=pk)
    context = {'page': page}
    return render(request, 'core/pages_detail.html', context)

@login_required
def pages_create(request):
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pages_list')
    else:
        form = PageForm()
    return render(request, 'core/pages_form.html', {'form': form})

@login_required
def pages_edit(request, pk):
    page = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            return redirect('pages_detail', pk=page.pk)
    else:
        form = PageForm(instance=page)
    return render(request, 'core/pages_form.html', {'form': form})

@login_required
def pages_delete(request, pk):
    page = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        page.delete()
        return redirect('pages_list')
    return render(request, 'core/pages_confirm_delete.html', {'page': page})

# -----------------------------
# NUEVA VISTA: CONTACT / FORMULARIO
# -----------------------------
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your Name")
    email = forms.EmailField(label="Your Email")
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)

def contact_view(request):
    """
    Formulario de contacto. Envía correo al admin (simulado) y muestra mensajes.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Enviar email (opcional: modificar destinatario)
            send_mail(
                form.cleaned_data['subject'],
                form.cleaned_data['message'],
                form.cleaned_data['email'],
                ['admin@example.com'],  # Cambiar por tu mail real
                fail_silently=True,
            )
            messages.success(request, "Message sent successfully!")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})
