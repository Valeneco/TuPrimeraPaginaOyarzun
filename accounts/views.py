from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser
from .forms import LoginForm, SignUpForm, CustomUserUpdateForm
from Finance.models import Customer, Vendor, CustomerInvoice, VendorInvoice
from datetime import date

def login_view(request):
    list(messages.get_messages(request))

    # Added: If already logged in, redirect to the dashboard flow
    if request.user.is_authenticated:
        return redirect('dashboard_flow')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user_obj = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist.")
                return render(request, 'accounts/login.html', {'form': form})

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome {user.username} 👋")
                return redirect('dashboard_flow') 
            else:
                messages.error(request, "Incorrect password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def signup_view(request):
    # Get user type from query param if exists
    preselected_type = request.GET.get('user_type', 'C')

    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = form.cleaned_data['user_type']
            user.save()

            # Create associated profile
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
                messages.error(request, f"Error creating profile: {e}")
                return render(request, 'accounts/signup.html', {'form': form})

            authenticated_user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, f"User created successfully! Welcome {authenticated_user.username} 👋")
                return redirect('dashboard_flow')
            else:
                messages.error(request, "User created but could not log in. Please log in manually.")
                return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Initialize form with preselected user type
        form = SignUpForm(initial={'user_type': preselected_type})

    return render(request, 'accounts/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    filter_status = request.GET.get('status')
    view_type = request.GET.get('view')

    # Block direct Profile access for Admins, forcing flow through Home
    if user.user_type == 'A':
        return redirect('home') 

    invoices = []

    if user.is_superuser:
        if view_type == 'AP':
            invoices = VendorInvoice.objects.all()
        else:
            invoices = CustomerInvoice.objects.all()
    else:
        # 🟢 CORRECCIÓN CLAVE: 
        # 1. Usar user.user_type para decidir la rama.
        # 2. Verificar que el objeto de perfil exista (no sea None) antes de acceder a las facturas.
        if user.user_type == 'C' and user.customer_profile:
            invoices = user.customer_profile.customerinvoice_set.all()
        
        elif user.user_type == 'V' and user.vendor_profile:
            invoices = user.vendor_profile.vendorinvoice_set.all()

    if filter_status:
        # Solo intentar filtrar si la variable 'invoices' contiene un QuerySet válido
        if invoices:
            invoices = invoices.filter(status=filter_status.upper())

    context = {
        'user': user,
        'invoices': invoices,
        'filter_status': filter_status or 'ALL',
        'view_type': view_type or 'AR',
        'customer': getattr(user, 'customer_profile', None),
        'vendor': getattr(user, 'vendor_profile', None),
    }
    return render(request, 'accounts/profile.html', context)


# VIEW 1: Update personal data (name, email, photo, etc.)
@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = CustomUserUpdateForm(instance=user)

    return render(request, 'accounts/edit_profile.html', {'form': form})

# VIEW 2: Change password (separate)
@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # IMPORTANT: Maintains the user's session after changing the password
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            # Note: The form already shows errors, this is a general message
            messages.error(request, 'Please correct the error below.') 
    else:
        form = PasswordChangeForm(request.user)
    
    # Renders the separate change_password.html template
    return render(request, 'accounts/change_password.html', {'form': form})