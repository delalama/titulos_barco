#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Personal Logbook / Sea Service Record, para Python 3.8+.

Guarda salidas en logbook_nautico.json y permite generar fichas Markdown
individuales listas para revisar y firmar.

Nota sobre los días: se calcula el número de fechas naturales cubiertas,
contando ambos extremos. La RYA define el día a bordo con criterios de horas
y tiempo efectivamente en la mar; confirma el cómputo con la RYA/DGMM y el
capitán antes de usarlo como acreditación oficial.
"""

import json
import os
from datetime import date
from typing import Any, Dict, List, Optional


CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_DATOS = os.path.join(CARPETA, "logbook_nautico.json")
CARPETA_CERTIFICADOS = os.path.join(CARPETA, "certificados_logbook")
TIPOS_BARCO = ("Vela", "Motor", "Catamarán")
ROLES = ("Patrón", "Primer Oficial/Mate", "Tripulación/Crew")


def cargar_registros() -> List[Dict[str, Any]]:
    """Carga el JSON existente o crea uno vacío en el primer inicio."""
    if not os.path.exists(ARCHIVO_DATOS):
        guardar_registros([])
        return []
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        if not isinstance(datos, list):
            raise ValueError("el contenido debe ser una lista JSON")
        return datos
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print("No se pudo cargar {}: {}".format(os.path.basename(ARCHIVO_DATOS), error))
        print("El archivo original se conserva. Se continuará con una lista vacía.")
        return []


def guardar_registros(registros: List[Dict[str, Any]]) -> None:
    """Guarda el archivo JSON con reemplazo atómico."""
    temporal = ARCHIVO_DATOS + ".tmp"
    with open(temporal, "w", encoding="utf-8") as archivo:
        json.dump(registros, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")
    os.replace(temporal, ARCHIVO_DATOS)


def leer_texto(etiqueta: str, obligatorio: bool = True) -> str:
    while True:
        valor = input(etiqueta).strip()
        if valor or not obligatorio:
            return valor
        print("Este campo es obligatorio.")


def leer_fecha(etiqueta: str) -> date:
    while True:
        valor = input("{} (AAAA-MM-DD): ".format(etiqueta)).strip()
        try:
            return date.fromisoformat(valor)
        except ValueError:
            print("Fecha no válida. Usa el formato AAAA-MM-DD, por ejemplo 2027-04-18.")


def leer_numero(etiqueta: str, minimo: float = 0.0) -> float:
    while True:
        valor = input(etiqueta).strip().replace(",", ".")
        try:
            numero = float(valor)
            if numero < minimo:
                raise ValueError
            return numero
        except ValueError:
            print("Introduce un número igual o superior a {}.".format(minimo))


def leer_si_no(etiqueta: str) -> bool:
    while True:
        respuesta = input(etiqueta + " [s/n]: ").strip().lower()
        if respuesta in ("s", "sí", "si", "y", "yes"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Responde s o n.")


def elegir_opcion(etiqueta: str, opciones: tuple) -> str:
    print(etiqueta)
    for numero, opcion in enumerate(opciones, start=1):
        print("  [{}] {}".format(numero, opcion))
    while True:
        respuesta = input("Opción: ").strip()
        if respuesta.isdigit() and 1 <= int(respuesta) <= len(opciones):
            return opciones[int(respuesta) - 1]
        print("Elige un número de la lista.")


def siguiente_id(registros: List[Dict[str, Any]]) -> str:
    usados = set()
    for registro in registros:
        identificador = str(registro.get("id", ""))
        if identificador.startswith("LOG-") and identificador[4:].isdigit():
            usados.add(int(identificador[4:]))
    numero = 1
    while numero in usados:
        numero += 1
    return "LOG-{:03d}".format(numero)


def registrar_salida(registros: List[Dict[str, Any]]) -> None:
    print("\n" + "─" * 62)
    print("NUEVA SALIDA / TRAVESÍA")
    print("─" * 62)
    fecha_inicio = leer_fecha("Fecha de salida")
    while True:
        fecha_fin = leer_fecha("Fecha de llegada")
        if fecha_fin >= fecha_inicio:
            break
        print("La fecha de llegada debe ser igual o posterior a la salida.")

    distancia = leer_numero("Distancia navegada (millas náuticas): ")
    horas_noche = leer_numero("Horas de navegación nocturna: ")
    registro = {
        "id": siguiente_id(registros),
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
        # Se cuenta cada fecha natural cubierta, incluidos el día de salida y llegada.
        "dias_mar": (fecha_fin - fecha_inicio).days + 1,
        "barco_nombre": leer_texto("Nombre de la embarcación: "),
        "barco_eslora": leer_numero("Eslora LOA en metros: "),
        "barco_tipo": elegir_opcion("Tipo de embarcación:", TIPOS_BARCO),
        "barco_mmsi_folio": leer_texto("MMSI o folio/matrícula: ", obligatorio=False),
        "origen_puerto": leer_texto("Puerto/cala de salida: "),
        "destino_puerto": leer_texto("Puerto/cala de llegada: "),
        "distancia_millas": distancia,
        "horas_nocturnas": horas_noche,
        "rol_a_bordo": elegir_opcion("Rol a bordo:", ROLES),
        "capitan_nombre": leer_texto("Nombre y apellidos del capitán: "),
        "capitan_titulacion": leer_texto("Titulación del capitán: "),
        "pasaje_60_millas": leer_si_no("¿Fue un pasaje ininterrumpido de más de 60 millas?"),
        "pasaje_nocturno": leer_si_no("¿Fue un pasaje nocturno (navegación durante la noche)?"),
        "notas_condiciones": leer_texto("Notas de condiciones/maniobras/incidentes (opcional): ", obligatorio=False),
    }
    registros.append(registro)
    guardar_registros(registros)
    print("\nSalida {} guardada. Días naturales cubiertos: {}.".format(registro["id"], registro["dias_mar"]))
    print("Recuerda que el cómputo oficial de días puede aplicar criterios distintos.")


def total(registros: List[Dict[str, Any]], campo: str) -> float:
    return sum(float(registro.get(campo, 0) or 0) for registro in registros)


def es_patron(registro: Dict[str, Any]) -> bool:
    return registro.get("rol_a_bordo") == "Patrón"


def pasajes_cualificados(registros: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [registro for registro in registros if registro.get("pasaje_60_millas", False)]


def barra(valor: float, objetivo: float, ancho: int = 18) -> str:
    porcentaje = min(100, int(valor * 100 / objetivo)) if objetivo else 100
    relleno = int(ancho * porcentaje / 100)
    return "[{}{}] {:3d}%".format("█" * relleno, "░" * (ancho - relleno), porcentaje)


def linea_objetivo(etiqueta: str, actual: float, objetivo: float, unidad: str) -> None:
    print("  {:<26} {:>8g} / {:<8g} {}  {}".format(etiqueta, actual, objetivo, unidad, barra(actual, objetivo)))


def mostrar_acumulados(registros: List[Dict[str, Any]]) -> None:
    millas = total(registros, "distancia_millas")
    nocturnas = total(registros, "horas_nocturnas")
    dias = total(registros, "dias_mar")
    pasajes = pasajes_cualificados(registros)
    pasajes_nocturnos = sum(1 for r in pasajes if r.get("pasaje_nocturno", False))
    pasajes_patron = sum(1 for r in pasajes if es_patron(r))
    dias_patron = sum(float(r.get("dias_mar", 0) or 0) for r in registros if es_patron(r))

    print("\n" + "═" * 66)
    print("RESUMEN DE SERVICIO EN LA MAR")
    print("═" * 66)
    print("Salidas registradas:       {}".format(len(registros)))
    print("Millas náuticas:           {:g} nm".format(millas))
    print("Horas nocturnas:           {:g} h".format(nocturnas))
    print("Días en la mar (estimado): {}".format(dias))
    print("Pasajes >60 nm:            {} ({} nocturnos, {} como patrón)".format(len(pasajes), pasajes_nocturnos, pasajes_patron))
    print("Días como patrón:          {}".format(dias_patron))
    print("\nCHECK DE EXPERIENCIA RYA (orientativo)")
    print("Day Skipper Practical — experiencia previa publicada por RYA:")
    linea_objetivo("Millas", millas, 100, "nm")
    linea_objetivo("Horas nocturnas", nocturnas, 4, "h")
    linea_objetivo("Días a bordo", dias, 5, "días")
    print("\nYachtmaster Offshore — requisitos publicados por RYA:")
    linea_objetivo("Millas", millas, 2500, "nm")
    linea_objetivo("Días en la mar", dias, 50, "días")
    linea_objetivo("Días como patrón", dias_patron, 5, "días")
    linea_objetivo("Pasajes >60 nm", len(pasajes), 5, "pasajes")
    linea_objetivo("Pasajes nocturnos >60 nm", pasajes_nocturnos, 2, "pasajes")
    linea_objetivo("Pasajes >60 nm como patrón", pasajes_patron, 2, "pasajes")
    print("\nAviso: este cálculo es orientativo. RYA evalúa, entre otros criterios, los días a bordo,")
    print("la eslora/tipo del barco, la disciplina (vela/motor), los pasajes documentados y la experiencia.")
    print("Confirma la elegibilidad con RYA; la DGMM puede exigir documentación y cómputos propios.")


def fmt_numero(valor: Any) -> str:
    try:
        return "{:g}".format(float(valor))
    except (TypeError, ValueError):
        return str(valor or "")


def mostrar_historial(registros: List[Dict[str, Any]]) -> None:
    print("\n" + "═" * 82)
    print("HISTORIAL DE SALIDAS")
    print("═" * 82)
    if not registros:
        print("Todavía no hay salidas registradas.")
        return
    for registro in sorted(registros, key=lambda r: (r.get("fecha_inicio", ""), r.get("id", ""))):
        paso = "Sí" if registro.get("pasaje_60_millas", False) else "No"
        noche = "Sí" if registro.get("pasaje_nocturno", False) else "No"
        print("\n{} | {} → {} | {} nm | {} día(s)".format(
            registro.get("id", "SIN-ID"), registro.get("fecha_inicio", ""),
            registro.get("fecha_fin", ""), fmt_numero(registro.get("distancia_millas")),
            registro.get("dias_mar", 0)))
        print("  {} ({}, {} m) · {} → {}".format(
            registro.get("barco_nombre", ""), registro.get("barco_tipo", ""),
            fmt_numero(registro.get("barco_eslora")), registro.get("origen_puerto", ""),
            registro.get("destino_puerto", "")))
        print("  Rol: {} · Capitán: {} ({})".format(registro.get("rol_a_bordo", ""),
            registro.get("capitan_nombre", ""), registro.get("capitan_titulacion", "")))
        print("  Horas nocturnas: {} · >60 nm: {} · Pasaje nocturno: {}".format(
            fmt_numero(registro.get("horas_nocturnas")), paso, noche))
        if registro.get("notas_condiciones"):
            print("  Notas: {}".format(registro["notas_condiciones"]))


def markdown_certificado(registro: Dict[str, Any]) -> str:
    """Genera el texto de certificación de una salida para revisión y firma."""
    pasaje = "Sí" if registro.get("pasaje_60_millas", False) else "No"
    nocturno = "Sí" if registro.get("pasaje_nocturno", False) else "No"
    notas = registro.get("notas_condiciones", "").strip() or "—"
    return """# CERTIFICADO DE SALIDA / SEA SERVICE RECORD

