from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser
from .forms import LoginForm, SignUpForm, CustomUserUpdateForm
from Finance.models import Customer, Vendor, CustomerInvoice, VendorInvoice
from Finance.forms import CustomerInvoiceForm, VendorInvoiceForm
from datetime import date

def login_view(request):
    list(messages.get_messages(request))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Verificar si el usuario existe
            try:
                user_obj = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist.")
                return render(request, 'accounts/login.html', {'form': form})

            # Autenticar usuario
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome {user.username} 👋")

                # 🔹 Redirección según tipo de usuario
                if user.user_type == 'A':  # Admin
                    return redirect('home')
                else:  # Customer o Vendor
                    return redirect('profile')
            else:
                messages.error(request, "Incorrect password.")
    else:
        form = LoginForm()

    # 🔹 Renderizar siempre login.html como página principal
    return render(request, 'accounts/login.html', {'form': form})

# -----------------------------
# SIGNUP
# -----------------------------
def signup_view(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)

        if form.is_valid():
            # Guardar usuario (sin commit todavía)
            user = form.save(commit=False)
            user.user_type = form.cleaned_data['user_type']
            user.save()  # Se guarda el usuario en DB

            # Crear perfil asociado en Finance
            try:
                if user.user_type == 'C':
                    customer = Customer.objects.create(
                        name=user.get_full_name() or user.username,
                        email=user.email,
                        company_code='USPS'
                    )
                    user.customer_profile = customer
                else:
                    vendor = Vendor.objects.create(
                        name=user.get_full_name() or user.username,
                        email=user.email,
                        company_code='USPS'
                    )
                    user.vendor_profile = vendor
                user.save()
            except Exception as e:
                # Mensaje de error si falla la creación del perfil
                messages.error(request, f"Error creating profile: {e}")
                return render(request, 'accounts/signup.html', {'form': form})

            # 🔹 Autenticación y login seguro
            authenticated_user = authenticate(
                request, 
                username=form.cleaned_data['username'], 
                password=form.cleaned_data['password1']
            )
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, f"User created successfully! Welcome {authenticated_user.username} 👋")

                # 🔹 Redirección según tipo de usuario
                if authenticated_user.user_type == 'A':  # Admin
                    return redirect('home')
                else:  # Customer o Vendor
                    return redirect('profile')

            else:
                # Si algo falla en login, mostrar error
                messages.error(request, "User created but could not log in. Please try logging in manually.")
                return redirect('login')

        else:
            # 🔹 Mostrar errores del formulario en mensajes
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})# -----------------------------
# LOGOUT
# -----------------------------
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

# -----------------------------
# PROFILE
# -----------------------------
@login_required
def profile_view(request):
    user = request.user
    filter_status = request.GET.get('status')

    # Facturas según tipo de usuario
    if user.user_type == 'C' and user.customer_profile:
        invoices = user.customer_profile.customerinvoice_set.all()
    elif user.user_type == 'V' and user.vendor_profile:
        invoices = user.vendor_profile.vendorinvoice_set.all()
    else:
        invoices = []

    if filter_status:
        invoices = invoices.filter(status=filter_status.upper())

    context = {
        'user': user,
        'invoices': invoices,
        'filter_status': filter_status or 'ALL',
        'customer': getattr(user, 'customer_profile', None),
        'vendor': getattr(user, 'vendor_profile', None),
    }

    return render(request, 'accounts/profile.html', context)

# -----------------------------
# EDIT PROFILE
# -----------------------------
@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        # Validar cambios
        if form.is_valid() and (not request.POST.get('old_password') or password_form.is_valid()):
            form.save()
            # Cambiar contraseña si se completó
            if request.POST.get('old_password'):
                password_form.save()
                update_session_auth_hash(request, user)  # Mantener al usuario logueado
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = CustomUserUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)

    context = {
        'form': form,
        'password_form': password_form
    }
    return render(request, 'accounts/edit_profile.html', context)
