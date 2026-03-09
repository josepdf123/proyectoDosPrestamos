from .models import Notificacion
from datetime import date

def notificaciones_processor(request):
    if request.user.is_authenticated and hasattr(request.user, 'idRol') \
            and request.user.idRol \
            and request.user.idRol.descripcion == 'usuario_solicitante':

        # Generar notificaciones automáticas en cada request
        from .views import generar_notificaciones_prestamos
        generar_notificaciones_prestamos(request.user)

        no_leidas = Notificacion.objects.filter(
            usuario=request.user,
            leida=False
        ).count()

        ultimas = Notificacion.objects.filter(
            usuario=request.user
        ).order_by('-creado_en')[:5]

        return {
            'notif_no_leidas': no_leidas,
            'ultimas_notificaciones': ultimas,
        }
    return {
        'notif_no_leidas': 0,
        'ultimas_notificaciones': [],
    }
