# RÉPONSES — TD-TP 2 : Pipelines agiles, versionnement et orchestration
### MLOps & DataOps — Pr. Mohammed AIT DAOUD

---

## Partie I — QCM (réponses)

| Question | Réponse | Justification |
|----------|---------|---------------|
| Q1 | **c** | structurer un flux répétable, traçable et contrôlable |
| Q2 | **b** | toute activité qui consomme des ressources sans créer de valeur suffisante |
| Q3 | **c** | le code, les configurations, les données et les artefacts |
| Q4 | **b** | gérer l'enchaînement, la planification et la supervision des tâches |
| Q5 | **b** | de détecter rapidement certaines erreurs après modification |
| Q6 | **c** | l'entraînement, l'évaluation et la gestion des modèles |
| Q7 | **b** | dont les dépendances et paramètres sont explicités et reconstruisibles |
| Q8 (Agile) | **c** | travailler par itérations avec feedback et adaptation |
| Q8 (correct) | **c** | DataOps et MLOps complètent DevOps dans les systèmes pilotés par les données |

---

## Partie I — Questions directes

**1. Définir la notion de pipeline dans un contexte data ou ML.**

Un pipeline data/ML est une séquence structurée, automatisée et reproductible d'étapes de traitement qui transforment des données brutes en un résultat exploitable (données transformées, modèle entraîné, métriques). Chaque étape a des entrées et des sorties clairement définies. Le pipeline garantit que le même processus peut être rejoué à l'identique.

**2. Expliquer la différence entre pipeline de données et pipeline ML.**

Le pipeline de données (DataOps) couvre l'ingestion, le nettoyage, la transformation et le stockage des données. Il s'arrête à la mise à disposition de données fiables et structurées.

Le pipeline ML (MLOps) va plus loin : il intègre en plus l'entraînement d'un modèle, son évaluation, la comparaison de versions, l'enregistrement de l'artefact modèle et son déploiement. Le pipeline ML consomme donc la sortie d'un pipeline de données.

**3. Pourquoi le versionnement des seules sources de code est-il insuffisant en MLOps ?**

En MLOps, le résultat dépend de quatre éléments distincts : le code, les données d'entraînement, les hyperparamètres/configurations, et les artefacts produits (modèle sérialisé, métriques). Si on ne versionne que le code, on ne peut pas reproduire un modèle identique lorsque les données ou les paramètres ont changé. Git ne gère pas les fichiers volumineux (CSV, modèles binaires), d'où la nécessité d'outils comme DVC pour les données et les artefacts.

**4. En quoi la cartographie du flux de valeur aide-t-elle à améliorer un système de traitement ?**

La cartographie du flux de valeur (Value Stream Mapping, issue du Lean) permet de visualiser l'ensemble des étapes par lesquelles passe une donnée depuis la source jusqu'au résultat final. Elle met en évidence les étapes qui créent de la valeur et celles qui constituent des gaspillages (attentes, actions manuelles, duplications). En la réalisant, une équipe peut identifier les goulets d'étranglement, prioriser les automatisations les plus impactantes et mesurer objectivement les améliorations.

**5. Pourquoi un pipeline peut-il être techniquement correct mais organisationnellement inefficace ?**

Un pipeline peut produire des résultats corrects et tourner sans erreur, mais rester inefficace si : les équipes ne partagent pas un référentiel commun (documentation absente, silos), les résultats ne sont pas accessibles aux décideurs dans les délais requis, les responsabilités ne sont pas clairement définies (qui déclenche le pipeline ? qui valide ?), ou si le pipeline répond à des besoins mal définis. L'efficacité organisationnelle exige une collaboration, une communication et une gouvernance que la technique seule ne peut pas fournir.

**6. Quel est le rôle de l'orchestration dans la robustesse du workflow ?**

