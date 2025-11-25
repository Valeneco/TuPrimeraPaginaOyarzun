from django.shortcuts import render, get_object_or_404, redirect  
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django import forms
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Page
from .forms import PageForm


# 1. NUEVA VISTA: TARGET DE LOGIN_REDIRECT_URL
@login_required
def dashboard_flow_view(request):
    """
    Punto central después del login.
    LOGIN_REDIRECT_URL = 'dashboard_flow'
    Redirige según tipo de usuario.
    """
    user = request.user
    
    # Admin o staff → Dashboard Admin (ruta '/')
    if user.user_type == 'A' or user.is_staff:
        return redirect('admin_dashboard')
    
    # Clientes/Vendedores → Perfil
    elif user.user_type in ['C', 'V']:
        return redirect('profile')
    
    # Fallback
    return redirect('login')


@login_required
def home_view(request):
    """
    Home principal.
    En esta versión lo redirigimos directamente al Admin de Django.
    """
    user = request.user

    # Si es admin → directo al panel admin
    if user.is_superuser or user.is_staff or user.user_type == 'A':
        return redirect('/admin/')

    # Si NO es admin → que vaya a su perfil
    return redirect('profile')


def index(request):
    return render(request, 'base.html')


def about(request):
    return render(request, 'core/about.html')


class PagesListView(ListView):
    model = Page
    template_name = 'core/pages_list.html'
    context_object_name = 'pages'

pages_list = PagesListView.as_view()


def pages_detail(request, pk):
    page = get_object_or_404(Page, pk=pk)
    context = {'page': page}
    return render(request, 'core/pages_detail.html', context)


class PagesCreateView(LoginRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    template_name = 'core/pages_form.html'
    success_url = reverse_lazy('pages_list')

pages_create = PagesCreateView.as_view()


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


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your Name")
    email = forms.EmailField(label="Your Email")
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)


def contact_view(request):
    """
    Formulario de contacto.
    Envía un email y muestra un mensaje.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            send_mail(
                form.cleaned_data['subject'],
                form.cleaned_data['message'],
                form.cleaned_data['email'],
                ['admin@example.com'],
                fail_silently=True,
            )
            messages.success(request, "Message sent successfully!")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})
