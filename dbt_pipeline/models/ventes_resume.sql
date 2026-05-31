-- dbt_pipeline/models/ventes_resume.sql
-- --------------------------------------
-- Modèle 2 : Agrégation par région et par mois.
-- Dépend de ventes_clean (les données nettoyées).
-- Produit : total des ventes, nombre de transactions, panier moyen.

{{ config(materialized='view') }}

SELECT
    region,
    annee_mois,
    COUNT(*)              AS nb_transactions,
    ROUND(SUM(montant), 2) AS total_ventes,
    ROUND(AVG(montant), 2) AS panier_moyen
FROM {{ ref('ventes_clean') }}
GROUP BY
    region,
    annee_mois
ORDER BY
    annee_mois,
    region
