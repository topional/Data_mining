"""Ejecutar y guardar notebooks con salidas visibles sin abrir un servidor.

Uso: python src/ejecutar_notebooks.py
     python src/ejecutar_notebooks.py notebooks/04_modelamiento.ipynb

Ejecuta el código local en el mismo proceso mediante IPython. No necesita
puertos, kernel externo ni conexión a internet (si el CSV ya existe).
"""

import argparse
import os
from pathlib import Path
import sys
import tempfile

import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output


class NotebookShell(InteractiveShell):
    def enable_gui(self, gui=None):
        # El backend inline publica imágenes; no necesita un bucle de interfaz gráfica.
        if gui is not None:
            raise ValueError("El ejecutor solo admite el backend inline")


def ejecutar(rutas):
    root = Path(__file__).resolve().parents[1]
    rutas = [Path(ruta).resolve() for ruta in rutas]
    os.chdir(root)
    sys.path.insert(0, str(root))
    shell = NotebookShell.instance()
    for ruta in rutas:
        ruta = Path(ruta).resolve()
        notebook = nbformat.read(ruta, as_version=4)
        shell.reset(new_session=True)
        shell.run_line_magic("matplotlib", "inline")
        print(f"Ejecutando {ruta.name}", flush=True)
        for numero, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue
            print(f"  celda {numero + 1}/{len(notebook.cells)}", flush=True)
            with capture_output() as salida:
                resultado = shell.run_cell(cell.source, store_history=True)
            cell.execution_count = resultado.execution_count
            cell.outputs = []
            if salida.stdout:
                cell.outputs.append(nbformat.v4.new_output("stream", name="stdout", text=salida.stdout))
            if salida.stderr:
                cell.outputs.append(nbformat.v4.new_output("stream", name="stderr", text=salida.stderr))
            for rich in salida.outputs:
                cell.outputs.append(nbformat.v4.new_output("display_data", data=rich.data, metadata=rich.metadata))
            error = resultado.error_before_exec or resultado.error_in_exec
            if error:
                # Mantener el notebook anterior; no guardar resultados parciales sobre él.
                raise RuntimeError(f"{ruta.name}, celda {numero + 1}: {error}") from error
        notebook.metadata["kernelspec"] = {
            "display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"}
        notebook.metadata["language_info"] = {"name": "python", "version": sys.version.split()[0]}
        nbformat.validate(notebook)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", dir=ruta.parent,
                                         delete=False, encoding="utf-8") as archivo:
            nbformat.write(notebook, archivo)
            temporal = Path(archivo.name)
        temporal.replace(ruta)
        print(f"  OK: {ruta.name} guardado con resultados", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    rutas = args.notebooks or sorted((root / "notebooks").glob("[0-9][0-9]_*.ipynb"))
    ejecutar(rutas)
