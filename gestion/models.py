# gestion/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# --- 1. Estudiante ---
class Estudiante(models.Model):
    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )
    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código Estudiantil")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)

    def __str__(self):
        return f"{self.codigo} - {self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        db_table = 'estudiante' # Nombre de la tabla en Supabase

# --- 2. Materia ---
class Materia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    creditos = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        db_table = 'materia'

# --- 3. Corte (Definición de Porcentajes) ---
class Corte(models.Model):
    """Define los cortes (ej: Corte 1, Corte 2) y su peso ponderado."""
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, verbose_name="Materia")
    numero_corte = models.IntegerField(
        verbose_name="Número del Corte (1, 2, 3)",
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name="Porcentaje de peso en la nota final (0.01 a 100.00)",
        validators=[MinValueValidator(0.01), MaxValueValidator(100.00)]
    )

    def __str__(self):
        return f"{self.materia.nombre} - Corte {self.numero_corte} ({self.porcentaje}%)"

    class Meta:
        verbose_name = "Corte de Evaluación"
        verbose_name_plural = "Cortes de Evaluación"
        # Asegura que no haya dos cortes con el mismo número para la misma materia
        unique_together = (('materia', 'numero_corte'),)
        db_table = 'corte'

# --- 4. Nota Individual (Registro de la Calificación) ---
class NotaIndividual(models.Model):
    """Registro de una nota específica dentro de un corte."""
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    corte = models.ForeignKey(Corte, on_delete=models.CASCADE)
    nota_valor = models.DecimalField(
        max_digits=3, decimal_places=2,
        verbose_name="Valor de la Nota (0.00 a 5.00)",
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)]
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.estudiante.nombre} - {self.materia.nombre} ({self.nota_valor})"

    class Meta:
        verbose_name = "Nota Individual"
        verbose_name_plural = "Notas Individuales"
        db_table = 'nota_individual'

# --- 5. Nota Final (Resultado Ponderado) ---
class NotaFinal(models.Model):
    """Resultado final de la materia, calculado con todos los cortes."""
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    nota_final = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.estudiante.nombre} - {self.materia.nombre}: {self.nota_final}"

    class Meta:
        verbose_name = "Nota Final"
        verbose_name_plural = "Notas Finales"
        # Asegura que solo haya una nota final por estudiante y materia
        unique_together = (('estudiante', 'materia'),)
        db_table = 'nota_final'