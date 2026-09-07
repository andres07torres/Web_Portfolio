from django.contrib import admin
from .models import AcercaDe, Habilidad, Experiencia, Proyecto

@admin.register(AcercaDe)
class AcercaDeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'subtitulo')

@admin.register(Habilidad)
class HabilidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'icono_class', 'orden')
    list_editable = ('orden',)

@admin.register(Experiencia)
class ExperienciaAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'empresa', 'periodo', 'orden')
    list_editable = ('orden',)

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'orden')
    list_editable = ('orden',)
    filter_horizontal = ('tecnologias_iconos',)
