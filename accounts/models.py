from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


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

    # Campos para control de bloqueo por intentos fallidos
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'usuario'
    EMAIL_FIELD = 'correo'          # ← línea agregada
    REQUIRED_FIELDS = ['correo', 'nombre', 'apellido']

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.usuario})'

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
