"""
pipeline/ingest.py
------------------
Étape 1 : Ingestion des données CSV vers DuckDB via dlt.
Ce script lit le fichier data/ventes.csv et le charge dans une base
DuckDB locale (pipeline/ventes.duckdb).
"""

import dlt
import pandas as pd
from pathlib import Path

# Chemin vers le fichier CSV source
CSV_PATH = Path(__file__).parent.parent / "data" / "ventes.csv"
# Chemin vers la base DuckDB de sortie
DUCKDB_PATH = Path(__file__).parent / "ventes.duckdb"


@dlt.resource(name="ventes", write_disposition="replace")
def source_ventes():
    """Générateur dlt : lit le CSV et produit des lignes une par une."""
    df = pd.read_csv(CSV_PATH)
    print(f"[ingest] {len(df)} lignes lues depuis {CSV_PATH}")
    for _, row in df.iterrows():
        yield row.to_dict()


def run_ingestion():
    """Lance le pipeline dlt d'ingestion."""
    print("[ingest] Démarrage de l'ingestion...")

    pipeline = dlt.pipeline(
        pipeline_name="ventes_pipeline",
        destination=dlt.destinations.duckdb(str(DUCKDB_PATH)),
        dataset_name="raw",
    )

    load_info = pipeline.run(source_ventes())
    print(f"[ingest] Ingestion terminée : {load_info}")
    print(f"[ingest] Base DuckDB créée : {DUCKDB_PATH}")
    return load_info


if __name__ == "__main__":
    run_ingestion()
