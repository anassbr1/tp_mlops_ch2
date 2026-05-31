"""
pipeline/orchestrate.py
-----------------------
Étape 3 : Orchestration avec Dagster.
Ce fichier définit les assets Dagster correspondant aux étapes du pipeline :
  1. ingest_ventes    → ingestion CSV → DuckDB
  2. validate_ventes  → validation qualité
  3. transform_ventes → exécution dbt (transformation + tests)

Pour lancer l'UI Dagster : dagster dev -f pipeline/orchestrate.py
Pour exécuter sans UI    : python pipeline/orchestrate.py
"""

import subprocess
import sys
from pathlib import Path

from dagster import (
    asset,
    AssetExecutionContext,
    Definitions,
    materialize,
)

# Répertoires du projet
PROJECT_ROOT = Path(__file__).parent.parent
DBT_DIR = PROJECT_ROOT / "dbt_pipeline"


# ---------------------------------------------------------------------------
# Asset 1 : Ingestion
# ---------------------------------------------------------------------------
@asset(
    name="ingest_ventes",
    description="Lit data/ventes.csv et charge les données dans DuckDB via dlt.",
    group_name="pipeline_ventes",
)
def ingest_ventes(context: AssetExecutionContext):
    context.log.info("=== Étape 1 : Ingestion ===")
    # Import local pour éviter l'import circulaire
    sys.path.insert(0, str(PROJECT_ROOT / "pipeline"))
    from ingest import run_ingestion

    load_info = run_ingestion()
    context.log.info(f"Ingestion OK : {load_info}")
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Asset 2 : Validation
# ---------------------------------------------------------------------------
@asset(
    name="validate_ventes",
    description="Vérifie la qualité des données ingérées dans DuckDB.",
    deps=[ingest_ventes],
    group_name="pipeline_ventes",
)
def validate_ventes(context: AssetExecutionContext):
    context.log.info("=== Étape 2 : Validation ===")
    sys.path.insert(0, str(PROJECT_ROOT / "pipeline"))
    from validate import validate

    erreurs = validate()
    context.log.info(f"Validation terminée. Anomalies : {len(erreurs)}")
    return {"anomalies": len(erreurs)}


# ---------------------------------------------------------------------------
# Asset 3 : Transformation dbt
# ---------------------------------------------------------------------------
@asset(
    name="transform_ventes",
    description="Exécute dbt run + dbt test pour transformer et valider les données.",
    deps=[validate_ventes],
    group_name="pipeline_ventes",
)
def transform_ventes(context: AssetExecutionContext):
    context.log.info("=== Étape 3 : Transformation dbt ===")

    # dbt run
    context.log.info("Lancement de : dbt run")
    result_run = subprocess.run(
        ["dbt", "run", "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR)],
        capture_output=True,
        text=True,
    )
    context.log.info(result_run.stdout)
    if result_run.returncode != 0:
        context.log.error(result_run.stderr)
        raise RuntimeError("dbt run a échoué.")

    # dbt test
    context.log.info("Lancement de : dbt test")
    result_test = subprocess.run(
        ["dbt", "test", "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR)],
        capture_output=True,
        text=True,
    )
    context.log.info(result_test.stdout)
    if result_test.returncode != 0:
        context.log.error(result_test.stderr)
        raise RuntimeError("dbt test a échoué.")

    context.log.info("Transformation et tests dbt réussis.")
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Définition Dagster
# ---------------------------------------------------------------------------
defs = Definitions(
    assets=[ingest_ventes, validate_ventes, transform_ventes],
)


# ---------------------------------------------------------------------------
# Exécution directe sans UI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Exécution du pipeline sans UI Dagster ===")
    print("(Pour l'UI, exécutez : dagster dev -f pipeline/orchestrate.py)\n")

    result = materialize(
        assets=[ingest_ventes, validate_ventes, transform_ventes],
        instance=None,
    )

    if result.success:
        print("\n✓ Pipeline exécuté avec succès !")
    else:
        print("\n✗ Le pipeline a rencontré des erreurs.")
        sys.exit(1)
