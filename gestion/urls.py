# gestion/urls.py

from django.urls import path
from . import views # Importa todas las funciones de tu archivo views.py

urlpatterns = [
    # Ruta: http://127.0.0.1:8000/
    # Llama a la función listar_estudiantes en views.py
    path('', views.listar_estudiantes, name='listar_estudiantes'), 
    
    # Ruta: http://127.0.0.1:8000/agregar/
    # Llama a la función agregar_estudiante en views.py
    path('agregar/', views.agregar_estudiante, name='agregar_estudiante'),
    path('nota/ingresar/', views.ingresar_nota, name='ingresar_nota'),
    path('', views.listar_estudiantes, name='listar_estudiantes'), 
    path('agregar/', views.agregar_estudiante, name='agregar_estudiante'),
    
    # Rutas para acciones específicas por código de estudiante
    path('editar/<str:codigo>/', views.editar_estudiante, name='editar_estudiante'),
    path('eliminar/<str:codigo>/', views.eliminar_estudiante, name='eliminar_estudiante'),
    
    path('nota/ingresar/', views.ingresar_nota, name='ingresar_nota'),
    
    # Agrega aquí otras rutas como /editar/<id>/, /eliminar/<id>/, /nota/ingresar/, etc.
]