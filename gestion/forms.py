# gestion/forms.py

from django import forms
from .models import Estudiante, Materia, Corte, NotaIndividual, NotaFinal

# Formulario básico para el modelo Estudiante
class EstudianteForm(forms.ModelForm):
    """Formulario para agregar y editar estudiantes."""
    class Meta:
        model = Estudiante
        # Incluye todos los campos necesarios para crear un estudiante
        fields = ['codigo', 'nombre', 'apellido', 'sexo']
        
        # Puedes personalizar los labels si quieres
        labels = {
            'codigo': 'Código Estudiantil',
            'nombre': 'Nombre(s)',
            'apellido': 'Apellido(s)',
            'sexo': 'Sexo',
        }
        
class NotaIndividualForm(forms.ModelForm):
    """Formulario para registrar una sola nota y su corte."""
    class Meta:
        model = NotaIndividual
        # Solo necesitamos los FK y el valor de la nota
        fields = ['estudiante', 'materia', 'corte', 'nota_valor'] 
        
        widgets = {
            # Esto ayuda a validar que la nota sea un decimal entre 0.00 y 5.00
            'nota_valor': forms.NumberInput(attrs={'step': 0.01, 'min': 0.00, 'max': 5.00})
        }