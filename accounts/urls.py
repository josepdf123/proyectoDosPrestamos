from django.urls import path
from . import views

urlpatterns = [
    # HU13 - Login y Recuperación de Contraseña
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperacion-contrasena/', views.recuperacion_contrasena_view, name='recuperacion_contrasena'),
    path('restablecer-contrasena/<str:token>/', views.restablecer_contrasena_view, name='restablecer_contrasena'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # HU14 - Gestión de Usuarios (Solo Administrador)
    path('usuarios/', views.usuarios_lista_view, name='usuarios_lista'),
    path('usuarios/crear/', views.usuario_crear_view, name='usuario_crear'),
    path('usuarios/editar/<int:pk>/', views.usuario_editar_view, name='usuario_editar'),
    path('usuarios/eliminar/<int:pk>/', views.usuario_eliminar_view, name='usuario_eliminar'),
]
