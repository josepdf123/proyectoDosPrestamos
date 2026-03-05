from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import timedelta
from .forms import LoginForm
from .models import Usuario

MAX_INTENTOS = 3
TIEMPO_BLOQUEO_MINUTOS = 2


def login_view(request):
    # Si ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm()
    error = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario_str = form.cleaned_data['usuario']
            password = form.cleaned_data['password']

            # Buscar el usuario en la base de datos
            try:
                usuario_obj = Usuario.objects.get(usuario=usuario_str)
            except Usuario.DoesNotExist:
                error = 'Usuario o contraseña incorrectos.'
                return render(request, 'accounts/login.html', {'form': form, 'error': error})

            # Verificar si la cuenta está bloqueada temporalmente
            if usuario_obj.bloqueado_hasta and timezone.now() < usuario_obj.bloqueado_hasta:
                segundos_restantes = int((usuario_obj.bloqueado_hasta - timezone.now()).total_seconds())
                minutos = segundos_restantes // 60
                segundos = segundos_restantes % 60
                error = f'Cuenta bloqueada. Intenta de nuevo en {minutos}m {segundos}s.'
                return render(request, 'accounts/login.html', {'form': form, 'error': error})

            # Intentar autenticar
            user = authenticate(request, username=usuario_str, password=password)

            if user is not None:
                # Login exitoso: resetear contadores
                usuario_obj.intentos_fallidos = 0
                usuario_obj.bloqueado_hasta = None
                usuario_obj.save()
                login(request, user)
                return redirect('dashboard')
            else:
                # Contraseña incorrecta: incrementar contador
                usuario_obj.intentos_fallidos += 1

                if usuario_obj.intentos_fallidos >= MAX_INTENTOS:
                    # Bloquear la cuenta por 2 minutos
                    usuario_obj.bloqueado_hasta = timezone.now() + timedelta(minutes=TIEMPO_BLOQUEO_MINUTOS)
                    usuario_obj.intentos_fallidos = 0
                    usuario_obj.save()
                    error = (
                        f'Has alcanzado {MAX_INTENTOS} intentos fallidos. '
                        f'Tu cuenta ha sido bloqueada por {TIEMPO_BLOQUEO_MINUTOS} minutos.'
                    )
                else:
                    intentos_restantes = MAX_INTENTOS - usuario_obj.intentos_fallidos
                    usuario_obj.save()
                    error = f'Contraseña incorrecta. Te quedan {intentos_restantes} intento(s) antes del bloqueo.'

    return render(request, 'accounts/login.html', {'form': form, 'error': error})


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    rol_nombre = None
    if request.user.idRol:
        rol_nombre = request.user.idRol.get_descripcion_display()

    return render(request, 'accounts/dashboard.html', {
        'rol': rol_nombre,
        'usuario': request.user,
    })


def logout_view(request):
    logout(request)
    return redirect('login')
