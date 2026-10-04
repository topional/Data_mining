"""Descarga el dataset original de SERVIR a data/raw/.

Intenta primero la fuente oficial (portal de Datos Abiertos) y, si falla,
usa la copia de respaldo en Google Drive.

Uso:
    python src/utils/download_data.py          # descarga si falta
    python src/utils/download_data.py --force  # vuelve a descargar
"""

import argparse
import hashlib
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
FILENAME = "Dataset_ENAP_RSCC_Dic_2025_May_2026.csv"

OFFICIAL_URL = (
    "https://www.datosabiertos.gob.pe/sites/default/files/"
    "Dataset_ENAP_RSCC_Dic_2025_May_2026.csv"
)
DRIVE_FILE_ID = "1jnBumWW9EzCBGUq41UP1m8_YVCm1zdVl"
DRIVE_URL = (
    "https://drive.usercontent.google.com/download"
    f"?id={DRIVE_FILE_ID}&export=download&confirm=t"
)

SOURCES = [("portal oficial (datosabiertos.gob.pe)", OFFICIAL_URL),
           ("respaldo en Google Drive", DRIVE_URL)]

EXPECTED_SHA256 = "92360ae29b38caf41d73ce92dd9918136da242e616ca175f6c33b512b50b79df"

HEADERS = {"User-Agent": "Mozilla/5.0 (proyecto academico UPC - data mining)"}

def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    with requests.get(url, headers=HEADERS, stream=True, timeout=60) as r:
        r.raise_for_status()
        if "text/html" in r.headers.get("Content-Type", ""):
            raise ValueError("la respuesta es una página HTML, no el CSV")
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)


def main(force: bool) -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / FILENAME

    if dest.exists() and not force:
        print(f"[ok] {FILENAME} ya existe en {RAW_DIR}. Usa --force para reemplazarlo.")
        return 0

    for label, url in SOURCES:
        try:
            print(f"[...] Descargando desde {label}")
            download(url, dest)
            if EXPECTED_SHA256 and sha256_of(dest) != EXPECTED_SHA256:
                raise ValueError("el hash SHA-256 no coincide con el esperado")
            size_mb = dest.stat().st_size / 1e6
            print(f"[ok] {FILENAME} listo ({size_mb:.1f} MB) en {RAW_DIR}")
            return 0
        except Exception as e:
            print(f"[!] Falló {label}: {e}")
            dest.unlink(missing_ok=True)

    print("\nNo se pudo descargar el dataset. Descárgalo manualmente desde:")
    print("  https://drive.google.com/file/d/" + DRIVE_FILE_ID + "/view")
    print(f"y colócalo en {RAW_DIR}")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-descargar")
    sys.exit(main(parser.parse_args().force))