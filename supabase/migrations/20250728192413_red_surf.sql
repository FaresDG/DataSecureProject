-- Script d'initialisation de la base de données

-- Créer la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS school_intranet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE school_intranet;

-- Grant privileges
GRANT ALL PRIVILEGES ON school_intranet.* TO 'appuser'@'%';
FLUSH PRIVILEGES;