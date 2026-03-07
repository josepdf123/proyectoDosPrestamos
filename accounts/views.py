from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from datetime import timedelta
import uuid

from .forms import LoginForm, RecuperacionContraseñaForm, RestablecerContraseñaForm, UsuarioCreationForm, UsuarioEditForm
from .models import Usuario, Rol

MAX_INTENTOS = 3
TIEMPO_BLOQUEO_MINUTOS = 2


# ─── DECORADOR PARA SOLO ADMINISTRADOR ───────────────────────────────────────

def solo_administrador(view_func):
    """Decorador para restringir acceso solo a administradores - HU14"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.idRol or request.user.idRol.descripcion != 'administrador':
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── HU13: LOGIN Y RECUPERACIÓN DE CONTRASEÑA ────────────────────────────────

def login_view(request):
    """HU13: Login del Administrador con validaciones mejoradas"""
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

            # Validar entrada
            if not usuario_str or not password:
                error = 'Usuario y contraseña son requeridos.'
                return render(request, 'accounts/login.html', {'form': form, 'error': error})

            # Buscar el usuario en la base de datos
            try:
                usuario_obj = Usuario.objects.get(usuario=usuario_str)
            except Usuario.DoesNotExist:
                error = 'Usuario o contraseña incorrectos.'
                return render(request, 'accounts/login.html', {'form': form, 'error': error})

            # Verificar si la cuenta está bloqueada temporalmente - HU13
            if usuario_obj.esta_bloqueado():
                segundos_restantes = int((usuario_obj.bloqueado_hasta - timezone.now()).total_seconds())
                minutos = segundos_restantes // 60
                segundos = segundos_restantes % 60
                error = f'🔒 Cuenta bloqueada. Intenta de nuevo en {minutos}m {segundos}s.'
                return render(request, 'accounts/login.html', {'form': form, 'error': error})

            # Intentar autenticar
            user = authenticate(request, username=usuario_str, password=password)

            if user is not None:
                # Login exitoso: resetear contadores - HU13
                usuario_obj.resetear_intentos()
                login(request, user)
                messages.success(request, f'¡Bienvenido, {usuario_obj.nombre}!')
                return redirect('dashboard')
            else:
                # Contraseña incorrecta: incrementar contador - HU13
                usuario_obj.incrementar_intentos_fallidos()

                if usuario_obj.bloqueado_hasta:
                    error = (
                        f'🔒 Has alcanzado {MAX_INTENTOS} intentos fallidos. '
                        f'Tu cuenta ha sido bloqueada por {TIEMPO_BLOQUEO_MINUTOS} minutos.'
                    )
                else:
                    intentos_restantes = MAX_INTENTOS - usuario_obj.intentos_fallidos
                    error = f'❌ Contraseña incorrecta. Te quedan {intentos_restantes} intento(s).'

    return render(request, 'accounts/login.html', {'form': form, 'error': error})


def recuperacion_contrasena_view(request):
    """HU13: Solicitar recuperación de contraseña"""
    form = RecuperacionContraseñaForm()
    mensaje = None

    if request.method == 'POST':
        form = RecuperacionContraseñaForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']

            try:
                usuario = Usuario.objects.get(correo=correo)

                # Generar token único
                token = str(uuid.uuid4())
                usuario.token_recuperacion = token
                usuario.token_recuperacion_expira = timezone.now() + timedelta(hours=24)
                usuario.save()

                # Construir URL para restablecer contraseña
                enlace = request.build_absolute_uri(f'/restablecer-contrasena/{token}/')

                # Enviar email
                asunto = '🔐 Recuperación de Contraseña - Gestión de Préstamos'
                mensaje_email = f'''
Hola {usuario.nombre},

Recibimos una solicitud para restablecer tu contraseña.

Haz clic en el siguiente enlace para crear una nueva contraseña:
{enlace}

Este enlace será válido por 24 horas.

Si no solicitaste esto, ignora este correo.

Saludos,
Sistema de Gestión de Préstamos
                '''

                send_mail(
                    asunto,
                    mensaje_email,
                    settings.DEFAULT_FROM_EMAIL,
                    [correo],
                    fail_silently=False,
                )

                mensaje = f'✅ Hemos enviado un enlace de recuperación a {correo}. Revisa tu bandeja de entrada.'
                return render(request, 'accounts/recuperacion_contrasena.html', {'form': form, 'mensaje': mensaje})

            except Usuario.DoesNotExist:
                # No revelar si el email existe o no (seguridad)
                mensaje = 'Si existe una cuenta con ese correo, recibirás un enlace de recuperación.'

    return render(request, 'accounts/recuperacion_contrasena.html', {'form': form, 'mensaje': mensaje})


def restablecer_contrasena_view(request, token):
    """HU13: Restablecer contraseña con token"""
    form = RestablecerContraseñaForm()
    error = None

    try:
        usuario = Usuario.objects.get(token_recuperacion=token)

        # Verificar si el token ha expirado
        if not usuario.token_recuperacion_expira or timezone.now() > usuario.token_recuperacion_expira:
            error = '❌ El enlace ha expirado. Por favor, solicita uno nuevo.'
            return render(request, 'accounts/restablecer_contrasena.html', {'error': error, 'token': token})

    except Usuario.DoesNotExist:
        error = '❌ El enlace no es válido.'
        return render(request, 'accounts/restablecer_contrasena.html', {'error': error, 'token': token})

    if request.method == 'POST':
        form = RestablecerContraseñaForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']

            # Validar longitud mínima
            if len(password) < 8:
                error = '❌ La contraseña debe tener al menos 8 caracteres.'
                return render(request, 'accounts/restablecer_contrasena.html', {
                    'form': form,
                    'error': error,
                    'token': token
                })

            # Actualizar contraseña
            usuario.set_password(password)
            usuario.token_recuperacion = None
            usuario.token_recuperacion_expira = None
            usuario.resetear_intentos()
            usuario.save()

            messages.success(request, '✅ Contraseña restablecida. Ya puedes iniciar sesión.')
            return redirect('login')
        else:
            error = 'Por favor, revisa los datos ingresados.'

    return render(request, 'accounts/restablecer_contrasena.html', {
        'form': form,
        'error': error,
        'token': token
    })


def dashboard_view(request):
    """Dashboard general después del login"""
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
    """Cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


