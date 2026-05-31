"""
check.py — Script de vérification de l'installation
----------------------------------------------------
Exécutez ce script AVANT de commencer le TP pour vérifier que
tous les outils sont correctement installés.

Usage :
    python check.py
"""

import sys
import importlib
import subprocess
from pathlib import Path

OK   = "  ✓"
FAIL = "  ✗"
WARN = "  ⚠"

errors = []

print("=" * 55)
print("  Vérification de l'environnement — TP MLOps Ch.2")
print("=" * 55)

# 1. Version Python
print("\n[1] Python")
ver = sys.version_info
if ver >= (3, 9):
    print(f"{OK} Python {ver.major}.{ver.minor}.{ver.micro}")
else:
    msg = f"Python >= 3.9 requis (version actuelle : {ver.major}.{ver.minor})"
    print(f"{FAIL} {msg}")
    errors.append(msg)

# 2. Bibliothèques Python
print("\n[2] Bibliothèques Python")
libs = ["dlt", "dbt", "dagster", "pandas", "duckdb"]
for lib in libs:
    try:
        mod = importlib.import_module(lib)
        version = getattr(mod, "__version__", "?")
        print(f"{OK} {lib} ({version})")
    except ImportError:
        msg = f"{lib} non installé — exécutez : pip install -r requirements.txt"
        print(f"{FAIL} {msg}")
        errors.append(msg)

# 3. Commandes en ligne de commande
print("\n[3] Commandes CLI")
cmds = ["dbt", "dagster"]
for cmd in cmds:
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True, text=True
        )
        version_line = (result.stdout or result.stderr).strip().split("\n")[0]
        print(f"{OK} {cmd} : {version_line}")
    except FileNotFoundError:
        msg = f"Commande '{cmd}' introuvable dans le PATH"
        print(f"{FAIL} {msg}")
        errors.append(msg)

# 4. Fichiers du projet
print("\n[4] Fichiers du projet")
required_files = [
    "data/ventes.csv",
    "pipeline/ingest.py",
    "pipeline/validate.py",
    "pipeline/orchestrate.py",
    "dbt_pipeline/dbt_project.yml",
    "dbt_pipeline/profiles.yml",
    "dbt_pipeline/models/ventes_clean.sql",
    "dbt_pipeline/models/ventes_resume.sql",
    "dbt_pipeline/models/schema.yml",
    ".gitignore",
    "requirements.txt",
]
for f in required_files:
    p = Path(f)
    if p.exists():
        print(f"{OK} {f}")
    else:
        msg = f"Fichier manquant : {f}"
        print(f"{FAIL} {msg}")
        errors.append(msg)

# 5. Git
print("\n[5] Git")
try:
    result = subprocess.run(
        ["git", "--version"], capture_output=True, text=True
    )
    print(f"{OK} {result.stdout.strip()}")
    # Vérifier que c'est un dépôt Git
    git_dir = Path(".git")
    if git_dir.exists():
        print(f"{OK} Dépôt Git initialisé")
    else:
        print(f"{WARN} .git absent — exécutez : git init")
except FileNotFoundError:
    msg = "Git non installé ou introuvable"
    print(f"{FAIL} {msg}")
    errors.append(msg)

# Résumé
print("\n" + "=" * 55)
if errors:
    print(f"  ✗ {len(errors)} problème(s) détecté(s) :")
    for e in errors:
        print(f"    - {e}")
    print("\n  Corrigez les erreurs ci-dessus avant de continuer.")
    sys.exit(1)
else:
    print("  ✓ Tout est prêt ! Vous pouvez commencer le TP.")
print("=" * 55)