**Referencia:** {id}  
**Periodo:** {fecha_inicio} a {fecha_fin}  
**Días naturales cubiertos (cómputo automático):** {dias_mar}

## Embarcación y travesía

| Campo | Datos |
|---|---|
| Nombre del barco | {barco_nombre} |
| Tipo | {barco_tipo} |
| Eslora LOA | {barco_eslora} m |
| MMSI / Folio / Matrícula | {barco_mmsi_folio} |
| Puerto de salida | {origen_puerto} |
| Puerto de llegada | {destino_puerto} |
| Distancia navegada | {distancia_millas} millas náuticas |
| Horas de navegación nocturna | {horas_nocturnas} h |
| Pasaje ininterrumpido de más de 60 nm | {pasaje} |
| Pasaje nocturno | {nocturno} |

## Servicio a bordo

**Rol:** {rol_a_bordo}  
**Capitán:** {capitan_nombre}  
**Titulación del capitán:** {capitan_titulacion}

**Condiciones, meteorología, maniobras o incidentes:**  
{notas_condiciones}

## Declaración del capitán

Declaro que, según mi leal saber y entender, los datos de esta salida/travesía
son correctos y que la persona indicada participó a bordo en el periodo y rol
descritos.

**Nombre del capitán:** ______________________________________________

