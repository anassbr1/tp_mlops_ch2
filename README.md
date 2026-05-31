# TD-TP 2 — Pipelines agiles, versionnement et orchestration
### MLOps & DataOps — Pr. Mohammed AIT DAOUD

---

## Schéma du pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PIPELINE VENTES — FLUX COMPLET                  │
└─────────────────────────────────────────────────────────────────────┘

  [data/ventes.csv]
        │
        │  lecture pandas
        ▼
  ┌─────────────┐
  │  INGESTION  │  pipeline/ingest.py  (outil : dlt)
  │  dlt + CSV  │  → charge les données brutes dans DuckDB
  └──────┬──────┘
         │
         │  raw.ventes (DuckDB)
         ▼
  ┌──────────────┐
  │  VALIDATION  │  pipeline/validate.py  (outil : duckdb)
  │  qualité     │  → vérifie NULLs, montants ≤ 0, ids manquants
  └──────┬───────┘
         │
         │  données validées (anomalies signalées)
         ▼
  ┌─────────────────┐
  │ TRANSFORMATION  │  dbt run  (outil : dbt-duckdb)
  │  dbt models     │  → ventes_clean  : filtrage + cast types
  │                 │  → ventes_resume : agrégation région/mois
  └──────┬──────────┘
         │
         │  modèles transformés
         ▼
  ┌──────────────┐
  │  TESTS dbt   │  dbt test  (outil : dbt test)
  │  qualité     │  → not_null, unique, accepted_values
  └──────┬───────┘
         │
         ▼
  ┌─────────────────────────────────────┐
  │         ORCHESTRATION               │  pipeline/orchestrate.py
  │  Dagster coordonne tout le flux     │  (outil : Dagster)
  │  ingest → validate → transform      │
  └─────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────┐
  │  CI/CD (GitHub Actions)             │
  │  Vérifie le pipeline à chaque push  │
  └─────────────────────────────────────┘
```

---

## Arborescence du projet

```
tp_mlops/
├── data/
│   └── ventes.csv                    ← Source brute de données
├── pipeline/
│   ├── ingest.py                     ← Ingestion dlt → DuckDB
│   ├── validate.py                   ← Contrôles qualité
│   └── orchestrate.py                ← Orchestration Dagster
├── dbt_pipeline/
│   ├── dbt_project.yml               ← Configuration dbt
│   ├── profiles.yml                  ← Connexion DuckDB
│   └── models/
│       ├── ventes_clean.sql          ← Nettoyage des données
│       ├── ventes_resume.sql         ← Agrégation par région/mois
│       └── schema.yml                ← Tests dbt (not_null, unique…)
├── .github/
│   └── workflows/
│       └── ci.yml                    ← Pipeline CI GitHub Actions
├── .gitignore
├── requirements.txt
├── check.py                          ← Script de vérification (optionnel)
├── README.md                         ← Ce fichier
└── REPONSES.md                       ← Réponses aux questions du TP
```

---

## Prérequis

- **Python 3.9 ou supérieur** installé
- **Git** installé
- **Connexion internet** pour l'installation des packages
- (Optionnel) Un compte **GitHub** pour la CI

Vérifier la version Python :
```bash
# Windows
py --version
# ou
python --version

# Linux / Mac
python3 --version
```

---

## Installation pas à pas

### Étape 0 — Cloner ou décompresser le projet

```bash
# Si vous décompressez une archive :
# Décompressez tp_mlops.zip, puis entrez dans le dossier :
cd tp_mlops
```

### Étape 1 — Créer l'environnement virtuel

> **Pourquoi ?** Un environnement virtuel isole les dépendances du projet
> des autres projets Python sur votre machine. C'est la base de la
> **reproductibilité** en MLOps.

```bash
# Windows (CMD ou PowerShell)
py -m venv .venv