L'orchestration garantit que les tâches s'exécutent dans le bon ordre, en respectant les dépendances entre elles. En cas d'échec d'une étape, l'orchestrateur arrête le pipeline et signale l'erreur précisément (pas de propagation silencieuse d'un résultat incorrect). Il gère aussi la planification (exécution planifiée), la reprise sur erreur (retry), la journalisation et la supervision. Sans orchestration, un pipeline dépend de l'intervention humaine pour l'ordre et la surveillance des tâches.

**7. Pourquoi la CI est-elle importante même avant le déploiement final ?**

La CI permet de détecter les régressions dès qu'un changement est introduit dans le code, avant même que celui-ci n'atteigne l'environnement de production. Elle garantit que le pipeline peut être installé et exécuté sur une machine vierge (vérification des dépendances), que la syntaxe du code est valide, et que les tests passent. Sans CI, une erreur introduite dans un commit peut rester invisible jusqu'au prochain déploiement manuel, parfois des semaines plus tard.

---

## Partie II — Questions pratiques

### Question 1 — En quoi ce pipeline est-il plus structuré qu'un notebook unique ?

Un notebook unique mélange dans un même fichier le code de lecture des données, le nettoyage, l'entraînement et l'affichage des résultats. Il n'a pas de structure formelle : les cellules peuvent être exécutées dans n'importe quel ordre, il n'y a pas de séparation des responsabilités, et la reproductibilité dépend de l'état interne du noyau (variables non réinitialisées entre deux exécutions).

Le pipeline structuré proposé dans ce TP sépare clairement :
- **`ingest.py`** : responsabilité unique — charger les données
- **`validate.py`** : responsabilité unique — contrôler la qualité
- **`dbt models`** : responsabilité unique — transformer et agréger
- **`orchestrate.py`** : responsabilité unique — définir l'ordre et les dépendances

Chaque script peut être testé, versionné et rejoué indépendamment. L'orchestrateur garantit l'ordre d'exécution. Les données et le code sont versionnés séparément. Ce pipeline est **répétable** (même résultat à chaque exécution), **traçable** (historique Git + logs Dagster) et **contrôlable** (tests automatisés à chaque étape).

---

### Question 2 — Quel est le rôle de Git dans ce projet ?

Git joue trois rôles essentiels :

1. **Versionnement du code** : chaque modification des scripts (`ingest.py`, `validate.py`, `orchestrate.py`) et des configurations (`dbt_project.yml`, `profiles.yml`, `schema.yml`) est enregistrée dans un commit avec un message explicite. On peut revenir à n'importe quelle version antérieure.

2. **Traçabilité** : l'historique des commits constitue un journal de bord du projet. On sait qui a modifié quoi, quand, et pourquoi (via le message de commit). Cela facilite le débogage ("à quel commit le pipeline a-t-il commencé à échouer ?").

3. **Collaboration et intégration** : Git est le déclencheur de la CI (GitHub Actions). Chaque `git push` lance automatiquement la vérification du pipeline. Il permet aussi à plusieurs développeurs de travailler en parallèle sur des branches séparées.

Dans ce projet, Git ne versionne **pas** les fichiers volumineux (base DuckDB, données) grâce au `.gitignore`. Dans un projet MLOps complet, DVC prendrait en charge cette partie.

---

### Question 3 — Quel est le rôle de `requirements.txt` ?

`requirements.txt` est le contrat de reproductibilité de l'environnement logiciel. Il liste exactement quelles bibliothèques Python sont nécessaires et, si les versions sont épinglées, dans quelles versions.

Sans ce fichier, deux développeurs travaillant sur le même code pourraient avoir des versions différentes de pandas ou de dbt, et obtenir des comportements différents (voire des erreurs). En versionnant `requirements.txt` dans Git, on garantit que :
- n'importe qui peut recréer l'environnement exact avec `pip install -r requirements.txt`
- la CI peut installer exactement les mêmes dépendances que le développeur local
- on peut identifier quelle version d'une bibliothèque a introduit un bug en consultant l'historique Git du fichier

`requirements.txt` est complémentaire à `venv` : venv crée l'espace isolé, `requirements.txt` définit ce qui y est installé.

---

### Question 4 — Pourquoi ajouter une étape `validate.py` ?

L'étape de validation répond au principe "fail fast" : mieux vaut détecter un problème de qualité des données dès l'ingestion que de le découvrir après l'entraînement d'un modèle ou la production d'un rapport erroné.

Dans ce pipeline, `validate.py` détecte :
- les **montants NULL** (lignes incomplètes, saisie manquante)
- les **montants nuls ou négatifs** (erreurs de saisie ou de conversion)
- les **identifiants clients manquants** (données corrompues)

Ces anomalies sont signalées explicitement dans les logs, permettant à l'équipe d'agir sur la source. Sans cette étape, les données invalides seraient silencieusement propagées jusqu'à la transformation dbt, où elles seraient filtrées sans alerte, masquant potentiellement un problème systémique en amont.

La validation constitue également un point de contrôle : si le nombre d'anomalies dépasse un seuil critique, on peut lever une erreur bloquante et arrêter le pipeline.

---

### Question 5 — Quel est le rôle de `dbt test` ?

`dbt test` exécute des tests automatisés sur les modèles de données produits par `dbt run`. Ces tests sont déclarés dans `schema.yml` et vérifiés à chaque exécution.

Dans ce projet, les tests incluent :
- **`not_null`** : vérifie qu'aucune colonne critique ne contient de valeur nulle
- **`unique`** : vérifie que `id_client` est unique dans `ventes_clean` (pas de doublons)
- **`accepted_values`** : vérifie que la colonne `region` ne contient que les valeurs attendues (`Nord`, `Sud`, `Est`, `Ouest`) et que `statut` vaut toujours `valide`

Ces tests jouent le rôle de **filet de sécurité** : si une transformation introduit une régression (ex. suppression accidentelle du filtre sur `statut`), les tests le détectent immédiatement. Ils constituent la "qualité métier" automatisée du pipeline, complémentaires à la CI qui vérifie la qualité technique.

---

### Question 6 — Qu'apporte Dagster par rapport à une exécution manuelle ?

Sans Dagster, l'exécution du pipeline consiste à lancer manuellement trois commandes dans le bon ordre :
```
python pipeline/ingest.py
python pipeline/validate.py
dbt run && dbt test
```

Cette approche présente plusieurs risques : oubli d'une étape, mauvais ordre, absence de journalisation structurée, difficulté à rejouer uniquement une partie du pipeline, et impossibilité de planifier des exécutions automatiques.

Dagster apporte :
1. **Déclaration explicite des dépendances** : `validate_ventes` ne peut s'exécuter que si `ingest_ventes` a réussi.
2. **Interface graphique** : visualisation du graphe d'exécution, logs par étape, historique des runs.
3. **Gestion des erreurs** : si une étape échoue, Dagster arrête le pipeline et signale précisément l'étape fautive.
4. **Planification** : possibilité d'exécuter le pipeline selon un schedule (ex. chaque lundi à 8h).
5. **Observabilité** : chaque exécution est tracée avec ses métriques, ses logs et son statut.
6. **Rejeu partiel** : possibilité de ne rejouer que les assets modifiés.

---

### Question 7 — Qu'apporte la CI (GitHub Actions) ?

La CI (Continuous Integration) automatise la vérification du pipeline à chaque modification du code poussée sur GitHub. Sans CI, les erreurs ne sont détectées que lors de la prochaine exécution manuelle, potentiellement longtemps après leur introduction.

Dans ce projet, la CI (`ci.yml`) effectue automatiquement :
1. Installation d'un environnement Python propre (depuis zéro, sans cache résiduel)
2. Installation des dépendances depuis `requirements.txt`
3. Vérification syntaxique des scripts Python
4. Vérification de la présence de tous les fichiers requis
5. Exécution complète du pipeline : ingestion → validation → `dbt run` → `dbt test`

La CI garantit que :
- Le pipeline fonctionne sur une machine vierge (pas uniquement sur le poste du développeur)
- Toute régression est détectée dans les minutes suivant le commit
- Le feedback est rapide et précis (quelle étape a échoué, pourquoi)
- La qualité du code est maintenue avant toute fusion dans la branche principale

---

### Question 8 — Que manque-t-il encore pour un pipeline pleinement industrialisé ?

Le pipeline construit dans ce TP est un bon point de départ, mais plusieurs éléments seraient nécessaires pour atteindre un niveau pleinement industrialisé :

**1. Versionnement des données (DVC)**
Les données CSV et la base DuckDB ne sont pas versionnées dans Git (fichiers exclus par `.gitignore`). DVC permettrait de lier chaque version du code à la version exacte des données utilisées, garantissant une reproductibilité totale.

**2. Entraînement de modèle et MLflow**
Le pipeline actuel s'arrête à la transformation des données. Un pipeline MLOps complet intégrerait l'entraînement du modèle de scoring, le suivi des expériences (hyperparamètres, métriques) via MLflow ou DVC, et l'enregistrement du modèle dans un model registry.

**3. Déploiement et CD (Continuous Deployment)**
La CI actuelle vérifie le pipeline mais ne déploie rien. Un pipeline industrialisé inclurait le déploiement automatique du modèle (ex. via une API FastAPI ou Flask) après validation des tests.

**4. Monitoring en production**
Une fois en production, il faut surveiller la dérive des données (data drift) et la dérive du modèle (model drift), et déclencher automatiquement un réentraînement si les performances se dégradent.

**5. Infrastructure as Code**
L'environnement d'exécution (serveur, conteneurs Docker, ressources cloud) devrait être défini sous forme de code (Docker, Terraform) pour garantir la reproductibilité de l'infrastructure.

**6. Gestion des secrets et configurations**
Les accès aux bases de données, API et services cloud doivent être gérés via des variables d'environnement ou un gestionnaire de secrets (ex. HashiCorp Vault), et non codés en dur.

**7. Tests plus complets**
Des tests unitaires (pytest) sur les fonctions Python, des tests d'intégration end-to-end et des tests de régression sur les métriques du modèle renforceraient la robustesse du pipeline.

**8. Documentation et gouvernance**
Un catalogue de données, une documentation des modèles dbt, et une politique de gouvernance (qui peut modifier quoi, processus de review) sont indispensables dans un contexte d'équipe.

---

## Partie I — Analyses

### Analyse 1 — Système artisanal de notebooks

**1. Pourquoi ce système est-il artisanal ?**

Ce système est artisanal car il repose entièrement sur des interventions humaines manuelles et répétitives, sans aucune automatisation, standardisation ni traçabilité. Chaque exécution hebdomadaire dépend de la présence et de la vigilance d'un opérateur, le flux n'est pas reproductible entre personnes ou machines différentes, et aucun artefact de sortie n'est archivé de façon structurée. C'est l'opposé d'un pipeline industrialisé.

**2. Cinq risques identifiés**

- **Erreur humaine** : l'opérateur peut sauter une étape, exécuter les notebooks dans le mauvais ordre, ou utiliser un fichier CSV obsolète sans s'en rendre compte.
- **Non-reproductibilité** : les dépendances Python diffèrent selon les postes, ce qui signifie que le même script peut produire des résultats différents sur deux machines.
- **Perte de traçabilité** : sans versionnement des données ni des notebooks, il est impossible de retrouver quelle version des données a produit quel résultat la semaine N-3.
- **Fragilité de la chaîne de transmission** : l'envoi des résultats par email n'est ni archivé de façon structurée ni versionné ; un email perdu équivaut à une perte du résultat.
- **Absence de contrôle qualité** : aucune validation automatique ne détecte si les données source sont corrompues ou incomplètes avant l'entraînement du modèle.

**3. Premiers éléments de transformation**

- Mettre les notebooks sous Git et les convertir en scripts Python modulaires
- Créer un `requirements.txt` et un `venv` partagé pour normaliser l'environnement
- Versionner les fichiers CSV d'entrée (DVC ou naming convention avec dates)
- Automatiser l'enchaînement des scripts avec un orchestrateur (Dagster, Airflow)
- Stocker les résultats dans une base de données (DuckDB) plutôt que par email

---

### Analyse 2 — Fausse agilité

**1. Pourquoi cette organisation n'est-elle pas réellement Agile au sens DataOps ?**

L'agilité dans le sens DataOps ne se résume pas à tenir des réunions régulières. Elle implique des cycles courts de feedback basés sur des indicateurs mesurables, une collaboration effective via des outils partagés, et une capacité à détecter et corriger rapidement les problèmes. Ici, les erreurs sont découvertes tardivement (pas de CI, pas de tests automatisés), les changements ne sont pas tracés (pas de Git), chaque équipe travaille en silo (pas de partage de code ni de données), et il n'y a aucun mécanisme de feedback rapide. La réunion hebdomadaire est un rituel vide de sens sans les pratiques sous-jacentes.

**2. Principes du DataOps Manifesto manquants**

- "Add observability to data" : pas de monitoring, erreurs découvertes tardivement
- "Embrace change" / "Make changes the unit of work" : les changements ne sont pas tracés
- "Reuse" : les scripts ne sont pas mutualisés, chaque équipe recrée ses outils
- "Test quality into the pipeline" : absence de tests automatisés
- "Use version control" : aucun versionnement du code ou des données

**3. Changements de pratiques proposés**

- Adopter Git pour tous les scripts et configurations (versionnement + collaboration)
- Mettre en place des tests automatisés (dbt test, pytest) déclenchés à chaque commit
- Créer un dépôt de code partagé (GitHub, GitLab) pour mutualiser les scripts
- Introduire un orchestrateur pour rendre les dépendances et l'ordre d'exécution explicites
- Adopter des sprints data avec des objectifs mesurables et des revues basées sur des métriques réelles

---

### Analyse 3 — Problème de reproductibilité

**1. Trois causes possibles de résultats distincts**

- **Versions de bibliothèques différentes** : pandas 1.x et pandas 2.x ne gèrent pas certains types de données de la même façon ; scikit-learn peut introduire de légères variations numériques entre versions.
- **Graine aléatoire (random seed) non fixée** : si le script utilise des algorithmes probabilistes (forêt aléatoire, initialisation K-Means) sans fixer la graine (`random_state`), les résultats varient à chaque exécution.
- **Données d'entrée différentes** : les deux étudiants utilisent peut-être des versions différentes du fichier CSV (l'un a une version mise à jour, l'autre non) sans que ce soit apparent.

**2. En quoi cela relève d'un problème de reproductibilité ?**

La reproductibilité exige qu'un même code, appliqué aux mêmes données, dans le même environnement, produise toujours le même résultat. Ici, deux des trois piliers sont défaillants : l'environnement (bibliothèques) et/ou les données ne sont pas identiques. C'est un problème fondamental en MLOps car il rend impossible la comparaison objective de deux exécutions, l'audit des résultats et la validation par un tiers.

**3. Mesures techniques pour réduire ce problème**

- **Épingler les versions** dans `requirements.txt` (`pandas==2.1.0`, `scikit-learn==1.3.0`) et utiliser le même `venv`
- **Fixer les graines aléatoires** dans tous les scripts (`random_state=42` pour scikit-learn, `np.random.seed(42)` pour NumPy)
- **Versionner les données** avec DVC ou un naming convention strict, pour garantir que tout le monde utilise exactement le même fichier source
- **Utiliser Docker** pour encapsuler l'environnement complet (OS, Python, bibliothèques) dans une image immuable
