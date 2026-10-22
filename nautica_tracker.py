#!/usr/bin/env python3
"""Checklist y diario de la Hoja de Ruta Náutica 2026-2027.

Compatible con Python 3.8+. El progreso se guarda en nautica_progress.json,
en la misma carpeta que este script.
"""

import json
import os
from typing import Any, Dict, List, Optional


ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nautica_progress.json")
ANCHO_BARRA = 10


def crear_plantilla() -> List[Dict[str, Any]]:
    """Crea las seis fases y sus hitos con estado pendiente y notas vacías."""
    return [
        {
            "fase": "FASE 1: Diciembre 2026 - PER + Habilitación a Vela",
            "hitos": [
                {"id": "fase1_examen_per", "descripcion": "Aprobar el examen PER", "completado": False, "fecha_objetivo": "Diciembre 2026", "notas": ""},
                {"id": "fase1_habilitacion_vela", "descripcion": "Completar la habilitación a Vela", "completado": False, "fecha_objetivo": "Diciembre 2026", "notas": ""},
                {"id": "fase1_psicotecnico_per", "descripcion": "Psicotécnico Náutico en Centro de Reconocimiento (para expedición PER/PY/CY)", "completado": False, "fecha_objetivo": "Diciembre 2026", "notas": ""},
            ],
        },
        {
            "fase": "FASE 2: Enero/Febrero 2027 - Requisitos RYA Commercial",
            "hitos": [
                {"id": "fase2_stcw", "descripcion": "Completar formación STCW", "completado": False, "fecha_objetivo": "Enero/Febrero 2027", "notas": ""},
                {"id": "fase2_medico_ism_eng1", "descripcion": "Reconocimiento Médico Marítimo ISM o ENG1 (para RYA Commercial Endorsement y Libreta Marítima)", "completado": False, "fecha_objetivo": "Enero/Febrero 2027", "notas": ""},
                {"id": "fase2_radio_src", "descripcion": "Obtener la radio RYA SRC", "completado": False, "fecha_objetivo": "Enero/Febrero 2027", "notas": ""},
                {"id": "fase2_millas_logbook", "descripcion": "Registrar 100 millas en el logbook", "completado": False, "fecha_objetivo": "Enero/Febrero 2027", "notas": ""},
            ],
        },
        {
            "fase": "FASE 3: Marzo 2027 - Patrón de Yate (PY) + Curso RYA PPR Online",
            "hitos": [
                {"id": "fase3_patron_yate", "descripcion": "Obtener el título de Patrón de Yate (PY)", "completado": False, "fecha_objetivo": "Marzo 2027", "notas": ""},
                {"id": "fase3_rya_ppr", "descripcion": "Completar el curso RYA PPR Online", "completado": False, "fecha_objetivo": "Marzo 2027", "notas": ""},
            ],
        },
        {
            "fase": "FASE 4: Abril/Mayo 2027 - RYA Day Skipper Practical + Commercial Endorsement",
            "hitos": [
                {"id": "fase4_day_skipper_sail", "descripcion": "Completar RYA Day Skipper Practical (SAIL)", "completado": False, "fecha_objetivo": "Abril/Mayo 2027", "notas": ""},
                {"id": "fase4_day_skipper_motor", "descripcion": "Completar RYA Day Skipper Practical (MOTOR)", "completado": False, "fecha_objetivo": "Abril/Mayo 2027", "notas": ""},
                {"id": "fase4_envio_endorsement", "descripcion": "Enviar la solicitud de Commercial Endorsement", "completado": False, "fecha_objetivo": "Abril/Mayo 2027", "notas": ""},
            ],
        },
        {
            "fase": "FASE 5: Mayo 2027 - Commercial Endorsement e Inicio Laboral",
            "hitos": [
                {"id": "fase5_endorsement_sail", "descripcion": "Recibir Commercial Endorsement (Sail)", "completado": False, "fecha_objetivo": "Mayo 2027", "notas": ""},
                {"id": "fase5_endorsement_motor", "descripcion": "Recibir Commercial Endorsement (Motor)", "completado": False, "fecha_objetivo": "Mayo 2027", "notas": ""},
                {"id": "fase5_inicio_laboral", "descripcion": "Iniciar la actividad laboral como Patrón Profesional", "completado": False, "fecha_objetivo": "Mayo 2027", "notas": ""},
            ],
        },
        {
            "fase": "FASE 6: Junio/Julio 2027 - Capitán de Yate (CY)",
            "hitos": [
                {"id": "fase6_capitan_yate", "descripcion": "Obtener el título de Capitán de Yate (CY)", "completado": False, "fecha_objetivo": "Junio/Julio 2027", "notas": ""},
            ],
        },
    ]


