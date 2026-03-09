from django.contrib import admin
from .models import Usuario, Rol, Item, CategoriaItem, Equipo, CategoriaEquipo, Ticket, Prestamo

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre', 'apellido', 'correo', 'idRol', 'is_active')
    list_filter = ('idRol', 'is_active')
    search_fields = ('usuario', 'nombre', 'apellido', 'correo')

@admin.register(CategoriaItem)
class CategoriaItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'cantidad', 'cantidad_disponible', 'estado')
    list_filter = ('categoria', 'estado')
    search_fields = ('nombre',)

@admin.register(CategoriaEquipo)
class CategoriaEquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'marca', 'modelo', 'estado')
    list_filter = ('categoria', 'estado')
    search_fields = ('nombre', 'numero_serie')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipo', 'tipo', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'tipo')
    search_fields = ('equipo__nombre', 'descripcion')

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'equipo', 'fecha_reclamo', 'fecha_entrega', 'estado')
    list_filter = ('estado', 'creado_en')
    search_fields = ('usuario__nombre', 'equipo__nombre')