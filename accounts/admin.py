from django.contrib import admin
from .models import (Usuario, Rol, Item, CategoriaItem, Equipo, 
                     CategoriaEquipo, Ticket, Prestamo, Notificacion)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre', 'apellido', 'correo', 'idRol')
    list_filter = ('idRol', 'is_active')
    search_fields = ('usuario', 'nombre', 'correo')

@admin.register(CategoriaItem)
class CategoriaItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'cantidad', 'estado')
    list_filter = ('estado', 'categoria')

@admin.register(CategoriaEquipo)
class CategoriaEquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'estado', 'numero_serie')
    list_filter = ('estado', 'categoria')
    search_fields = ('nombre', 'numero_serie')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipo', 'tipo', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'tipo')

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'equipo', 'estado', 'fecha_reclamo')
    list_filter = ('estado', 'creado_en')

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'leida', 'creado_en')
    list_filter = ('tipo', 'leida')
    search_fields = ('mensaje', 'usuario__nombre')