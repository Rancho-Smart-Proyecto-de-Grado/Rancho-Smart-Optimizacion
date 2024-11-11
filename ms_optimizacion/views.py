from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Vaca
from django.views.decorators.csrf import csrf_exempt
import json

def calcular_puntaje(vaca, criterio, genero_objetivo, raza):
    PRIORIDAD_RAZA = {
        "Holstein": {"leche": 20, "carne": 5, "mixto": 10},
        "Jersey": {"leche": 15, "carne": 5, "mixto": 10},
        "Angus": {"leche": 5, "carne": 20, "mixto": 10},
        "Hereford": {"leche": 5, "carne": 15, "mixto": 10},
        "Simmental": {"leche": 10, "carne": 10, "mixto": 15}
    }

    # Rechazar vacas con el mismo género que la vaca objetivo
    if vaca['genero'] == genero_objetivo:
        return 0  # Penalización total si el género coincide

    # Asignación de ponderaciones para cada criterio
    PONDERACIONES = {
        "salud": 30,
        "fertilidad": 20,
        "criterio_base": 30,
        "raza": 20
    }
    
    puntaje_total = 0

    # Evaluar salud y fertilidad
    puntaje_salud_fertilidad = 0
    if not vaca['enfermedad'] and not vaca['problemas_reproductivos']:
        puntaje_salud_fertilidad += PONDERACIONES["salud"]

    # Puntaje base en función del criterio solicitado
    puntaje_base = 0
    if criterio == 'carne':
        puntaje_base = vaca['peso']
    elif criterio == 'leche':
        puntaje_base = vaca['produccion_leche_anual']
    elif criterio == 'mixto':
        puntaje_base = 0.5 * vaca['peso'] + 0.5 * vaca['produccion_leche_anual']
    puntaje_base *= PONDERACIONES["criterio_base"] / 100

    # Evaluar raza
    puntaje_raza = PRIORIDAD_RAZA.get(vaca['raza'], {}).get(criterio, 0)
    puntaje_raza *= PONDERACIONES["raza"] / 100

    # Sumar todos los puntajes ponderados
    puntaje_total = puntaje_salud_fertilidad + puntaje_base + puntaje_raza

    return puntaje_total

@csrf_exempt
def optimizar_cruce(request):
    if request.method == "POST":
        data = json.loads(request.body)
        vaca_a_reproducir_data = data['vaca_a_reproducir']
        vacas_disponibles_data = data['vacas_disponibles']
        criterio = data['criterio']

        # Buscar o crear la vaca a reproducir en la base de datos
        vaca_a_reproducir, created = Vaca.objects.get_or_create(
            id=vaca_a_reproducir_data['id'],
            defaults=vaca_a_reproducir_data
        )

        # Cargar vacas disponibles, creándolas si no existen
        vacas_disponibles = []
        for vaca_data in vacas_disponibles_data:
            vaca, created = Vaca.objects.get_or_create(id=vaca_data['id'], defaults=vaca_data)
            vacas_disponibles.append(vaca)
            
        # Optimizar el cruce
        genero_objetivo = 'macho' if vaca_a_reproducir.genero == 'macho' else 'hembra'
        raza = vaca_a_reproducir.raza
        puntaje_max = 0
        mejor_vaca = None

        for vaca in vacas_disponibles:
            print(vaca.id)
            print(vaca_a_reproducir.familiares)
            
            # Excluir familiares
            if vaca.id in vaca_a_reproducir.familiares:
                continue

            # Calcular puntaje solo si el género es el opuesto al de la vaca a reproducir
            puntaje = calcular_puntaje(vaca.__dict__, criterio, genero_objetivo, raza)
            if puntaje > puntaje_max:
                mejor_vaca = vaca
                puntaje_max = puntaje

        return JsonResponse({
            "vaca_a_reproducir": vaca_a_reproducir.id,
            "mejor_cruce": mejor_vaca.id if mejor_vaca else None,
            "puntaje": puntaje_max
        })