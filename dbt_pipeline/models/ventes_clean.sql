-- dbt_pipeline/models/ventes_clean.sql
-- ------------------------------------
-- Modèle 1 : Nettoyage des données brutes.
-- - Filtre les lignes avec montant NULL ou <= 0 (statut = 'invalide')
-- - Cast des types pour garantir la cohérence
-- - Ajoute une colonne annee_mois pour faciliter les agrégations

{{ config(materialized='view') }}

SELECT
    CAST(id_client AS INTEGER) AS id_client,
    CAST(nom       AS VARCHAR) AS nom,
    CAST(montant   AS DOUBLE)  AS montant,
    date_vente,
    CAST(region    AS VARCHAR) AS region,
    CAST(statut    AS VARCHAR) AS statut,
    STRFTIME(STRPTIME(CAST(date_vente AS VARCHAR), '%d/%m/%Y'), '%Y-%m') AS annee_mois
FROM raw.ventes
WHERE
    montant IS NOT NULL
    AND CAST(montant AS DOUBLE) > 0
    AND statut = 'valide'