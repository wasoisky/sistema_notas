# gestion/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages # Para mostrar mensajes de éxito/error
from django.db.models import Prefetch # Para optimizar consultas
from .forms import EstudianteForm, NotaIndividualForm 
from .models import Estudiante, Materia, Corte, NotaIndividual, NotaFinal 


# --- Función Auxiliar: CÁLCULO DE NOTA FINAL ---
def calcular_nota_final(estudiante_id, materia_id):
    """
    Calcula la nota final ponderada de un estudiante en una materia
    y actualiza/crea el registro en la tabla NotaFinal.
    """
    try:
        estudiante = Estudiante.objects.get(pk=estudiante_id)
        materia = Materia.objects.get(pk=materia_id)
    except (Estudiante.DoesNotExist, Materia.DoesNotExist):
        return
        
    notas_individuales = NotaIndividual.objects.filter(
        estudiante=estudiante,
        materia=materia
    ).select_related('corte') # Optimiza trayendo la info del Corte (porcentaje)

    nota_final_calculada = 0.0
    
    # Suma de ponderaciones
    for nota_reg in notas_individuales:
        porcentaje_decimal = nota_reg.corte.porcentaje / 100
        ponderacion = float(nota_reg.nota_valor) * float(porcentaje_decimal)
        nota_final_calculada += ponderacion

    # Actualizar o crear el registro final
    NotaFinal.objects.update_or_create(
        estudiante=estudiante,
        materia=materia,
        defaults={'nota_final': round(nota_final_calculada, 2)}
    )


# --- 1. VISTA PARA LISTAR ESTUDIANTES (con filtros y ordenamiento) ---
def listar_estudiantes(request):
    """Muestra la lista de todos los estudiantes con filtros de sexo y ordenamiento."""
    
    # --- 1. CONFIGURACIÓN BASE DE LA CONSULTA ---
    # Usamos Prefetch para traer las notas finales de cada estudiante de manera eficiente
    estudiantes_query = Estudiante.objects.all().order_by('apellido').prefetch_related(
        Prefetch(
            'notafinal_set', 
            queryset=NotaFinal.objects.all(), 
            to_attr='notas_calculadas'
        )
    )

    # --- 2. APLICAR FILTROS DE SEXO ---
    filtro_sexo = request.GET.get('sexo')
    if filtro_sexo in ['M', 'F']:
        estudiantes_query = estudiantes_query.filter(sexo=filtro_sexo)

    # --- 3. PREPARAR DATOS PARA EL ORDENAMIENTO DE NOTAS ---
    # Convertimos el QuerySet a una lista de diccionarios para poder ordenar por Nota Final
    lista_estudiantes = []
    for est in estudiantes_query:
        # Recuperar la nota final. Si no hay nota, se asigna 0.0
        nota_final = est.notas_calculadas[0].nota_final if est.notas_calculadas else 0.0
        
        lista_estudiantes.append({
            'codigo': est.codigo,
            'nombre': est.nombre,
            'apellido': est.apellido,
            'sexo': est.sexo,
            'nota_final': nota_final,
            'objeto': est 
        })

    # --- 4. APLICAR ORDENAMIENTO POR NOTA FINAL ---
    orden = request.GET.get('orden')
    if orden == 'mayor':
        # Ordena descendente (Mayor a Menor)
        lista_estudiantes.sort(key=lambda x: x['nota_final'], reverse=True)
    elif orden == 'menor':
        # Ordena ascendente (Menor a Mayor)
        lista_estudiantes.sort(key=lambda x: x['nota_final'])

    context = {
        'estudiantes': lista_estudiantes, # Se pasa la lista de diccionarios
        'filtro_activo': filtro_sexo,
        'orden_activo': orden,
    }
    
    return render(request, 'gestion/lista_estudiantes.html', context)


# --- 2. VISTA PARA AGREGAR ESTUDIANTES ---
def agregar_estudiante(request):
    """Muestra el formulario para agregar un nuevo estudiante y maneja la inserción."""
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"El estudiante {form.cleaned_data['nombre']} ha sido agregado correctamente.")
            return redirect('listar_estudiantes') 
    else:
        form = EstudianteForm()
        
    return render(request, 'gestion/agregar_estudiante.html', {'form': form})


# --- 3. VISTA PARA EDITAR ESTUDIANTES (CRUD COMPLETO) ---
def editar_estudiante(request, codigo):
    """Carga y procesa el formulario para editar un estudiante existente."""
    estudiante = get_object_or_404(Estudiante, codigo=codigo) # Obtiene el estudiante por código

    if request.method == 'POST':
        # Rellena con datos enviados y con el estudiante existente
        form = EstudianteForm(request.POST, instance=estudiante) 
        if form.is_valid():
            form.save() # Guarda los cambios
            messages.success(request, f"Estudiante {estudiante.nombre} {estudiante.apellido} actualizado correctamente.")
            return redirect('listar_estudiantes')
    else:
        # Rellena el formulario con los datos actuales del estudiante
        form = EstudianteForm(instance=estudiante) 
    
    context = {
        'form': form,
        'estudiante': estudiante,
    }
    # Asegúrate de crear la plantilla 'editar_estudiante.html'
    return render(request, 'gestion/editar_estudiante.html', context)


# --- 4. VISTA PARA ELIMINAR ESTUDIANTES ---
def eliminar_estudiante(request, codigo):
    """Elimina un estudiante y sus registros relacionados."""
    estudiante = get_object_or_404(Estudiante, codigo=codigo)
    
    # Solo se permite POST para eliminar (seguridad)
    if request.method == 'POST':
        nombre_completo = f"{estudiante.nombre} {estudiante.apellido}"
        estudiante.delete()
        messages.warning(request, f"El estudiante {nombre_completo} ha sido eliminado permanentemente.")
        return redirect('listar_estudiantes')

    # Si se accede por GET, se muestra una página de confirmación (puedes omitir esto si solo quieres eliminar directo)
    return render(request, 'gestion/confirmar_eliminacion.html', {'estudiante': estudiante})


# --- 5. VISTA PARA INGRESAR NOTAS INDIVIDUALES ---
def ingresar_nota(request):
    """Maneja el formulario de ingreso de notas y dispara el cálculo."""
    if request.method == 'POST':
        form = NotaIndividualForm(request.POST)
        if form.is_valid():
            nota_individual = form.save()
            
            # DISPARADOR: Ejecuta la función de cálculo
            calcular_nota_final(nota_individual.estudiante.id, nota_individual.materia.id)
            
            messages.success(request, "La nota y el promedio final han sido actualizados.")
            return redirect('listar_estudiantes') 
    else:
        form = NotaIndividualForm()
        
    return render(request, 'gestion/ingresar_nota.html', {'form': form})