**Firma:** __________________________________  **Fecha:** ____ / ____ / ______

**Datos de contacto / sello (opcional):** ______________________________

---

*Documento preparado a partir de datos personales del logbook. Debe revisarse,
corregirse si procede y firmarse por el capitán. La aceptación y el cómputo de
servicio dependen de los requisitos vigentes de RYA/DGMM y de la documentación
de respaldo; este formulario no constituye por sí solo una certificación oficial.*
""".format(
        id=registro.get("id", ""), fecha_inicio=registro.get("fecha_inicio", ""),
        fecha_fin=registro.get("fecha_fin", ""), dias_mar=registro.get("dias_mar", ""),
        barco_nombre=registro.get("barco_nombre", ""), barco_tipo=registro.get("barco_tipo", ""),
        barco_eslora=fmt_numero(registro.get("barco_eslora")), barco_mmsi_folio=registro.get("barco_mmsi_folio", "") or "No indicado",
        origen_puerto=registro.get("origen_puerto", ""), destino_puerto=registro.get("destino_puerto", ""),
        distancia_millas=fmt_numero(registro.get("distancia_millas")), horas_nocturnas=fmt_numero(registro.get("horas_nocturnas")),
        pasaje=pasaje, nocturno=nocturno, rol_a_bordo=registro.get("rol_a_bordo", ""),
        capitan_nombre=registro.get("capitan_nombre", ""), capitan_titulacion=registro.get("capitan_titulacion", ""),
        notas_condiciones=notas)


def exportar_certificado(registros: List[Dict[str, Any]]) -> None:
    if not registros:
        print("No hay salidas que se puedan exportar.")
        return
    print("\nSelecciona la salida que quieres exportar:")
    ordenados = sorted(registros, key=lambda r: (r.get("fecha_inicio", ""), r.get("id", "")))
    for numero, registro in enumerate(ordenados, start=1):
        print("  [{}] {} | {} → {} | {} nm | {}".format(
            numero, registro.get("id", ""), registro.get("fecha_inicio", ""),
            registro.get("destino_puerto", ""), fmt_numero(registro.get("distancia_millas")),
            registro.get("barco_nombre", "")))
    respuesta = input("Número (Enter para cancelar): ").strip()
    if not respuesta:
        return
    if not respuesta.isdigit() or not 1 <= int(respuesta) <= len(ordenados):
        print("Selección no válida.")
        return
    registro = ordenados[int(respuesta) - 1]
    os.makedirs(CARPETA_CERTIFICADOS, exist_ok=True)
    ruta = os.path.join(CARPETA_CERTIFICADOS, "certificado_{}.md".format(registro.get("id", "salida")))
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(markdown_certificado(registro))
    print("Certificado Markdown guardado en: {}".format(ruta))


def ejecutar() -> None:
    registros = cargar_registros()
    while True:
        print("\n" + "═" * 58)
        print("       PERSONAL LOGBOOK · SEA SERVICE RECORD")
        print("═" * 58)
        print("[1] Registrar una nueva salida / travesía")
        print("[2] Ver resumen de acumulados y check de requisitos RYA")
        print("[3] Mostrar historial completo")
        print("[4] Exportar certificado / formulario de firma (.md)")
        print("[5] Guardar y salir")
        opcion = input("Elige una opción: ").strip()
        if opcion == "1":
            registrar_salida(registros)
        elif opcion == "2":
            mostrar_acumulados(registros)
        elif opcion == "3":
            mostrar_historial(registros)
        elif opcion == "4":
            exportar_certificado(registros)
        elif opcion == "5":
            guardar_registros(registros)
            print("Datos guardados en {}. ¡Buena proa!".format(ARCHIVO_DATOS))
            break
        else:
            print("Opción no válida. Elige un número del 1 al 5.")


if __name__ == "__main__":
    ejecutar()