# ─── HU14: GESTIÓN DE USUARIOS ──────────────────────────────────────────────

@solo_administrador
def usuarios_lista_view(request):
    """HU14: Listar todos los usuarios"""
    usuarios = Usuario.objects.all().order_by('-creado_en')

    # Búsqueda
    busqueda = request.GET.get('busqueda', '').strip()
    if busqueda:
        usuarios = usuarios.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido__icontains=busqueda) |
            Q(usuario__icontains=busqueda) |
            Q(correo__icontains=busqueda)
        )

    # Filtro por rol
    rol_filtro = request.GET.get('rol', '')
    if rol_filtro:
        usuarios = usuarios.filter(idRol__descripcion=rol_filtro)

    roles = Rol.objects.all()

    context = {
        'usuarios': usuarios,
        'roles': roles,
        'busqueda': busqueda,
        'rol_filtro': rol_filtro,
        'total_usuarios': Usuario.objects.count(),
    }

    return render(request, 'accounts/usuarios_lista.html', context)


@solo_administrador
def usuario_crear_view(request):
    """HU14: Crear nuevo usuario"""
    form = UsuarioCreationForm()

    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'✅ Usuario {usuario.nombre} creado correctamente.')
            return redirect('usuarios_lista')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    return render(request, 'accounts/usuario_crear.html', {'form': form})


@solo_administrador
def usuario_editar_view(request, pk):
    """HU14: Editar usuario existente"""
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioEditForm(instance=usuario)

    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'✅ Usuario {usuario.nombre} actualizado correctamente.')
            return redirect('usuarios_lista')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    context = {
        'form': form,
        'usuario': usuario,
        'modo': 'editar'
    }

    return render(request, 'accounts/usuario_editar.html', context)


@solo_administrador
def usuario_eliminar_view(request, pk):
    """HU14: Eliminar usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)

    # No permitir eliminar la propia cuenta
    if usuario.pk == request.user.pk:
        messages.error(request, '❌ No puedes eliminar tu propia cuenta.')
        return redirect('usuarios_lista')

    if request.method == 'POST':
        nombre_completo = f'{usuario.nombre} {usuario.apellido}'
        usuario.delete()
        messages.success(request, f'✅ Usuario {nombre_completo} eliminado correctamente.')
        return redirect('usuarios_lista')

    context = {
        'usuario': usuario,
        'modo': 'eliminar'
    }

    return render(request, 'accounts/usuario_eliminar.html', context)


# Importar Q para búsquedas
from django.db.models import Q
