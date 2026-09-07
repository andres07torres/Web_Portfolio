from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import escape
import json
import re
from .models import AcercaDe, Habilidad, Experiencia, Proyecto, Personalizacion, RedSocial
from .forms import (
    AcercaDeForm, HabilidadForm, ExperienciaForm, 
    ProyectoForm, PersonalizacionForm, RedSocialForm
)

# ─── Seguridad: Rate Limiting ─────────────────────────────────
MAX_LOGIN_ATTEMPTS  = 5     # Intentos antes de bloqueo
LOGIN_BLOCK_SECONDS = 300   # 5 minutos de bloqueo
MAX_CONTACT_PER_HOUR = 3   # Envíos de contacto por hora por IP

def get_client_ip(request):
    """Extrae la IP real incluso detrás de proxies/Nginx."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


# ─── Portafolio público ───────────────────────────────────────
def base(request):
    return render(request, 'index.html')

# ─── SEO: robots.txt ──────────────────────────────────────────
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /login/",
        "Disallow: /section/",
        "",
        "Sitemap: https://" + request.get_host() + "/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

# ─── SEO: sitemap.xml ─────────────────────────────────────────
def sitemap_xml(request):
    from django.urls import reverse
    urls = [
        {"loc": request.build_absolute_uri(reverse("base")), "changefreq": "weekly", "priority": "1.0"},
    ]
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        xml_parts.append("  <url>")
        xml_parts.append(f"    <loc>{u['loc']}</loc>")
        xml_parts.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        xml_parts.append(f"    <priority>{u['priority']}</priority>")
        xml_parts.append("  </url>")
    xml_parts.append("</urlset>")
    return HttpResponse("\n".join(xml_parts), content_type="application/xml")

# ─── Lazy Section Load (AJAX) ────────────────────────────────
def section_sobre_mi(request):
    acerca_de = AcercaDe.objects.first()
    habilidades = Habilidad.objects.all().order_by('orden')
    html = render_to_string('secciones/sobre_mi.html', {
        'acerca_de': acerca_de,
        'habilidades': habilidades,
    }, request=request)
    return HttpResponse(html)

def section_experiencia(request):
    experiencias = Experiencia.objects.all().order_by('-orden')
    html = render_to_string('secciones/experiencia.html', {
        'experiencias': experiencias,
    }, request=request)
    return HttpResponse(html)

def section_proyectos(request):
    proyectos = Proyecto.objects.all().order_by('orden')
    html = render_to_string('secciones/proyectos.html', {
        'proyectos': proyectos,
    }, request=request)
    return HttpResponse(html)

def section_contacto(request):
    html = render_to_string('secciones/contacto.html', {}, request=request)
    return HttpResponse(html)

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ip  = get_client_ip(self.request)
        ctx['attempts_left'] = max(0, MAX_LOGIN_ATTEMPTS - cache.get(f'login_attempts_{ip}', 0))
        ctx['is_blocked']    = cache.get(f'login_blocked_{ip}', False)
        return ctx

    def form_invalid(self, form):
        ip  = get_client_ip(self.request)
        key = f'login_attempts_{ip}'
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, timeout=LOGIN_BLOCK_SECONDS)
        if attempts >= MAX_LOGIN_ATTEMPTS:
            cache.set(f'login_blocked_{ip}', True, timeout=LOGIN_BLOCK_SECONDS)
        return super().form_invalid(form)

    def form_valid(self, form):
        ip = get_client_ip(self.request)
        cache.delete(f'login_attempts_{ip}')
        cache.delete(f'login_blocked_{ip}')
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        ip = get_client_ip(request)
        if cache.get(f'login_blocked_{ip}'):
            return render(request, 'login.html', {
                'is_blocked': True,
                'attempts_left': 0,
                'form': self.get_form(),
            })
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ip = get_client_ip(request)
        if cache.get(f'login_blocked_{ip}'):
            return render(request, 'login.html', {
                'is_blocked': True,
                'attempts_left': 0,
                'form': self.get_form(),
            })
        return super().post(request, *args, **kwargs)

def custom_logout(request):
    auth_logout(request)
    return redirect('/')

# ─── Formulario de Contacto ───────────────────────────────────
def contacto(request):
    if request.method != 'POST':
        return redirect('base')

    ip = get_client_ip(request)

    # ── 1. Honeypot anti-bot ──────────────────────────────────
    if request.POST.get('website'):   # Campo oculto; si viene lleno es bot
        return JsonResponse({'ok': False, 'msg': 'Bot detectado.'}, status=400)

    # ── 2. Rate limiting por IP ───────────────────────────────
    rate_key = f'contact_rate_{ip}'
    sent = cache.get(rate_key, 0)
    if sent >= MAX_CONTACT_PER_HOUR:
        return JsonResponse({
            'ok': False,
            'msg': 'Has enviado demasiados mensajes. Intenta más tarde.'
        }, status=429)

    # ── 3. Sanitización y validación ─────────────────────────
    nombre  = escape(request.POST.get('nombre',  '').strip()[:100])
    correo  = request.POST.get('correo', '').strip()[:254]
    mensaje = escape(request.POST.get('mensaje', '').strip()[:2000])

    if not nombre or not correo or not mensaje:
        return JsonResponse({'ok': False, 'msg': 'Todos los campos son obligatorios.'}, status=400)

    EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
    if not EMAIL_RE.match(correo):
        return JsonResponse({'ok': False, 'msg': 'El correo no tiene un formato válido.'}, status=400)

    if len(mensaje) < 10:
        return JsonResponse({'ok': False, 'msg': 'El mensaje es demasiado corto.'}, status=400)

    # ── 4. Envío de email ─────────────────────────────────────
    try:
        context = {'nombre': nombre, 'email': correo, 'mensaje': mensaje}
        html_msg = render_to_string('emails/contacto.html', context, request=request)
        text_msg = f'De: {nombre} <{correo}>\n\n{mensaje}'

        email = EmailMultiAlternatives(
            subject=f'Nuevo mensaje de contacto web | {nombre}',
            body=text_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],
            reply_to=[correo],  # <-- Esto permite responder directo al cliente desde Gmail
        )
        email.attach_alternative(html_msg, "text/html")
        email.send(fail_silently=False)

        # Incrementa el contador de rate limit (expira en 1 hora)
        cache.set(rate_key, sent + 1, timeout=3600)
        return JsonResponse({'ok': True, 'msg': '¡Mensaje enviado! Te responderé pronto.'})
    except Exception as e:
        print(f"❌ Error SMTP al enviar correo: {e}")
        return JsonResponse({
            'ok': False,
            'msg': f'Error al enviar el mensaje. Intenta más tarde.'
        }, status=500)

# ─── Helper ───────────────────────────────────────────────────
def is_admin(user):
    return user.is_authenticated and user.is_staff

admin_required = user_passes_test(is_admin, login_url='login')

# ─── Dashboard ────────────────────────────────────────────────
@admin_required
def dashboard_index(request):
    return render(request, 'dashboard/index.html', {
        'active_nav': 'index',
        'tiene_acercade': AcercaDe.objects.exists(),
        'num_habilidades': Habilidad.objects.count(),
        'num_experiencias': Experiencia.objects.count(),
        'num_proyectos': Proyecto.objects.count(),
    })

# ── Acerca de ────────────────────────────────────────────────
@admin_required
def dashboard_acercade(request):
    obj = AcercaDe.objects.first()

    if request.method == 'POST':
        # ── Eliminar foto ─────────────────────────────────────
        if request.POST.get('eliminar_foto') == '1' and obj and obj.foto:
            import os
            try:
                if os.path.isfile(obj.foto.path):
                    os.remove(obj.foto.path)
            except: pass
            obj.foto = None
            obj.save()
            messages.success(request, '✓ Foto de perfil eliminada.')
            return redirect('dashboard_acercade')

        form = AcercaDeForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Información de "Sobre mí" actualizada.')
            return redirect('dashboard_acercade')
        else:
            errores = []
            for field, errs in form.errors.items():
                label = form.fields[field].label or field
                errores.append(f'{label}: {errs[0]}')
            msg = 'Error al guardar. ' + ' | '.join(errores)
            if request.FILES.get('foto'):
                msg += ' (vuelve a seleccionar la foto)'
            messages.error(request, msg)
    else:
        form = AcercaDeForm(instance=obj)

    return render(request, 'dashboard/acercade.html', {
        'active_nav': 'acercade', 'form': form, 'object': obj,
    })

# ── Habilidades ──────────────────────────────────────────────
@admin_required
def dashboard_habilidades(request):
    return render(request, 'dashboard/habilidades.html', {
        'active_nav': 'habilidades',
        'habilidades': Habilidad.objects.all().order_by('orden'),
    })

@admin_required
def dashboard_habilidad_form(request, pk=None):
    obj = get_object_or_404(Habilidad, pk=pk) if pk else None
    titulo_form = 'Editar' if obj else 'Nueva'

    if request.method == 'POST':
        form = HabilidadForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'✓ Habilidad {"actualizada" if obj else "creada"} correctamente.')
            return redirect('dashboard_habilidades')
    else:
        form = HabilidadForm(instance=obj)

    return render(request, 'dashboard/habilidad_form.html', {
        'active_nav': 'habilidades', 'form': form, 'titulo_form': titulo_form,
    })

@admin_required
def dashboard_habilidad_eliminar(request, pk):
    obj = get_object_or_404(Habilidad, pk=pk)
    obj.delete()
    messages.success(request, '✓ Habilidad eliminada.')
    return redirect('dashboard_habilidades')

@admin_required
def dashboard_habilidad_ajax(request, pk=None):
    """Crea o edita una habilidad vía AJAX (POST) y retorna JSON."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

    pk = pk or request.POST.get('pk')
    obj = get_object_or_404(Habilidad, pk=pk) if pk else None
    form = HabilidadForm(request.POST, instance=obj)
    
    if form.is_valid():
        obj = form.save()
        from django.urls import reverse
        return JsonResponse({
            'success':     True,
            'accion':      'actualizada' if pk else 'creada',
            'pk':          obj.pk,
            'nombre':      obj.nombre,
            'icono_class': obj.icono_class,
            'orden':       obj.orden,
            'edit_url':    reverse('dashboard_habilidad_editar', args=[obj.pk]),
            'delete_url':  reverse('dashboard_habilidad_eliminar', args=[obj.pk]),
        })
    else:
        # Simplificamos errores
        error = "Datos inválidos."
        if 'nombre' in form.errors: error = "El nombre es obligatorio."
        if 'icono_class' in form.errors: error = "Selecciona un ícono primero."
        return JsonResponse({'success': False, 'error': error})

