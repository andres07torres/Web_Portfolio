from django.db import models
from ckeditor.fields import RichTextField

class AcercaDe(models.Model):
    titulo = models.CharField(max_length=100, default="Sobre mí", blank=True)
    subtitulo = models.CharField(max_length=200, blank=True, help_text="Ej: Soy un Desarrollador Frontend y Backend...")
    descripcion = models.TextField(blank=True)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    
    @property
    def foto_url_valida(self):
        if self.foto:
            try:
                if self.foto.storage.exists(self.foto.name):
                    return self.foto.url
            except Exception:
                pass
        return None
    
    class Meta:
        verbose_name = "Acerca de mí"
        verbose_name_plural = "Acerca de mí"

    def __str__(self):
        return self.titulo

class Habilidad(models.Model):
    nombre = models.CharField(max_length=50)
    icono_class = models.CharField(max_length=100, help_text="Clase de Bootstrap Icon. Ej: bi-filetype-py")
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Habilidad"
        verbose_name_plural = "Habilidades"
        ordering = ['orden']

    def __str__(self):
        return self.nombre

class Experiencia(models.Model):
    cargo = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100)
    periodo = models.CharField(max_length=100, help_text="Ej: Ene 2025 - Presente")
    descripcion = RichTextField(help_text="Lista de logros y responsabilidades")
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Experiencia"
        verbose_name_plural = "Experiencias"
        ordering = ['-orden']

    def __str__(self):
        return f"{self.cargo} - {self.empresa}"

class Proyecto(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    icono_class = models.CharField(max_length=100, help_text="Icono representativo. Ej: bi-translate")
    link_github = models.URLField(blank=True, null=True)
    link_despliegue = models.URLField(blank=True, null=True, help_text="Link del proyecto desplegado (Render, Vercel, etc)")
    tecnologias = models.CharField(max_length=200, help_text="Lista separada por puntos o comas. Ej: AI • Python • Django")
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['orden']

    def __str__(self):
        return self.titulo

class Personalizacion(models.Model):
    # Colores principales (Hex)
    color_botones      = models.CharField(max_length=7, default='#00d4ff')
    color_titulos      = models.CharField(max_length=7, default='#ffffff')
    color_logo         = models.CharField(max_length=7, default='#ffffff')
    color_fondo        = models.CharField(max_length=7, default='#0a0a0a')
    color_cartas       = models.CharField(max_length=7, default='#121212')
    color_navbar       = models.CharField(max_length=7, default='#121212')
    color_footer       = models.CharField(max_length=7, default='#121212')
    
    # Colores por sección
    color_seccion_sobremi     = models.CharField(max_length=7, default='#0a0a0a')
    color_seccion_experiencia = models.CharField(max_length=7, default='#0a0a0a')
    color_seccion_proyectos   = models.CharField(max_length=7, default='#0a0a0a')
    color_seccion_contacto    = models.CharField(max_length=7, default='#0a0a0a')
    
    # Metadatos
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Personalización"
        verbose_name_plural = "Personalización"

    def __str__(self):
        return "Configuración de Colores"

class RedSocial(models.Model):
    nombre = models.CharField(max_length=50)
    url    = models.URLField()
    icono  = models.CharField(max_length=50, help_text="Clase de Bootstrap Icon (ej: bi-facebook)")
    orden  = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Red Social"
        verbose_name_plural = "Redes Sociales"
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre
