-- Hacer backup de los datos existentes
CREATE TABLE postura_backup AS SELECT * FROM postura;

-- Eliminar la tabla actual
DROP TABLE postura;

-- Recrear la tabla con todas las columnas
CREATE TABLE postura (
    id_postura INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_es TEXT NOT NULL,
    nombre_sans TEXT,
    instrucciones TEXT,
    beneficios TEXT,
    precauciones TEXT,
    video TEXT,
    fotografia TEXT
);

-- Restaurar los datos del backup
INSERT INTO postura (id_postura, nombre_es, nombre_sans)
SELECT id_postura, nombre_es, nombre_sans FROM postura_backup;

-- Eliminar la tabla de backup
DROP TABLE postura_backup; 