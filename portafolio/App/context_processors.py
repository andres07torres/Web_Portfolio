from .models import Personalizacion

def personalizacion_context(request):
    """Hace que la configuración de UI esté disponible en todos los templates."""
    try:
        config = Personalizacion.objects.first()
        if not config:
            # Si no existe, creamos el primer registro con valores default
            config = Personalizacion.objects.create()
    except:
        config = None
    
    return {
        'config_ui': config
    }

def redes_sociales_context(request):
    from .models import RedSocial
    return {
        'redes_sociales': RedSocial.objects.all().order_by('orden', 'nombre')
    }
