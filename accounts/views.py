from .models import Usuario, Rol, Equipo, CategoriaEquipo, Item, CategoriaItem, Ticket, Prestamo, Notificacion
from .forms import LoginForm, RecuperacionContraseñaForm, RestablecerContraseñaForm, UsuarioCreationForm, UsuarioEditForm, ItemForm, EquipoForm, TicketForm, TicketEditForm, PrestamoForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import timedelta, date
import uuid

#from .models import Usuario, Rol, Equipo, CategoriaEquipo, Item, CategoriaItem, Ticket, Prestamo, Notificacion



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


# ─── DECORADOR PARA SOLO ENCARGADO DE TECNOLOGÍA ─────────────────────────────


def solo_encargado(view_func):
    """Decorador para restringir acceso solo a encargados - HU12"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.idRol or request.user.idRol.descripcion != 'encargado_tecnologia':
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── HU13: LOGIN Y RECUPERACIÓN DE CONTRASEÑA ────────────────────────────────


def login_view(request):
    """HU13: Login del Administrador con validaciones mejoradas"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm()
    error = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario_str = form.cleaned_data['usuario']
            password = form.cleaned_data['password']

            if not usuario_str or not password:
                error = 'Usuario y contraseña son requeridos.'
                return render(request, 'accounts/login.html', {'form': form, 'error': error})

            try:
                usuario_obj = Usuario.objects.get(usuario=usuario_str)
            except Usuario.DoesNotExist:
                error = 'Usuario o contraseña incorrectos.'
                return render(request, 'accounts/login.html', {'form': form, 'error': error})

            if usuario_obj.esta_bloqueado():
                segundos_restantes = int((usuario_obj.bloqueado_hasta - timezone.now()).total_seconds())
                minutos = segundos_restantes // 60
                segundos = segundos_restantes % 60
                error = f'🔒 Cuenta bloqueada. Intenta de nuevo en {minutos}m {segundos}s.'
                return render(request, 'accounts/login.html', {'form': form, 'error': error})

            user = authenticate(request, username=usuario_str, password=password)

            if user is not None:
                usuario_obj.resetear_intentos()
                login(request, user)
                messages.success(request, f'¡Bienvenido, {usuario_obj.nombre}!')
                return redirect('dashboard')
            else:
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
                token = str(uuid.uuid4())
                usuario.token_recuperacion = token
                usuario.token_recuperacion_expira = timezone.now() + timedelta(hours=24)
                usuario.save()

                enlace = request.build_absolute_uri(f'/restablecer-contrasena/{token}/')
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
                send_mail(asunto, mensaje_email, settings.DEFAULT_FROM_EMAIL, [correo], fail_silently=False)
                mensaje = f'✅ Hemos enviado un enlace de recuperación a {correo}. Revisa tu bandeja de entrada.'
                return render(request, 'accounts/recuperacion_contrasena.html', {'form': form, 'mensaje': mensaje})

            except Usuario.DoesNotExist:
                mensaje = 'Si existe una cuenta con ese correo, recibirás un enlace de recuperación.'

    return render(request, 'accounts/recuperacion_contrasena.html', {'form': form, 'mensaje': mensaje})


def restablecer_contrasena_view(request, token):
    """HU13: Restablecer contraseña con token"""
    form = RestablecerContraseñaForm()
    error = None

    try:
        usuario = Usuario.objects.get(token_recuperacion=token)
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
            if len(password) < 8:
                error = '❌ La contraseña debe tener al menos 8 caracteres.'
                return render(request, 'accounts/restablecer_contrasena.html', {'form': form, 'error': error, 'token': token})

            usuario.set_password(password)
            usuario.token_recuperacion = None
            usuario.token_recuperacion_expira = None
            usuario.resetear_intentos()
            usuario.save()
            messages.success(request, '✅ Contraseña restablecida. Ya puedes iniciar sesión.')
            return redirect('login')
        else:
            error = 'Por favor, revisa los datos ingresados.'

    return render(request, 'accounts/restablecer_contrasena.html', {'form': form, 'error': error, 'token': token})


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


# ─── HU14: GESTIÓN DE USUARIOS ───────────────────────────────────────────────