# Linux / Mac
python3 -m venv .venv
```

### Étape 2 — Activer l'environnement virtuel

```bash
# Windows CMD
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / Mac
source .venv/bin/activate
```

> ✓ Vous devriez voir `(.venv)` au début de votre ligne de commande.

> **Dépannage Windows PowerShell :** Si vous obtenez une erreur
> "scripts disabled", exécutez d'abord :
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Étape 3 — Installer les dépendances

```bash
pip install -r requirements.txt
```

> Cette commande installe : dlt, dbt-duckdb, dagster, pandas, duckdb.
> L'installation peut prendre 2 à 5 minutes.
>
> ✓ Vérification : `pip list` doit afficher tous les packages.

### Étape 4 — Vérifier l'installation (optionnel mais recommandé)

```bash
python check.py
```

> Ce script vérifie que Python, toutes les bibliothèques, les commandes
> CLI et tous les fichiers du projet sont bien en place.
> **Corrigez toute erreur avant de continuer.**

### Étape 5 — Initialiser le dépôt Git

> **Pourquoi ?** Git permet de versionner le code et de tracer l'historique
> des modifications. C'est indispensable dans tout pipeline industrialisé.

```bash
git init
git add .
git commit -m "init: structure initiale du projet MLOps TP2"
```

---

## Exécution du pipeline (étape par étape)

### Étape A — Ingestion des données

> **Ce que fait cette étape :** lit `data/ventes.csv` et charge les
> données dans une base DuckDB locale (`pipeline/ventes.duckdb`) via dlt.

```bash
python pipeline/ingest.py
```

**Sortie attendue :**
```
[ingest] Démarrage de l'ingestion...
[ingest] 15 lignes lues depuis .../data/ventes.csv
[ingest] Ingestion terminée : ...
[ingest] Base DuckDB créée : .../pipeline/ventes.duckdb
```

**Vérification :** Le fichier `pipeline/ventes.duckdb` doit exister.

```bash
# Commit après cette étape
git add pipeline/
git commit -m "feat(ingest): ajout du script d'ingestion dlt"
```

---

### Étape B — Validation des données

> **Ce que fait cette étape :** se connecte à DuckDB et vérifie la
> qualité des données (valeurs nulles, montants négatifs, etc.).
> Les anomalies sont signalées mais non bloquantes car elles seront
> filtrées par dbt.

```bash
python pipeline/validate.py
```

**Sortie attendue :**
```
[validate] Connexion à DuckDB...
[validate] Nombre total de lignes : 15
[validate] ✓ Aucun id_client NULL
[validate] Anomalies détectées (non bloquantes) :
  ⚠  3 ligne(s) avec montant NULL ou <= 0
[validate] Validation terminée.
```

```bash
git add pipeline/validate.py
git commit -m "feat(validate): ajout de la validation qualité"
```

---

### Étape C — Transformation dbt

> **Ce que fait cette étape :**
> - `dbt run` crée les vues `ventes_clean` (données filtrées et castées)
>   et `ventes_resume` (agrégation par région et mois).
> - `dbt test` vérifie les contraintes définies dans `schema.yml`.

```bash
# Transformation
dbt run --project-dir dbt_pipeline --profiles-dir dbt_pipeline

# Tests de qualité
dbt test --project-dir dbt_pipeline --profiles-dir dbt_pipeline
```

**Sortie attendue pour dbt run :**
```
Running with dbt=...
Found 2 models, 0 tests, 0 snapshots, ...
  OK created view model raw.ventes_clean ............. [OK]
  OK created view model raw.ventes_resume ............ [OK]
Finished running 2 view models in ...
Completed successfully
```

**Sortie attendue pour dbt test :**
```
Running 10 tests...
  PASS not_null_ventes_clean_id_client ............... [PASS]
  PASS unique_ventes_clean_id_client ................. [PASS]
  ... (tous les tests doivent passer)
Completed successfully
```

```bash
git add dbt_pipeline/
git commit -m "feat(dbt): ajout des modèles ventes_clean et ventes_resume + tests"
```

---

### Étape D — Orchestration avec Dagster

> **Ce que fait cette étape :** Dagster enchaîne automatiquement les
> trois étapes précédentes (ingest → validate → transform) dans le bon
> ordre, avec journalisation et gestion des dépendances.

**Option 1 : Interface graphique Dagster (recommandée)**

```bash
# Windows
set DAGSTER_HOME=%CD%\.dagster
dagster dev -f pipeline/orchestrate.py

