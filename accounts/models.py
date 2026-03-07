from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta


class Rol(models.Model):
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('encargado_tecnologia', 'Encargado de Tecnología'),
        ('usuario_solicitante', 'Usuario Solicitante (Docente/Estudiante)'),
    ]
    descripcion = models.CharField(
        max_length=50,
        choices=ROL_CHOICES,
        unique=True
    )

    def __str__(self):
        return self.get_descripcion_display()

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'


class UsuarioManager(BaseUserManager):
    def create_user(self, usuario, password=None, **extra_fields):
        if not usuario:
            raise ValueError('El nombre de usuario es obligatorio')
        user = self.model(usuario=usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, usuario, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(usuario, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    idRol = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Rol'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    correo = models.EmailField(unique=True, verbose_name='Correo')
    usuario = models.CharField(max_length=100, unique=True, verbose_name='Usuario')

    # Campos para control de bloqueo por intentos fallidos - HU13
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)

    # Campos para recuperación de contraseña - HU13
    token_recuperacion = models.CharField(max_length=255, blank=True, null=True)
    token_recuperacion_expira = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Auditoria - HU14
    creado_en = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    actualizado_en = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'usuario'
    EMAIL_FIELD = 'correo'
    REQUIRED_FIELDS = ['correo', 'nombre', 'apellido']

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.usuario})'

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def incrementar_intentos_fallidos(self):
        """HU13: Incrementa intentos fallidos y bloquea si es necesario"""
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 3:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=2)
            self.intentos_fallidos = 0
        self.save()

    def resetear_intentos(self):
        """HU13: Resetea intentos después de login exitoso"""
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.save()

    def esta_bloqueado(self):
        """HU13: Verifica si la cuenta está bloqueada"""
        if self.bloqueado_hasta and timezone.now() < self.bloqueado_hasta:
            return True
        elif self.bloqueado_hasta and timezone.now() >= self.bloqueado_hasta:
            self.bloqueado_hasta = None
            self.save()
            return False
        return False

    def obtener_rol_display(self):
        """HU14: Obtiene nombre legible del rol"""
        if self.idRol:
            return self.idRol.get_descripcion_display()
        return 'Sin Rol'


# ─── UH6: INVENTARIO DE EQUIPOS ──────────────────────────────────────────────

class CategoriaEquipo(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Categoría')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class Equipo(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('prestado', 'Prestado'),
        ('mantenimiento', 'En Mantenimiento'),
        ('dañado', 'Dañado'),
        ('dado_de_baja', 'Dado de Baja'),
    ]

    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    categoria = models.ForeignKey(
        CategoriaEquipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Categoría'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name='Marca')
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Modelo')
    numero_serie = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name='Número de Serie')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name='Estado'
    )
    imagen = models.ImageField(upload_to='equipos/', blank=True, null=True, verbose_name='Imagen')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.nombre} ({self.get_estado_display()})'

    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['nombre']


# ─── HU7: PRÉSTAMOS ──────────────────────────────────────────────────────────

class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('entregado', 'Entregado'),
        ('devuelto', 'Devuelto'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='prestamos',
        verbose_name='Usuario'
    )
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='prestamos',
        verbose_name='Equipo'
    )
    fecha_reclamo = models.DateField(verbose_name='Fecha de Reclamo')
    fecha_entrega = models.DateField(verbose_name='Fecha de Entrega')
    motivo = models.TextField(verbose_name='Motivo del Préstamo')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Préstamo de {self.equipo.nombre} por {self.usuario.nombre} ({self.get_estado_display()})'

    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = ['-creado_en']