def guardar_datos(fases: List[Dict[str, Any]]) -> None:
    """Guarda el estado en JSON y reemplaza el archivo de forma segura."""
    archivo_temporal = ARCHIVO_DATOS + ".tmp"
    with open(archivo_temporal, "w", encoding="utf-8") as archivo:
        json.dump(fases, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")
    os.replace(archivo_temporal, ARCHIVO_DATOS)


def cargar_datos() -> List[Dict[str, Any]]:
    """Carga el progreso existente o crea el archivo desde la plantilla."""
    if not os.path.exists(ARCHIVO_DATOS):
        fases = crear_plantilla()
        guardar_datos(fases)
        return fases

    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        if not isinstance(datos, list):
            raise ValueError("el JSON no contiene una lista de fases")

        # Reconstruye la plantilla para incorporar hitos nuevos sin perder
        # el estado o las notas que ya estén guardados con el mismo ID.
        hitos_guardados = {}
        for fase in datos:
            if isinstance(fase, dict) and isinstance(fase.get("hitos"), list):
                for hito in fase["hitos"]:
                    if isinstance(hito, dict) and isinstance(hito.get("id"), str):
                        hitos_guardados[hito["id"]] = hito

        fases = crear_plantilla()
        for fase in fases:
            for hito in fase["hitos"]:
                guardado = hitos_guardados.get(hito["id"], {})
                hito["completado"] = bool(guardado.get("completado", False))
                hito["notas"] = str(guardado.get("notas", ""))
                hito["fecha_objetivo"] = str(guardado.get("fecha_objetivo", hito["fecha_objetivo"]))
        return fases
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
        print("Aviso: no se pudo leer nautica_progress.json ({}). Se iniciará una plantilla nueva.".format(error))
        fases = crear_plantilla()
        guardar_datos(fases)
        return fases


def obtener_hitos(fases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Devuelve los hitos en una lista con el nombre de su fase."""
    return [
        {"fase": fase["fase"], "hito": hito}
        for fase in fases
        for hito in fase["hitos"]
    ]


def barra_progreso(completados: int, total: int) -> str:
    porcentaje = int(completados * 100 / total) if total else 0
    bloques = int(ANCHO_BARRA * porcentaje / 100)
    return "[{}{}] {}%".format("█" * bloques, "░" * (ANCHO_BARRA - bloques), porcentaje)


def mostrar_progreso(fases: List[Dict[str, Any]]) -> None:
    todos = obtener_hitos(fases)
    completados = sum(1 for item in todos if item["hito"]["completado"])
    print("\n=== HOJA DE RUTA NÁUTICA 2026-2027 ===")
    print("Progreso general: {} ({}/{})".format(barra_progreso(completados, len(todos)), completados, len(todos)))
    for fase in fases:
        hechos = sum(1 for hito in fase["hitos"] if hito["completado"])
        print("\n{} — {} ({}/{})".format(fase["fase"], barra_progreso(hechos, len(fase["hitos"])), hechos, len(fase["hitos"])))
        for hito in fase["hitos"]:
            marca = "X" if hito["completado"] else " "
            print("  [{}] {} — Objetivo: {}".format(marca, hito["descripcion"], hito["fecha_objetivo"]))


def seleccionar_hito(fases: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    todos = obtener_hitos(fases)
    print("\nSelecciona un hito:")
    for numero, item in enumerate(todos, start=1):
        marca = "X" if item["hito"]["completado"] else " "
        print("{:2}. [{}] {}".format(numero, marca, item["hito"]["descripcion"]))
        print("    {}".format(item["fase"]))
    respuesta = input("Número (Enter para cancelar): ").strip()
    if not respuesta:
        return None
    try:
        numero = int(respuesta)
        if 1 <= numero <= len(todos):
            return todos[numero - 1]["hito"]
    except ValueError:
        pass
    print("Selección no válida.")
    return None


def alternar_completado(fases: List[Dict[str, Any]]) -> None:
    hito = seleccionar_hito(fases)
    if hito is None:
        return
    hito["completado"] = not hito["completado"]
    guardar_datos(fases)
    estado = "completado" if hito["completado"] else "pendiente"
    print("Hito marcado como {}. Progreso guardado.".format(estado))


def editar_nota(fases: List[Dict[str, Any]]) -> None:
    hito = seleccionar_hito(fases)
    if hito is None:
        return
    print("Nota actual: {}".format(hito["notas"] or "(sin nota)"))
    print("Escribe una nueva nota. Déjala vacía para borrar la nota actual.")
    hito["notas"] = input("Nota: ").strip()
    guardar_datos(fases)
    print("Nota guardada.")


def mostrar_notas(fases: List[Dict[str, Any]]) -> None:
    print("\n=== RESUMEN DE NOTAS Y COMENTARIOS ===")
    hay_notas = False
    for fase in fases:
        for hito in fase["hitos"]:
            if hito["notas"].strip():
                hay_notas = True
                print("\n{}".format(fase["fase"]))
                print("  {}".format(hito["descripcion"]))
                print("  Nota: {}".format(hito["notas"]))
    if not hay_notas:
        print("Todavía no hay notas guardadas.")


def ejecutar() -> None:
    fases = cargar_datos()
    while True:
        print("\n" + "=" * 48)
        print("       SEGUIMIENTO DE HOJA DE RUTA NÁUTICA")
        print("=" * 48)
        print("[1] Ver progreso general y estado de la hoja de ruta")
        print("[2] Marcar / desmarcar un hito como completado")
        print("[3] Añadir o editar un comentario/nota")
        print("[4] Ver resumen de notas y comentarios guardados")
        print("[5] Guardar y salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            mostrar_progreso(fases)
        elif opcion == "2":
            alternar_completado(fases)
        elif opcion == "3":
            editar_nota(fases)
        elif opcion == "4":
            mostrar_notas(fases)
        elif opcion == "5":
            guardar_datos(fases)
            print("Progreso guardado en: {}".format(ARCHIVO_DATOS))
            print("¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Elige un número del 1 al 5.")


if __name__ == "__main__":
    ejecutar()
