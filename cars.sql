-- psql -U username -d cars -f cars.sql
-- Création de la table pour stocker le XML des voitures
CREATE TABLE cars_data (
    id SERIAL PRIMARY KEY,  -- Identifiant unique pour chaque entrée
    data XML NOT NULL       -- Le champ pour stocker les données XML (données des voitures)
);
