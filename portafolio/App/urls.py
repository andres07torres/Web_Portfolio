from django.urls import path
from . import views

urlpatterns = [
    # Portafolio público
    path('', views.base, name='base'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('contacto/', views.contacto, name='contacto'),

    # Dashboard personalizado
    path('dashboard/', views.dashboard_index, name='dashboard_index'),

    # Sobre mí
    path('dashboard/acerca-de/', views.dashboard_acercade, name='dashboard_acercade'),

    # Habilidades
    path('dashboard/habilidades/', views.dashboard_habilidades, name='dashboard_habilidades'),
    path('dashboard/habilidades/nueva/', views.dashboard_habilidad_form, name='dashboard_habilidad_nueva'),
    path('dashboard/habilidades/nueva/ajax/', views.dashboard_habilidad_ajax, name='dashboard_habilidad_nueva_ajax'),
    path('dashboard/habilidades/<int:pk>/editar/', views.dashboard_habilidad_form, name='dashboard_habilidad_editar'),
    path('dashboard/habilidades/<int:pk>/eliminar/', views.dashboard_habilidad_eliminar, name='dashboard_habilidad_eliminar'),

    # Experiencias
    path('dashboard/experiencias/', views.dashboard_experiencias, name='dashboard_experiencias'),
    path('dashboard/experiencias/nueva/', views.dashboard_experiencia_form, name='dashboard_experiencia_nueva'),
    path('dashboard/experiencias/nueva/ajax/', views.dashboard_experiencia_ajax, name='dashboard_experiencia_nueva_ajax'),
    path('dashboard/experiencias/<int:pk>/editar/', views.dashboard_experiencia_form, name='dashboard_experiencia_editar'),
    path('dashboard/experiencias/<int:pk>/eliminar/', views.dashboard_experiencia_eliminar, name='dashboard_experiencia_eliminar'),

    # Proyectos
    path('dashboard/proyectos/', views.dashboard_proyectos, name='dashboard_proyectos'),
    path('dashboard/proyectos/nuevo/', views.dashboard_proyecto_form, name='dashboard_proyecto_nuevo'),
    path('dashboard/proyectos/nuevo/ajax/', views.dashboard_proyecto_ajax, name='dashboard_proyecto_nueva_ajax'),
    path('dashboard/proyectos/<int:pk>/editar/', views.dashboard_proyecto_form, name='dashboard_proyecto_editar'),
    path('dashboard/proyectos/<int:pk>/eliminar/', views.dashboard_proyecto_eliminar, name='dashboard_proyecto_eliminar'),

    # Reordenar (SortableJS)
    path('dashboard/reordenar/', views.dashboard_reordenar, name='dashboard_reordenar'),

    # Reset por defecto
    path('dashboard/acerca-de/reset/', views.dashboard_reset_acercade, name='dashboard_reset_acercade'),
    path('dashboard/habilidades/reset/', views.dashboard_reset_habilidades, name='dashboard_reset_habilidades'),
    path('dashboard/experiencias/reset/', views.dashboard_reset_experiencias, name='dashboard_reset_experiencias'),
    path('dashboard/proyectos/reset/', views.dashboard_reset_proyectos, name='dashboard_reset_proyectos'),
    path('dashboard/redes/reset/', views.dashboard_reset_redes, name='dashboard_reset_redes'),
    
    # Personalización
    path('dashboard/personalizacion/', views.dashboard_personalizacion, name='dashboard_personalizacion'),
    path('dashboard/redes/', views.dashboard_redes_list, name='dashboard_redes_list'),
    path('dashboard/redes/save/ajax/', views.dashboard_redes_save_ajax, name='dashboard_redes_save_ajax'),
    path('dashboard/redes/add/', views.dashboard_redes_create, name='dashboard_redes_create'),
    path('dashboard/redes/edit/<int:pk>/', views.dashboard_redes_edit, name='dashboard_redes_edit'),
    path('dashboard/redes/delete/<int:pk>/', views.dashboard_redes_delete, name='dashboard_redes_delete'),
]
