from django import forms
from .models import AcercaDe, Habilidad, Experiencia, Proyecto, Personalizacion, RedSocial

class AcercaDeForm(forms.ModelForm):
    class Meta:
        model = AcercaDe
        fields = ['titulo', 'subtitulo', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class HabilidadForm(forms.ModelForm):
    class Meta:
        model = Habilidad
        fields = ['nombre', 'icono_class', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'icono_class': forms.TextInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ExperienciaForm(forms.ModelForm):
    class Meta:
        model = Experiencia
        fields = ['cargo', 'empresa', 'periodo', 'descripcion', 'orden']
        widgets = {
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'periodo': forms.TextInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'icono_class', 'link_github', 'link_despliegue', 'tecnologias', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icono_class': forms.TextInput(attrs={'class': 'form-control'}),
            'link_github': forms.URLInput(attrs={'class': 'form-control'}),
            'link_despliegue': forms.URLInput(attrs={'class': 'form-control'}),
            'tecnologias': forms.TextInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class RedSocialForm(forms.ModelForm):
    class Meta:
        model = RedSocial
        fields = ['nombre', 'url', 'icono', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'icono': forms.TextInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PersonalizacionForm(forms.ModelForm):
    class Meta:
        model = Personalizacion
        fields = [
            'color_botones', 'color_titulos', 'color_logo', 'color_fondo', 
            'color_cartas', 'color_navbar', 'color_footer',
            'color_seccion_sobremi', 'color_seccion_experiencia', 
            'color_seccion_proyectos', 'color_seccion_contacto'
        ]
        widgets = {
            'color_botones': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_titulos': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_logo': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_fondo': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_cartas': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_navbar': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_footer': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_seccion_sobremi': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_seccion_experiencia': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_seccion_proyectos': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'color_seccion_contacto': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }
