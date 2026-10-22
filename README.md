# titulos_barco

Hoja de ruta náutica 2026–2027 y herramientas personales para el seguimiento de la experiencia en la mar.

## Web

`index.html` es una página estática que puede publicarse con GitHub Pages. El checklist y las notas se guardan en el almacenamiento local del navegador. Usa la exportación JSON de la página para hacer copias de seguridad.

## Logbook de consola

Con Python 3.8 o posterior:

```sh
python logbook_nautico.py
```

El programa crea `logbook_nautico.json` al iniciarse y guarda los certificados exportados en `certificados_logbook/`.

## Hoja de ruta en consola

```sh
python nautica_tracker.py
```

El estado se guarda en `nautica_progress.json`.
