# gestion/admin.py

from django.contrib import admin
from .models import Estudiante, Materia, Corte, NotaIndividual, NotaFinal

# Permite ingresar Cortes directamente en la página de Materia
class CorteInline(admin.TabularInline):
    model = Corte
    extra = 1  # Cuántos formularios vacíos mostrar

# Clase para mostrar la lista de cortes al editar una materia
class MateriaAdmin(admin.ModelAdmin):
    inlines = [CorteInline]
    list_display = ('nombre', 'creditos')

# Registra todos los modelos
admin.site.register(Estudiante)
admin.site.register(Materia, MateriaAdmin) # Usamos la clase personalizada para Cortes
admin.site.register(Corte)
admin.site.register(NotaIndividual)
admin.site.register(NotaFinal)