@solo_administrador
def usuarios_lista_view(request):
    """HU14: Listar todos los usuarios"""
    usuarios = Usuario.objects.all().order_by('-creado_en')

    busqueda = request.GET.get('busqueda', '').strip()
    if busqueda:
        usuarios = usuarios.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido__icontains=busqueda) |
            Q(usuario__icontains=busqueda) |
            Q(correo__icontains=busqueda)
        )

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

    context = {'form': form, 'usuario': usuario, 'modo': 'editar'}
    return render(request, 'accounts/usuario_editar.html', context)


@solo_administrador
def usuario_eliminar_view(request, pk):
    """HU14: Eliminar usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.pk == request.user.pk:
        messages.error(request, '❌ No puedes eliminar tu propia cuenta.')
        return redirect('usuarios_lista')

    if request.method == 'POST':
        nombre_completo = f'{usuario.nombre} {usuario.apellido}'
        usuario.delete()
        messages.success(request, f'✅ Usuario {nombre_completo} eliminado correctamente.')
        return redirect('usuarios_lista')

    context = {'usuario': usuario, 'modo': 'eliminar'}
    return render(request, 'accounts/usuario_eliminar.html', context)


# ─── UH6: VISUALIZACIÓN DE EQUIPOS DISPONIBLES ───────────────────────────────


@login_required(login_url='/login/')
def equipos_disponibles_view(request):
    """UH6 CA1 y CA3: Ver equipos disponibles y buscar por nombre"""
    equipos = Equipo.objects.filter(estado='disponible').order_by('nombre')

    busqueda = request.GET.get('busqueda', '').strip()
    if busqueda:
        equipos = equipos.filter(
            Q(nombre__icontains=busqueda) |
            Q(marca__icontains=busqueda) |
            Q(modelo__icontains=busqueda) |
            Q(categoria__nombre__icontains=busqueda)
        )

    categoria_filtro = request.GET.get('categoria', '')
    if categoria_filtro:
        equipos = equipos.filter(categoria__id=categoria_filtro)

    categorias = CategoriaEquipo.objects.all()

    context = {
        'equipos': equipos,
        'categorias': categorias,
        'busqueda': busqueda,
        'categoria_filtro': categoria_filtro,
        'total_disponibles': Equipo.objects.filter(estado='disponible').count(),
    }
    return render(request, 'accounts/equipos_disponibles.html', context)


@login_required(login_url='/login/')
def equipo_detalle_view(request, pk):
    """UH6 CA2: Ver detalle de un equipo específico"""
    equipo = get_object_or_404(Equipo, pk=pk, estado='disponible')
    return render(request, 'accounts/equipo_detalle.html', {'equipo': equipo})


# ─── HU7: PRÉSTAMOS ──────────────────────────────────────────────────────────


@login_required(login_url='/login/')
def solicitar_prestamo_view(request, pk):
    """HU7 CA1 y CA2: Validar disponibilidad y mostrar formulario"""
    equipo = get_object_or_404(Equipo, pk=pk)

    if equipo.estado != 'disponible':
        messages.error(request, f'❌ El equipo "{equipo.nombre}" no está disponible para préstamo.')
        return redirect('equipos_disponibles')

    form = PrestamoForm()

    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            Prestamo.objects.create(
                usuario=request.user,
                equipo=equipo,
                fecha_reclamo=form.cleaned_data['fecha_reclamo'],
                fecha_entrega=form.cleaned_data['fecha_entrega'],
                motivo=form.cleaned_data['motivo'],
                estado='pendiente'
            )
            messages.success(request, f'✅ Solicitud de préstamo para "{equipo.nombre}" enviada correctamente. Espera la aprobación.')
            return redirect('mis_prestamos')

    return render(request, 'accounts/solicitar_prestamo.html', {'equipo': equipo, 'form': form})


# ─── HU2: MIS PRÉSTAMOS ACTIVOS ──────────────────────────────────────────────


@login_required(login_url='/login/')
def mis_prestamos_view(request):
    """HU2: Ver préstamos con colores por urgencia y días faltantes"""
    hoy = date.today()
    prestamos_qs = Prestamo.objects.filter(usuario=request.user).order_by('fecha_entrega')

    prestamos = []
    for p in prestamos_qs:
        dias_restantes = (p.fecha_entrega - hoy).days if p.fecha_entrega else None

        # CA1: lógica de color
        if p.estado in ['devuelto', 'cancelado', 'rechazado']:
            color = 'secondary'
        elif dias_restantes is None:
            color = 'secondary'
        elif dias_restantes < 0:
            color = 'danger'     # rojo: atrasado
        elif dias_restantes <= 2:
            color = 'warning'    # amarillo: menos de 2 días
        else:
            color = 'success'    # verde: con tiempo

        prestamos.append({
            'obj': p,
            'dias_restantes': dias_restantes,
            'color': color,
        })

    context = {
        'prestamos': prestamos,
        'total_pendientes': prestamos_qs.filter(estado='pendiente').count(),
        'total_aprobados': prestamos_qs.filter(estado='aprobado').count(),
        'total_activos': prestamos_qs.filter(estado__in=['pendiente', 'aprobado']).count(),
    }
    return render(request, 'accounts/mis_prestamos.html', context)


@login_required(login_url='/login/')
def cancelar_prestamo_view(request, pk):
    """HU7 CA5: Cancelar solicitud de préstamo"""
    prestamo = get_object_or_404(Prestamo, pk=pk, usuario=request.user)

    if prestamo.estado not in ['pendiente']:
        messages.error(request, '❌ Solo puedes cancelar solicitudes en estado pendiente.')
        return redirect('mis_prestamos')

    if request.method == 'POST':
        prestamo.estado = 'cancelado'
        prestamo.save()
        messages.success(request, f'✅ Solicitud de préstamo para "{prestamo.equipo.nombre}" cancelada.')
        return redirect('mis_prestamos')

    return render(request, 'accounts/cancelar_prestamo.html', {'prestamo': prestamo})


@login_required(login_url='/login/')
def solicitar_cambio_equipo_view(request, pk):
    """HU2 CA4: Solicitar cambio de equipo por fallo"""
    prestamo = get_object_or_404(Prestamo, pk=pk, usuario=request.user)

    if prestamo.estado not in ['aprobado', 'entregado']:
        messages.error(request, '❌ Solo puedes solicitar cambio en préstamos aprobados o entregados.')
        return redirect('mis_prestamos')

    if request.method == 'POST':
        motivo_cambio = request.POST.get('motivo_cambio', '').strip()
        if not motivo_cambio:
            messages.error(request, '❌ Debes ingresar el motivo del cambio.')
            return render(request, 'accounts/solicitar_cambio_equipo.html', {'prestamo': prestamo})

        prestamo.observaciones = f'[CAMBIO SOLICITADO] {motivo_cambio}'
        prestamo.save()

        # Notificar al administrador por correo
        admins = Usuario.objects.filter(idRol__descripcion='administrador')
        correos_admin = [a.correo for a in admins if a.correo]
        if correos_admin:
            send_mail(
                '🔄 Solicitud de Cambio de Equipo',
                f'El usuario {request.user.nombre} {request.user.apellido} '
                f'ha solicitado un cambio del equipo "{prestamo.equipo.nombre}".\n\n'
                f'Motivo: {motivo_cambio}',
                settings.DEFAULT_FROM_EMAIL,
                correos_admin,
                fail_silently=True,
            )

        messages.success(request, '✅ Solicitud de cambio enviada. El administrador será notificado.')
        return redirect('mis_prestamos')

    return render(request, 'accounts/solicitar_cambio_equipo.html', {'prestamo': prestamo})


# ─── HU12: GESTIÓN DE PRÉSTAMOS (ENCARGADO) ──────────────────────────────────


@solo_encargado
def gestion_prestamos_view(request):
    """HU12 CA1 y CA2: Ver solicitudes y estado de equipos"""
    prestamos_pendientes = Prestamo.objects.filter(estado='pendiente').order_by('creado_en')
    prestamos_gestionados = Prestamo.objects.exclude(estado='pendiente').order_by('-actualizado_en')[:20]

    context = {
        'prestamos_pendientes': prestamos_pendientes,
        'prestamos_gestionados': prestamos_gestionados,
        'total_pendientes': prestamos_pendientes.count(),
    }
    return render(request, 'accounts/gestion_prestamos.html', context)


@solo_encargado
def aprobar_prestamo_view(request, pk):
    """HU12 CA2: Aprobar solicitud de préstamo"""
    prestamo = get_object_or_404(Prestamo, pk=pk)

    if prestamo.estado != 'pendiente':
        messages.error(request, '❌ Solo se pueden aprobar solicitudes pendientes.')
        return redirect('gestion_prestamos')

    if request.method == 'POST':
        prestamo.estado = 'aprobado'
        prestamo.observaciones = request.POST.get('observaciones', '')
        prestamo.save()
        equipo = prestamo.equipo
        equipo.estado = 'prestado'
        equipo.save()
        
        # HU3: Notificar al usuario
        Notificacion.objects.create(
            usuario=prestamo.usuario,
            tipo='prestamo_aprobado',
            mensaje=f'Tu préstamo del equipo "{prestamo.equipo.nombre}" fue aprobado. ¡Ya puedes recogerlo!',
            prestamo=prestamo
        )
        messages.success(request, f'✅ Préstamo de "{equipo.nombre}" aprobado correctamente.')
        return redirect('gestion_prestamos')

    return render(request, 'accounts/aprobar_prestamo.html', {'prestamo': prestamo})


@solo_encargado
def denegar_prestamo_view(request, pk):
    """HU12 CA3: Denegar solicitud de préstamo"""
    prestamo = get_object_or_404(Prestamo, pk=pk)

    if prestamo.estado != 'pendiente':
        messages.error(request, '❌ Solo se pueden denegar solicitudes pendientes.')
        return redirect('gestion_prestamos')

    if request.method == 'POST':
        prestamo.estado = 'rechazado'
        prestamo.observaciones = request.POST.get('observaciones', '')
        prestamo.save()
        
        # HU3: Notificar al usuario
        Notificacion.objects.create(
            usuario=prestamo.usuario,
            tipo='prestamo_rechazado',
            mensaje=f'Tu préstamo del equipo "{prestamo.equipo.nombre}" fue rechazado. Motivo: {prestamo.observaciones or "Sin observaciones"}.',
            prestamo=prestamo
        )

        messages.success(request, f'✅ Solicitud de "{prestamo.equipo.nombre}" denegada.')
        return redirect('gestion_prestamos')

    return render(request, 'accounts/denegar_prestamo.html', {'prestamo': prestamo})


# ─── HU09: GESTIÓN DE ITEMS DE INVENTARIO ────────────────────────────────────


@solo_encargado
def items_lista_view(request):
    """HU09: Listar todos los ítems de inventario"""
    items = Item.objects.all().order_by('nombre')

    busqueda = request.GET.get('busqueda', '').strip()
    if busqueda:
        items = items.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )

    categoria_filtro = request.GET.get('categoria', '')
    if categoria_filtro:
        items = items.filter(categoria__id=categoria_filtro)

    categorias = CategoriaItem.objects.all()

    context = {
        'items': items,
        'categorias': categorias,
        'busqueda': busqueda,
        'categoria_filtro': categoria_filtro,
        'total_items': Item.objects.count(),
    }
    return render(request, 'accounts/items_lista.html', context)


@solo_encargado
def item_crear_view(request):
    """HU09: Crear nuevo ítem de inventario"""
    form = ItemForm()

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'✅ Ítem "{item.nombre}" creado correctamente.')
            return redirect('items_lista')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    return render(request, 'accounts/item_crear.html', {'form': form})


@solo_encargado
def item_editar_view(request, pk):
    """HU09: Editar ítem de inventario"""
    item = get_object_or_404(Item, pk=pk)
    form = ItemForm(instance=item)

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'✅ Ítem "{item.nombre}" actualizado correctamente.')
            return redirect('items_lista')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    context = {'form': form, 'item': item, 'modo': 'editar'}
    return render(request, 'accounts/item_editar.html', context)


@solo_encargado
def item_eliminar_view(request, pk):
    """HU09: Eliminar ítem de inventario"""
    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        nombre = item.nombre
        item.delete()
        messages.success(request, f'✅ Ítem "{nombre}" eliminado correctamente.')
        return redirect('items_lista')

    context = {'item': item, 'modo': 'eliminar'}
    return render(request, 'accounts/item_eliminar.html', context)


# ─── HU10: GESTIÓN DE EQUIPOS ────────────────────────────────────────────────


@solo_encargado
def equipos_gestion_lista_view(request):
    """HU10: Listar todos los equipos (para encargado)"""
    equipos = Equipo.objects.all().order_by('nombre')

    busqueda = request.GET.get('busqueda', '').strip()
    if busqueda:
        equipos = equipos.filter(
            Q(nombre__icontains=busqueda) |
            Q(marca__icontains=busqueda) |
            Q(modelo__icontains=busqueda) |
            Q(numero_serie__icontains=busqueda)
        )

    categoria_filtro = request.GET.get('categoria', '')
    if categoria_filtro:
        equipos = equipos.filter(categoria__id=categoria_filtro)

    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        equipos = equipos.filter(estado=estado_filtro)

    categorias = CategoriaEquipo.objects.all()
    estados = Equipo.ESTADO_CHOICES

    context = {
        'equipos': equipos,
        'categorias': categorias,
        'estados': estados,
        'busqueda': busqueda,
        'categoria_filtro': categoria_filtro,
        'estado_filtro': estado_filtro,
        'total_equipos': Equipo.objects.count(),
        'total_disponibles': Equipo.objects.filter(estado='disponible').count(),
        'total_prestados': Equipo.objects.filter(estado='prestado').count(),
        'total_mantenimiento': Equipo.objects.filter(estado='mantenimiento').count(),
    }
    return render(request, 'accounts/equipos_lista.html', context)


@solo_encargado
def equipo_crear_view(request):
    """HU10: Crear nuevo equipo"""
    form = EquipoForm()

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save()
            messages.success(request, f'✅ Equipo "{equipo.nombre}" creado correctamente.')
            return redirect('equipos_lista')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    return render(request, 'accounts/equipo_crear.html', {'form': form})


@solo_encargado
def equipo_editar_view(request, pk):
    """HU10: Editar equipo"""
    equipo = get_object_or_404(Equipo, pk=pk)
    form = EquipoForm(instance=equipo)

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            equipo = form.save()
            messages.success(request, f'✅ Equipo "{equipo.nombre}" actualizado correctamente.')
            return redirect('equipos_lista')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    context = {'form': form, 'equipo': equipo, 'modo': 'editar'}
    return render(request, 'accounts/equipo_editar.html', context)


@solo_encargado
def equipo_eliminar_view(request, pk):
    """HU10: Eliminar equipo"""
    equipo = get_object_or_404(Equipo, pk=pk)

    if request.method == 'POST':
        nombre = equipo.nombre
        equipo.delete()
        messages.success(request, f'✅ Equipo "{nombre}" eliminado correctamente.')
        return redirect('equipos_lista')

    context = {'equipo': equipo, 'modo': 'eliminar'}
    return render(request, 'accounts/equipo_eliminar.html', context)


# ─── HU11: GESTIÓN DE TICKETS DE MANTENIMIENTO ───────────────────────────────


@solo_encargado
def tickets_lista_view(request):
    """HU11: Listar todos los tickets de mantenimiento"""
    tickets = Ticket.objects.all().order_by('-fecha_creacion')

    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        tickets = tickets.filter(estado=estado_filtro)

    tipo_filtro = request.GET.get('tipo', '')
    if tipo_filtro:
        tickets = tickets.filter(tipo=tipo_filtro)

    busqueda = request.GET.get('busqueda', '').strip()
    if busqueda:
        tickets = tickets.filter(
            Q(equipo__nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )

    context = {
        'tickets': tickets,
        'estados': Ticket.ESTADO_CHOICES,
        'tipos': Ticket.TIPO_CHOICES,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
        'busqueda': busqueda,
        'total_tickets': Ticket.objects.count(),
        'total_no_atendidos': Ticket.objects.filter(estado='no_atendido').count(),
        'total_en_proceso': Ticket.objects.filter(estado='en_proceso').count(),
        'total_finalizados': Ticket.objects.filter(estado='finalizado').count(),
    }
    return render(request, 'accounts/tickets_lista.html', context)


@solo_encargado
def ticket_crear_view(request):
    """HU11: Crear nuevo ticket"""
    form = TicketForm()

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            messages.success(request, f'✅ Ticket #{ticket.pk} creado para "{ticket.equipo.nombre}".')
            return redirect('tickets_lista')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    return render(request, 'accounts/ticket_crear.html', {'form': form})


@solo_encargado
def ticket_editar_view(request, pk):
    """HU11: Editar ticket (cambiar estado y notas)"""
    ticket = get_object_or_404(Ticket, pk=pk)
    form = TicketEditForm(instance=ticket)

    if request.method == 'POST':
        form = TicketEditForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()
            messages.success(request, f'✅ Ticket #{ticket.pk} actualizado correctamente.')
            return redirect('tickets_lista')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    context = {'form': form, 'ticket': ticket, 'modo': 'editar'}
    return render(request, 'accounts/ticket_editar.html', context)


# ─── HU16: INVENTARIO GENERAL (ADMINISTRADOR) ────────────────────────────────


@solo_administrador
def inventario_general_view(request):
    """HU16 CA1: Ver inventario completo de equipos e ítems"""
    equipos = Equipo.objects.all().order_by('nombre')
    items = Item.objects.all().order_by('nombre')

    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        equipos = equipos.filter(estado=estado_filtro)

    categoria_filtro = request.GET.get('categoria', '')
    if categoria_filtro:
        equipos = equipos.filter(categoria__id=categoria_filtro)

    busqueda = request.GET.get('busqueda', '').strip()
    if busqueda:
        equipos = equipos.filter(
            Q(nombre__icontains=busqueda) |
            Q(marca__icontains=busqueda) |
            Q(modelo__icontains=busqueda) |
            Q(numero_serie__icontains=busqueda)
        )
        items = items.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )

    categorias = CategoriaEquipo.objects.all()

    context = {
        'equipos': equipos,
        'items': items,
        'categorias': categorias,
        'estados': Equipo.ESTADO_CHOICES,
        'estado_filtro': estado_filtro,
        'categoria_filtro': categoria_filtro,
        'busqueda': busqueda,
        'total_equipos': Equipo.objects.count(),
        'total_disponibles': Equipo.objects.filter(estado='disponible').count(),
        'total_prestados': Equipo.objects.filter(estado='prestado').count(),
        'total_mantenimiento': Equipo.objects.filter(estado='mantenimiento').count(),
        'total_items': Item.objects.count(),
    }
    return render(request, 'accounts/inventario_general.html', context)


@solo_administrador
def inventario_detalle_view(request, pk):
    """HU16 CA2: Ver detalle de un equipo con historial y estado"""
    equipo = get_object_or_404(Equipo, pk=pk)
    historial_prestamos = Prestamo.objects.filter(equipo=equipo).order_by('-creado_en')
    tickets = Ticket.objects.filter(equipo=equipo).order_by('-fecha_creacion')

    responsable = Prestamo.objects.filter(
        equipo=equipo,
        estado__in=['aprobado', 'entregado']
    ).first()

    context = {
        'equipo': equipo,
        'historial_prestamos': historial_prestamos,
        'tickets': tickets,
        'responsable': responsable,
        'total_prestamos': historial_prestamos.count(),
        'total_tickets': tickets.count(),
    }
    return render(request, 'accounts/inventario_detalle.html', context)


# ─── HU17: HISTORIAL DE PRÉSTAMOS (ADMINISTRADOR) ────────────────────────────


@solo_administrador
def historial_prestamos_view(request):
    """HU17 CA1: Ver historial completo de préstamos"""
    prestamos = Prestamo.objects.all().order_by('-creado_en')

    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        prestamos = prestamos.filter(estado=estado_filtro)

    equipo_filtro = request.GET.get('equipo', '')
    if equipo_filtro:
        prestamos = prestamos.filter(equipo__id=equipo_filtro)

    busqueda = request.GET.get('busqueda', '').strip()
    if busqueda:
        prestamos = prestamos.filter(
            Q(usuario__nombre__icontains=busqueda) |
            Q(usuario__apellido__icontains=busqueda) |
            Q(equipo__nombre__icontains=busqueda)
        )

    equipos = Equipo.objects.all().order_by('nombre')

    context = {
        'prestamos': prestamos,
        'equipos': equipos,
        'estados': Prestamo.ESTADO_CHOICES,
        'estado_filtro': estado_filtro,
        'equipo_filtro': equipo_filtro,
        'busqueda': busqueda,
        'total_prestamos': Prestamo.objects.count(),
        'total_pendientes': Prestamo.objects.filter(estado='pendiente').count(),
        'total_aprobados': Prestamo.objects.filter(estado='aprobado').count(),
        'total_devueltos': Prestamo.objects.filter(estado='devuelto').count(),
    }
    return render(request, 'accounts/historial_prestamos.html', context)


@solo_administrador
def historial_prestamo_detalle_view(request, pk):
    """HU17 CA2: Ver detalle de un préstamo específico"""
    prestamo = get_object_or_404(Prestamo, pk=pk)
    return render(request, 'accounts/historial_prestamo_detalle.html', {'prestamo': prestamo})


# ─── HU3: NOTIFICACIONES ─────────────────────────────────────────────────────

def generar_notificaciones_prestamos(usuario):
    """
    Genera automáticamente notificaciones para préstamos atrasados
    o que vencen hoy. Evita duplicados del mismo día.
    """
    from datetime import date
    hoy = date.today()

    prestamos_activos = Prestamo.objects.filter(
        usuario=usuario,
        estado__in=['aprobado', 'entregado']
    )

    for prestamo in prestamos_activos:
        dias = (prestamo.fecha_entrega - hoy).days

        if dias < 0:
            tipo = 'prestamo_atrasado'
            mensaje = (
                f'Tu préstamo del equipo "{prestamo.equipo.nombre}" '
                f'está atrasado {abs(dias)} día(s). Por favor, devuélvelo.'
            )
        elif dias == 0:
            tipo = 'prestamo_vence_hoy'
            mensaje = (
                f'Tu préstamo del equipo "{prestamo.equipo.nombre}" '
                f'vence HOY. Recuerda devolverlo.'
            )
        else:
            continue  # sin notificación si aún tiene tiempo

        # Evitar duplicar notificaciones del mismo tipo y préstamo en el mismo día
        ya_existe = Notificacion.objects.filter(
            usuario=usuario,
            tipo=tipo,
            prestamo=prestamo,
            creado_en__date=hoy
        ).exists()

        if not ya_existe:
            Notificacion.objects.create(
                usuario=usuario,
                tipo=tipo,
                mensaje=mensaje,
                prestamo=prestamo
            )


@login_required(login_url='/login/')
def notificaciones_view(request):
    """HU3 CA1 y CA2: Ver todas las notificaciones del usuario"""
    # Generar notificaciones automáticas antes de mostrar
    generar_notificaciones_prestamos(request.user)

    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-creado_en')[:30]

    # Marcar todas como leídas al abrir la página
    Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).update(leida=True)

    context = {
        'notificaciones': notificaciones,
        'total': notificaciones.count(),
    }
    return render(request, 'accounts/notificaciones.html', context)


@login_required(login_url='/login/')
def marcar_notificacion_leida_view(request, pk):
    """HU3: Marcar una notificación individual como leída"""
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notificacion.leida = True
    notificacion.save()
    return redirect('notificaciones')

# ─── HU5: HISTORIAL DE PRÉSTAMOS (USUARIO SOLICITANTE) ───────────────────────

@login_required(login_url='/login/')
def historial_mis_prestamos_view(request):
    """HU5 CA1: Ver historial completo de préstamos del usuario solicitante"""
    prestamos = Prestamo.objects.filter(usuario=request.user).order_by('-creado_en')

    # Filtro por estado
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        prestamos = prestamos.filter(estado=estado_filtro)

    context = {
        'prestamos': prestamos,
        'estados': Prestamo.ESTADO_CHOICES,
        'estado_filtro': estado_filtro,
        'total': prestamos.count(),
        'total_pendientes':  Prestamo.objects.filter(usuario=request.user, estado='pendiente').count(),
        'total_aprobados':   Prestamo.objects.filter(usuario=request.user, estado='aprobado').count(),
        'total_devueltos':   Prestamo.objects.filter(usuario=request.user, estado='devuelto').count(),
        'total_rechazados':  Prestamo.objects.filter(usuario=request.user, estado='rechazado').count(),
    }
    return render(request, 'accounts/historial_mis_prestamos.html', context)


@login_required(login_url='/login/')
def historial_mis_prestamos_detalle_view(request, pk):
    """HU5 CA2: Ver detalle de un préstamo específico del usuario"""
    prestamo = get_object_or_404(Prestamo, pk=pk, usuario=request.user)
    return render(request, 'accounts/historial_mis_prestamos_detalle.html', {'prestamo': prestamo})