# Linux / Mac
export DAGSTER_HOME=$(pwd)/.dagster
dagster dev -f pipeline/orchestrate.py
```

Ouvrez ensuite votre navigateur à l'adresse : **http://localhost:3000**

Dans l'interface :
1. Cliquez sur "Assets" dans le menu gauche
2. Sélectionnez tous les assets (`ingest_ventes`, `validate_ventes`, `transform_ventes`)
3. Cliquez sur "Materialize all"
4. Observez l'exécution en temps réel

**Option 2 : Exécution en ligne de commande (sans UI)**

```bash
python pipeline/orchestrate.py
```

```bash
git add pipeline/orchestrate.py
git commit -m "feat(dagster): ajout de l'orchestration du pipeline"
```

---

### Étape E — CI GitHub Actions (optionnel)

> **Ce que fait cette étape :** configure un workflow automatisé qui
> vérifie le pipeline à chaque push sur GitHub.

```bash
# Créer un dépôt GitHub, puis :
git remote add origin https://github.com/VOTRE_NOM/tp_mlops.git
git branch -M main
git push -u origin main
```

La CI se déclenche automatiquement. Consultez l'onglet **Actions**
de votre dépôt GitHub pour voir les résultats.

```bash
git add .github/
git commit -m "ci: ajout du workflow GitHub Actions"
git push
```

---

## Historique Git simulé (commits recommandés)

Voici l'historique à reproduire dans votre projet :

```
git log --oneline

a7f3d2e  ci: ajout du workflow GitHub Actions
9c1b5f8  feat(dagster): ajout de l'orchestration du pipeline
6e8a2d1  feat(dbt): ajout des modèles ventes_clean et ventes_resume + tests
4f9c3b7  feat(validate): ajout de la validation qualité
2d5e1a9  feat(ingest): ajout du script d'ingestion dlt
1b3c8e4  init: structure initiale du projet MLOps TP2
```

---

## Captures d'écran à fournir

Pour votre rapport, prenez des captures d'écran après chaque commande :

| # | Commande à exécuter | Ce qu'il faut capturer |
|---|--------------------|-----------------------|
| 1 | `python check.py` | Tous les ✓ verts |
| 2 | `python pipeline/ingest.py` | Message "Ingestion terminée" |
| 3 | `python pipeline/validate.py` | Rapport de validation |
| 4 | `dbt run --project-dir dbt_pipeline --profiles-dir dbt_pipeline` | "Completed successfully" + 2 modèles |
| 5 | `dbt test --project-dir dbt_pipeline --profiles-dir dbt_pipeline` | Tous les tests PASS |
| 6 | `dagster dev -f pipeline/orchestrate.py` + UI | Interface Dagster avec les 3 assets verts |
| 7 | `git log --oneline` | Les 6 commits |
| 8 | GitHub → onglet Actions | Workflow CI vert (si applicable) |

---

## Dépannage

### Windows : `source` non reconnu
```
# NE PAS utiliser :
source .venv/bin/activate

# UTILISER à la place (CMD) :
.venv\Scripts\activate.bat

# UTILISER à la place (PowerShell) :
.venv\Scripts\Activate.ps1
```

### Windows : `python` non reconnu
```
# Essayer :
py pipeline/ingest.py
# ou
python3 pipeline/ingest.py
```

### Windows PowerShell : erreur "scripts disabled"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### `dbt` non reconnu après installation
```bash
# Vérifier que l'environnement virtuel est activé, puis :
pip install dbt-duckdb
# Ou essayer :
python -m dbt run --project-dir dbt_pipeline --profiles-dir dbt_pipeline
```

### Erreur dbt : "Could not find profile named 'dbt_pipeline'"
```bash
# Toujours spécifier --profiles-dir :
dbt run --project-dir dbt_pipeline --profiles-dir dbt_pipeline
```

### Erreur "Table raw.ventes not found" dans dbt
```bash
# Exécutez d'abord l'ingestion :
python pipeline/ingest.py
# Puis relancez dbt
```

### Dagster : port 3000 déjà utilisé
```bash
dagster dev -f pipeline/orchestrate.py --port 3001
```

### `pip install` très lent
```bash
# Utiliser un miroir plus rapide :
pip install -r requirements.txt -i https://pypi.org/simple/
```

---

## Exécution complète en une seule fois

### Windows (CMD)

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
git init
git add .
git commit -m "init: structure initiale du projet MLOps TP2"
py pipeline/ingest.py
py pipeline/validate.py
dbt run --project-dir dbt_pipeline --profiles-dir dbt_pipeline
dbt test --project-dir dbt_pipeline --profiles-dir dbt_pipeline
echo Pipeline execute avec succes !
```

### Linux / Mac (Bash)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
git init
git add .
git commit -m "init: structure initiale du projet MLOps TP2"
python pipeline/ingest.py
python pipeline/validate.py
dbt run --project-dir dbt_pipeline --profiles-dir dbt_pipeline
dbt test --project-dir dbt_pipeline --profiles-dir dbt_pipeline
echo "✓ Pipeline exécuté avec succès !"
```
