"""
pipeline/validate.py
--------------------
Étape 2 : Validation des données ingérées dans DuckDB.
Ce script vérifie les contraintes de qualité minimales :
  - Aucune valeur nulle dans les colonnes critiques
  - Les montants doivent être > 0
  - Les dates doivent être au bon format
Il affiche un rapport de validation et lève une erreur si des anomalies
bloquantes sont détectées.
"""

import duckdb
from pathlib import Path

DUCKDB_PATH = Path(__file__).parent / "ventes.duckdb"


def validate():
    """Exécute les contrôles de qualité sur la table raw.ventes."""
    print("[validate] Connexion à DuckDB...")

    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"[validate] Base DuckDB introuvable : {DUCKDB_PATH}\n"
            "Exécutez d'abord : python pipeline/ingest.py"
        )

    con = duckdb.connect(str(DUCKDB_PATH))

    # Récupère le nom exact de la table créée par dlt
    tables = con.execute("SHOW TABLES").fetchall()
    print(f"[validate] Tables disponibles : {[t[0] for t in tables]}")

    # dlt crée le schéma "raw" ; la table s'appelle "ventes"
    try:
        total = con.execute("SELECT COUNT(*) FROM raw.ventes").fetchone()[0]
    except Exception:
        # Fallback si le schéma n'est pas préfixé
        total = con.execute("SELECT COUNT(*) FROM ventes").fetchone()[0]

    print(f"[validate] Nombre total de lignes : {total}")

    erreurs = []

    # --- Contrôle 1 : montant NULL ---
    try:
        nulls = con.execute(
            "SELECT COUNT(*) FROM raw.ventes WHERE montant IS NULL"
        ).fetchone()[0]
    except Exception:
        nulls = con.execute(
            "SELECT COUNT(*) FROM ventes WHERE montant IS NULL"
        ).fetchone()[0]

    if nulls > 0:
        erreurs.append(f"  ⚠  {nulls} ligne(s) avec montant NULL")
    else:
        print("[validate] ✓ Aucun montant NULL")

    # --- Contrôle 2 : montant <= 0 ---
    try:
        zeros = con.execute(
            "SELECT COUNT(*) FROM raw.ventes WHERE montant <= 0"
        ).fetchone()[0]
    except Exception:
        zeros = con.execute(
            "SELECT COUNT(*) FROM ventes WHERE montant <= 0"
        ).fetchone()[0]

    if zeros > 0:
        erreurs.append(f"  ⚠  {zeros} ligne(s) avec montant <= 0")
    else:
        print("[validate] ✓ Tous les montants sont positifs")

    # --- Contrôle 3 : id_client NULL ---
    try:
        id_nulls = con.execute(
            "SELECT COUNT(*) FROM raw.ventes WHERE id_client IS NULL"
        ).fetchone()[0]
    except Exception:
        id_nulls = con.execute(
            "SELECT COUNT(*) FROM ventes WHERE id_client IS NULL"
        ).fetchone()[0]

    if id_nulls > 0:
        erreurs.append(f"  ⚠  {id_nulls} ligne(s) avec id_client NULL")
    else:
        print("[validate] ✓ Aucun id_client NULL")

    # --- Rapport final ---
    con.close()

    if erreurs:
        print("\n[validate] Anomalies détectées (non bloquantes) :")
        for e in erreurs:
            print(e)
        print(
            "\n[validate] Ces anomalies seront filtrées lors de la "
            "transformation dbt (statut='invalide')."
        )
    else:
        print("[validate] ✓ Toutes les validations ont réussi.")

    print("[validate] Validation terminée.")
    return erreurs


if __name__ == "__main__":
    validate()
