from django.db import models
from django.contrib.auth.models import User


class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.usuario.username


class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre_categoria


class Equipo(models.Model):

    ESTADOS = [
        ('disponible', 'Disponible'),
        ('prestado', 'Prestado'),
        ('reparacion', 'En reparación'),
        ('baja', 'Dado de baja')
    ]

    codigo_inventario = models.CharField(max_length=100, unique=True)
    nombre_equipo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='disponible'
    )

    fecha_adquisicion = models.DateField(null=True, blank=True)
    ubicacion = models.CharField(max_length=100, blank=True)

    responsable_actual = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre_equipo


class Prestamo(models.Model):

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('finalizado', 'Finalizado')
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="prestamos_solicitados"
    )

    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE
    )

    aprobado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prestamos_aprobados"
    )

    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    fecha_devolucion = models.DateField(null=True, blank=True)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente'
    )

    motivo = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Prestamo {self.id} - {self.equipo.nombre_equipo}"


class Incidencia(models.Model):

    TIPOS = [
        ('daño', 'Daño'),
        ('mantenimiento', 'Mantenimiento'),
        ('perdida', 'Pérdida')
    ]

    ESTADOS = [
        ('abierta', 'Abierta'),
        ('proceso', 'En proceso'),
        ('cerrada', 'Cerrada')
    ]

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)

    prestamo = models.ForeignKey(
        Prestamo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    descripcion = models.TextField()

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    fecha_reporte = models.DateTimeField(auto_now_add=True)

    reportado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='abierta'
    )

    def __str__(self):
        return f"Incidencia {self.id} - {self.tipo}"


class Notificacion(models.Model):

    TIPOS = [
        ('recordatorio', 'Recordatorio'),
        ('aprobacion', 'Aprobación'),
        ('rechazo', 'Rechazo')
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    mensaje = models.TextField()

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    fecha_envio = models.DateTimeField(auto_now_add=True)

    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación {self.id}"