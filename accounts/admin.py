from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['id', 'descripcion']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ['usuario', 'nombre', 'apellido', 'correo', 'idRol', 'is_active']
    list_filter = ['idRol', 'is_active']
    fieldsets = (
        (None, {'fields': ('usuario', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido', 'correo', 'idRol')}),
        ('Control de Acceso', {'fields': ('intentos_fallidos', 'bloqueado_hasta')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('usuario', 'nombre', 'apellido', 'correo', 'idRol', 'password1', 'password2'),
        }),
    )
    search_fields = ['usuario', 'nombre', 'apellido', 'correo']
    ordering = ['usuario']