# ── Experiencias ─────────────────────────────────────────────
@admin_required
def dashboard_experiencias(request):
    return render(request, 'dashboard/experiencias.html', {
        'active_nav': 'experiencias',
        'experiencias': Experiencia.objects.all().order_by('-orden'),
    })

@admin_required
def dashboard_experiencia_form(request, pk=None):
    obj = get_object_or_404(Experiencia, pk=pk) if pk else None
    titulo_form = 'Editar' if obj else 'Nueva'

    if request.method == 'POST':
        form = ExperienciaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'✓ Experiencia {"actualizada" if obj else "creada"}.')
            return redirect('dashboard_experiencias')
    else:
        form = ExperienciaForm(instance=obj)

    return render(request, 'dashboard/experiencia_form.html', {
        'active_nav': 'experiencias', 'form': form, 'titulo_form': titulo_form,
    })

@admin_required
def dashboard_experiencia_eliminar(request, pk):
    obj = get_object_or_404(Experiencia, pk=pk)
    obj.delete()
    messages.success(request, '✓ Experiencia eliminada.')
    return redirect('dashboard_experiencias')

@admin_required
def dashboard_experiencia_ajax(request, pk=None):
    """Crea o edita una experiencia vía AJAX."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)
    
    pk = pk or request.POST.get('pk')
    obj = get_object_or_404(Experiencia, pk=pk) if pk else None
    form = ExperienciaForm(request.POST, instance=obj)
    
    if form.is_valid():
        obj = form.save()
        from django.urls import reverse
        return JsonResponse({
            'success': True,
            'accion': 'actualizada' if pk else 'creada',
            'pk': obj.pk,
            'cargo': obj.cargo,
            'empresa': obj.empresa,
            'periodo': obj.periodo,
            'orden': obj.orden,
            'edit_url':   reverse('dashboard_experiencia_editar', args=[obj.pk]),
            'delete_url': reverse('dashboard_experiencia_eliminar', args=[obj.pk]),
        })
    else:
        return JsonResponse({'success': False, 'error': 'El cargo es obligatorio.'})

# ── Proyectos ─────────────────────────────────────────────────
@admin_required
def dashboard_proyectos(request):
    return render(request, 'dashboard/proyectos.html', {
        'active_nav': 'proyectos',
        'proyectos': Proyecto.objects.all().order_by('orden'),
        'habilidades': Habilidad.objects.all().order_by('nombre'),
    })

@admin_required
def dashboard_proyecto_form(request, pk=None):
    obj = get_object_or_404(Proyecto, pk=pk) if pk else None
    titulo_form = 'Editar' if obj else 'Nuevo'

    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'✓ Proyecto {"actualizado" if obj else "creado"}.')
            return redirect('dashboard_proyectos')
    else:
        form = ProyectoForm(instance=obj)

    return render(request, 'dashboard/proyecto_form.html', {
        'active_nav': 'proyectos', 'form': form, 'titulo_form': titulo_form,
    })

@admin_required
def dashboard_proyecto_eliminar(request, pk):
    obj = get_object_or_404(Proyecto, pk=pk)
    obj.delete()
    messages.success(request, '✓ Proyecto eliminado.')
    return redirect('dashboard_proyectos')

@admin_required
def dashboard_proyecto_ajax(request, pk=None):
    """Crea o edita un proyecto vía AJAX."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

    pk = pk or request.POST.get('pk')
    obj = get_object_or_404(Proyecto, pk=pk) if pk else None
    form = ProyectoForm(request.POST, instance=obj)

    if form.is_valid():
        obj = form.save()
        
        # Procesar tecnologias múltiples desde el JSON enviado
        tecs_json = request.POST.get('tecnologias_json')
        if tecs_json:
            import json
            try:
                tecs_data = json.loads(tecs_json)
                habs_to_add = []
                for t in tecs_data:
                    # Crear la habilidad si no existe
                    hab, created = Habilidad.objects.get_or_create(
                        icono_class=t['class'],
                        defaults={'nombre': t['label']}
                    )
                    habs_to_add.append(hab)
                obj.tecnologias_iconos.set(habs_to_add)
            except Exception as e:
                pass # Fallo silencioso si hay error de JSON

        from django.urls import reverse
        tecs_ids_str = ",".join(str(t.pk) for t in obj.tecnologias_iconos.all())
        tecs_classes_str = ",".join(str(t.icono_class) for t in obj.tecnologias_iconos.all())
        tecs_html = ""
        for t in obj.tecnologias_iconos.all().order_by('nombre'):
            tecs_html += f'<span class="pry-tag"><i class="{t.icono_class}"></i> {t.nombre}</span>'

        return JsonResponse({
            'success': True,
            'accion': 'actualizado' if pk else 'creado',
            'pk': obj.pk,
            'titulo': obj.titulo,
            'descripcion': obj.descripcion,
            'icono_class': obj.icono_class,
            'tecnologias_ids': tecs_ids_str,
            'tecnologias_classes': tecs_classes_str,
            'tecnologias_iconos_html': tecs_html,
            'link_github': obj.link_github,
            'link_despliegue': obj.link_despliegue,
            'orden': obj.orden,
            'edit_url':   reverse('dashboard_proyecto_editar', args=[obj.pk]),
            'delete_url': reverse('dashboard_proyecto_eliminar', args=[obj.pk]),
        })
    else:
        return JsonResponse({'success': False, 'error': 'El título es obligatorio.'})

