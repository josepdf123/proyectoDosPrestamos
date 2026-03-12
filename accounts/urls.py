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
    
    # HU6 - Equipos Disponibles (Usuario Solicitante)
    path('equipos-disponibles/', views.equipos_disponibles_view, name='equipos_disponibles'),
    path('equipo/<int:pk>/', views.equipo_detalle_view, name='equipo_detalle'),
    
    # HU7 - Préstamos (Usuario Solicitante)
    path('solicitar-prestamo/<int:pk>/', views.solicitar_prestamo_view, name='solicitar_prestamo'),
    path('mis-prestamos/', views.mis_prestamos_view, name='mis_prestamos'),
    path('cancelar-prestamo/<int:pk>/', views.cancelar_prestamo_view, name='cancelar_prestamo'),
    
    # HU12 - Gestión de Préstamos (Encargado)
    path('gestion-prestamos/', views.gestion_prestamos_view, name='gestion_prestamos'),
    path('aprobar-prestamo/<int:pk>/', views.aprobar_prestamo_view, name='aprobar_prestamo'),
    path('denegar-prestamo/<int:pk>/', views.denegar_prestamo_view, name='denegar_prestamo'),
    
    # HU09 - Gestión de Items (Encargado)
    path('items/', views.items_lista_view, name='items_lista'),
    path('items/crear/', views.item_crear_view, name='item_crear'),
    path('items/editar/<int:pk>/', views.item_editar_view, name='item_editar'),
    path('items/eliminar/<int:pk>/', views.item_eliminar_view, name='item_eliminar'),
    
    # HU10 - Gestión de Equipos (Encargado)
    path('equipos/', views.equipos_gestion_lista_view, name='equipos_lista'),
    path('equipos/crear/', views.equipo_crear_view, name='equipo_crear'),
    path('equipos/editar/<int:pk>/', views.equipo_editar_view, name='equipo_editar'),
    path('equipos/eliminar/<int:pk>/', views.equipo_eliminar_view, name='equipo_eliminar'),
    
    # HU11 - Gestión de Tickets (Encargado)
    path('tickets/', views.tickets_lista_view, name='tickets_lista'),
    path('tickets/crear/', views.ticket_crear_view, name='ticket_crear'),
    path('tickets/editar/<int:pk>/', views.ticket_editar_view, name='ticket_editar'),
    
    # HU16 - Inventario General (Administrador)
    path('inventario/', views.inventario_general_view, name='inventario_general'),
    path('inventario/<int:pk>/', views.inventario_detalle_view, name='inventario_detalle'),
    
    # HU17 - Historial de Préstamos (Administrador)
    path('historial-prestamos/', views.historial_prestamos_view, name='historial_prestamos'),
    path('historial-prestamos/<int:pk>/', views.historial_prestamo_detalle_view, name='historial_prestamo_detalle'),
    
    # HU2 - Cambio de equipo
    path('solicitar-cambio-equipo/<int:pk>/', views.solicitar_cambio_equipo_view, name='solicitar_cambio_equipo'),
    
    # HU3 - Notificaciones
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),
    path('notificaciones/<int:pk>/leida/', views.marcar_notificacion_leida_view, name='marcar_notificacion_leida'),
    
    # HU5 - Historial mis préstamos
    path('historial-mis-prestamos/', views.historial_mis_prestamos_view, name='historial_mis_prestamos'),
    path('historial-mis-prestamos/<int:pk>/', views.historial_mis_prestamos_detalle_view, name='historial_mis_prestamos_detalle'),
    # HU18 - Reportes de Préstamos
    path('reportes-prestamos/', views.reportes_prestamos_view, name='reportes_prestamos'),
    path('reportes-prestamos/descargar-pdf/', views.descargar_reporte_prestamos_pdf, name='descargar_reporte_prestamos_pdf'),
    path('reportes-prestamos/descargar-excel/', views.descargar_reporte_prestamos_excel, name='descargar_reporte_prestamos_excel'),
    
    # HU19 - Reportes de Reparaciones
    path('reportes-reparaciones/', views.reportes_reparaciones_view, name='reportes_reparaciones'),
    path('reportes-reparaciones/descargar-pdf/', views.descargar_reporte_reparaciones_pdf, name='descargar_reporte_reparaciones_pdf'),
    path('reportes-reparaciones/descargar-excel/', views.descargar_reporte_reparaciones_excel, name='descargar_reporte_reparaciones_excel'),
    
    # HU20 - Métricas y Estadísticas
    path('metricas/', views.metricas_view, name='metricas'),
    
    path('registro/', views.registro_view, name='registro'),
]