# ─── Reordenar (SortableJS) ───────────────────────────────────
@admin_required
def dashboard_reordenar(request):
    """Recibe JSON con {modelo, ordenes} y actualiza el campo `orden`."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido.'}, status=400)

    modelo  = data.get('modelo')
    ordenes = data.get('ordenes', [])

    models_map = {
        'habilidad':   Habilidad,
        'experiencia': Experiencia,
        'proyecto':    Proyecto,
    }

    ModelClass = models_map.get(modelo)
    if not ModelClass:
        return JsonResponse({'success': False, 'error': 'Modelo no válido.'}, status=400)

    for idx, pk in enumerate(ordenes):
        if modelo == 'experiencia':
            # Experiencia ordena descendente: primero visual = orden más alto
            ModelClass.objects.filter(pk=pk).update(orden=len(ordenes) - 1 - idx)
        else:
            ModelClass.objects.filter(pk=pk).update(orden=idx)

    return JsonResponse({'success': True})

# ─── Ordenar Alfabéticamente ───────────────────────────────────
@admin_required
def dashboard_ordenar_alfabeticamente(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido.'}, status=400)

    modelo = data.get('modelo')
    
    models_map = {
        'habilidad': (Habilidad, 'nombre'),
        'experiencia': (Experiencia, 'empresa'),
        'proyecto': (Proyecto, 'titulo'),
    }

    if modelo not in models_map:
        return JsonResponse({'success': False, 'error': 'Modelo no válido.'}, status=400)
        
    ModelClass, sort_field = models_map[modelo]
    items = ModelClass.objects.all().order_by(sort_field)
    
    for idx, item in enumerate(items):
        if modelo == 'experiencia':
            item.orden = len(items) - 1 - idx
        else:
            item.orden = idx
        item.save()
        
    return JsonResponse({'success': True})

# ─── Reset por defecto ────────────────────────────────────────
@admin_required
def dashboard_reset_acercade(request):
    AcercaDe.objects.all().delete()
    messages.success(request, '✓ Sección "Sobre mí" restaurada a los valores por defecto.')
    return redirect('dashboard_acercade')

@admin_required
def dashboard_reset_habilidades(request):
    Habilidad.objects.all().delete()
    messages.success(request, '✓ Habilidades restauradas a los valores por defecto.')
    return redirect('dashboard_habilidades')

@admin_required
def dashboard_reset_experiencias(request):
    Experiencia.objects.all().delete()
    messages.success(request, '✓ Experiencias restauradas a los valores por defecto.')
    return redirect('dashboard_experiencias')

@admin_required
def dashboard_reset_proyectos(request):
    Proyecto.objects.all().delete()
    messages.success(request, '✓ Proyectos restaurados a los valores por defecto.')
    return redirect('dashboard_proyectos')

@admin_required
def dashboard_reset_redes(request):
    RedSocial.objects.all().delete()
    messages.success(request, '✓ Redes sociales restauradas a los valores por defecto.')
    return redirect('dashboard_redes_list')

# ─── Personalización ──────────────────────────────────────────
@admin_required
def dashboard_personalizacion(request):
    config = Personalizacion.objects.first()
    if not config:
        config = Personalizacion.objects.create()

    if request.method == 'POST':
        # Reset color request
        if request.POST.get('reset') == '1':
            config.color_botones = '#00d4ff'
            config.color_titulos = '#ffffff'
            config.color_logo    = '#ffffff'
            config.color_fondo   = '#0a0a0a'
            config.color_cartas  = '#121212'
            config.color_navbar  = '#121212'
            config.color_footer  = '#121212'
            config.color_seccion_sobremi     = '#0a0a0a'
            config.color_seccion_experiencia = '#0a0a0a'
            config.color_seccion_proyectos   = '#0a0a0a'
            config.color_seccion_contacto    = '#0a0a0a'
            config.save()
            messages.success(request, '✓ Colores restaurados a los valores por defecto.')
            return redirect('dashboard_personalizacion')

        form = PersonalizacionForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Personalización de colores guardada correctamente.')
            return redirect('dashboard_personalizacion')
        else:
            messages.error(request, 'Error al guardar. Revisa los valores hexadecimales.')

    else:
        form = PersonalizacionForm(instance=config)

    return render(request, 'dashboard/personalizacion.html', {
        'active_nav': 'personalizacion',
        'config': config,
        'form': form
    })

# ─── Redes Sociales ──────────────────────────────────────────

@admin_required
def dashboard_redes_list(request):
    redes = RedSocial.objects.all().order_by('orden', 'nombre')
    return render(request, 'dashboard/redes_sociales.html', {
        'redes': redes,
        'active_nav': 'redes'
    })

@admin_required
def dashboard_redes_create(request):
    if request.method == 'POST':
        form = RedSocialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Red social añadida correctamente.')
        else:
            messages.error(request, 'Error al añadir. Revisa los datos.')
    return redirect('dashboard_redes_list')

@admin_required
def dashboard_redes_edit(request, pk):
    red = get_object_or_404(RedSocial, pk=pk)
    if request.method == 'POST':
        form = RedSocialForm(request.POST, instance=red)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Red social actualizada correctamente.')
    return redirect('dashboard_redes_list')

@admin_required
def dashboard_redes_delete(request, pk):
    red = get_object_or_404(RedSocial, pk=pk)
    red.delete()
    messages.success(request, '✓ Red social eliminada correctamente.')
    return redirect('dashboard_redes_list')

@admin_required
def dashboard_redes_save_ajax(request):
    """Crea o edita una red social vía AJAX."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    pk = request.POST.get('pk')
    obj = get_object_or_404(RedSocial, pk=pk) if pk else None
    form = RedSocialForm(request.POST, instance=obj)
    
    if form.is_valid():
        obj = form.save()
        return JsonResponse({
            'success': True,
            'pk': obj.pk,
            'nombre': obj.nombre,
            'url': obj.url,
            'icono': obj.icono,
            'orden': obj.orden,
            'accion': "actualizada" if pk else "añadida"
        })
    else:
        return JsonResponse({'success': False, 'error': 'Revisa los datos del formulario.'})
