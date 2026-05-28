-- ============================================================
-- ESQUEMA ACTUALIZADO — torneos_deportivos_db
-- Nuevo diseño con tablas: Deporte, Torneo, Equipo, Jugador,
-- Cancha, Condicion, Partido, Partido_Equipo, Resultado
-- Ejecutar en el SQL Editor de Neon.tech
-- ============================================================

CREATE TABLE Deporte (
    id_deporte SERIAL PRIMARY KEY,
    nombre_deporte VARCHAR(50) NOT NULL,
    reglas TEXT
);

CREATE TABLE Torneo (
    id_torneo SERIAL PRIMARY KEY,
    nombre_torneo VARCHAR(100) NOT NULL,
    fecha_inicio DATE,
    numero_equipos INT,
    id_deporte INT,
    FOREIGN KEY (id_deporte) REFERENCES Deporte(id_deporte)
);

CREATE TABLE Equipo (
    id_equipo SERIAL PRIMARY KEY,
    nombre_equipo VARCHAR(100) NOT NULL,
    numero_jugadores INT,
    id_torneo INT,
    FOREIGN KEY (id_torneo) REFERENCES Torneo(id_torneo)
);

CREATE TABLE Jugador (
    id_jugador SERIAL PRIMARY KEY,
    nombre_jugador VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NOT NULL,
    DNI VARCHAR(15) UNIQUE NOT NULL,
    id_equipo INT,
    FOREIGN KEY (id_equipo) REFERENCES Equipo(id_equipo)
);

CREATE TABLE Cancha (
    id_cancha SERIAL PRIMARY KEY,
    nombre_cancha VARCHAR(50) NOT NULL,
    tipo VARCHAR(30)
);

CREATE TABLE Condicion (
    id_condicion SERIAL PRIMARY KEY,
    nombre_condicion VARCHAR(20) NOT NULL
);

CREATE TABLE Partido (
    id_partido SERIAL PRIMARY KEY,
    fecha DATE,
    hora TIME,
    estado VARCHAR(20),
    id_cancha INT,
    id_torneo INT,
    FOREIGN KEY (id_cancha) REFERENCES Cancha(id_cancha),
    FOREIGN KEY (id_torneo) REFERENCES Torneo(id_torneo)
);

CREATE TABLE Partido_Equipo (
    id_partido_equipo SERIAL PRIMARY KEY,
    id_partido INT,
    id_equipo INT,
    id_condicion INT,
    FOREIGN KEY (id_partido) REFERENCES Partido(id_partido),
    FOREIGN KEY (id_equipo) REFERENCES Equipo(id_equipo),
    FOREIGN KEY (id_condicion) REFERENCES Condicion(id_condicion)
);

CREATE TABLE Resultado (
    id_resultado SERIAL PRIMARY KEY,
    puntaje INT,
    id_partido_equipo INT,
    FOREIGN KEY (id_partido_equipo) REFERENCES Partido_Equipo(id_partido_equipo)
);

-- ============================================================
-- DATOS DE PRUEBA
-- ============================================================

INSERT INTO Deporte (nombre_deporte, reglas) VALUES 
('Vóley', 'Partidos a 3 sets de 25 puntos cada uno.'),
('Fútbol', 'Partidos de dos tiempos de 25 minutos, 7 vs 7.');

INSERT INTO Torneo (nombre_torneo, fecha_inicio, numero_equipos, id_deporte) VALUES 
('Torneo Clausura Vóley', '2026-06-01', 10, 1),
('Copa Relámpago Fútbol 7', '2026-06-05', 2, 2);

INSERT INTO Equipo (nombre_equipo, numero_jugadores, id_torneo) VALUES 
('Vóley Club Amazonas', 7, 1), ('Net Masters', 7, 1), ('Spike Force', 7, 1),
('Saitama Vóley', 7, 1), ('Inkas Vóley', 7, 1), ('Titanes de la Red', 7, 1),
('Pumas Vóley', 7, 1), ('Sky Jumpers', 7, 1), ('Halcones Dorados', 7, 1), ('Punto de Oro', 7, 1),
('Real CanchaLibre FC', 7, 2), ('Sporting Norte', 7, 2);

INSERT INTO Jugador (nombre_jugador, apellido_paterno, apellido_materno, DNI, id_equipo) VALUES
('Ana','Gomez','Flores','10000001',1),('Maria','Diaz','Ruiz','10000002',1),('Lucia','Perez','Soto','10000003',1),('Elena','Castro','Vega','10000004',1),('Sofia','Ramos','Luna','10000005',1),('Laura','Torres','Mora','10000006',1),('Paula','Vargas','Rios','10000007',1),
('Camila','Silva','Cruz','10000008',2),('Valeria','Reyes','Mejia','10000009',2),('Andrea','Mendoza','Alva','10000010',2),('Natalia','Espinoza','Peña','10000011',2),('Daniela','Benitez','León','10000012',2),('Gabriela','Cabrera','Solis','10000013',2),('Claudia','Nuñez','Campos','10000014',2),
('Fiorella','Flores','Quispe','10000015',3),('Diana','Guerra','Rojas','10000016',3),('Estefani','Vidal','Suarez','10000017',3),('Karla','Paredes','Zevallos','10000018',3),('Alejandra','Salazar','Chavez','10000019',3),('Vanessa','Miranda','Villanueva','10000020',3),('Monica','Caceres','Palomino','10000021',3),
('Roxana','Cordova','Delgado','10000022',4),('Juliana','Navarro','Gutierrez','10000023',4),('Tatiana','Arias','Ortega','10000024',4),('Patricia','Acosta','Romero','10000025',4),('Isabel','Morales','Pinedo','10000026',4),('Beatriz','Herrera','Medina','10000027',4),('Alicia','Dominguez','Guerrero','10000028',4),
('Jimena','Jimenez','Echevarria','10000029',5),('Adriana','Blanco','Marin','10000030',5),('Melina','Ortega','Garrido','10000031',5),('Silvia','Serrano','Crespo','10000032',5),('Yolanda','Molina','Alonso','10000033',5),('Olga','Vazquez','Delgado','10000034',5),('Irene','Suarez','Ortiz','10000035',5),
('Nadia','Castillo','Rubio','10000036',6),('Cecilia','Ortiz','Santos','10000037',6),('Lorena','Garrido','Lozano','10000038',6),('Fabiola','Lozano','Pena','10000039',6),('Gisela','Calvo','Vidal','10000040',6),('Marta','Rubio','Medina','10000041',6),('Gloria','Marquez','Cano','10000042',6),
('Angeles','Rey','Acevedo','10000043',7),('Susana','Cano','Benitez','10000044',7),('Milagros','Bravo','Vicente','10000045',7),('Noelia','Merino','Sanz','10000046',7),('Jessica','Sanz','Lara','10000047',7),('Veronica','Lara','Soler','10000048',7),('Rebeca','Soler','Franco','10000049',7),
('Estela','Franco','Ramos','10000050',8),('Clara','Ramos','Ochoa','10000051',8),('Zoe','Ochoa','Maza','10000052',8),('Alba','Maza','Lowe','10000053',8),('Ruth','Lowe','Guzman','10000054',8),('Miriam','Guzman','Bello','10000055',8),('Sara','Bello','Arce','10000056',8),
('Iris','Arce','Tello','10000057',9),('Judith','Tello','Pinto','10000058',9),('Leonor','Pinto','Valle','10000059',9),('Lidia','Valle','Bermudez','10000060',9),('Cynthia','Bermudez','Tapia','10000061',9),('Erika','Tapia','Sosa','10000062',9),('Sonia','Sosa','Gomez','10000063',9),
('Alicia','Chavez','Farfan','10000064',10),('Blanca','Palacios','Ugarte','10000065',10),('Carolina','Velasquez','Quispe','10000066',10),('Esperanza','Prado','Heredia','10000067',10),('Esther','Zuniga','Guerra','10000068',10),('Luz','Vilchez','Malca','10000069',10),('Mercedes','Camino','Borda','10000070',10),
('Juan','Perez','Quispe','20000001',11),('Carlos','Lopez','Mendoza','20000002',11),('Luis','Garcia','Rojas','20000003',11),('Pedro','Martinez','Soto','20000004',11),('Jorge','Rodriguez','Flores','20000005',11),('Raul','Sanchez','Benitez','20000006',11),('Miguel','Ramirez','Castillo','20000007',11),
('Andres','Torres','Espinoza','20000008',12),('Kevin','Flores','Gomez','20000009',12),('Diego','Morales','Castro','20000010',12),('Renzo','Vargas','Ruiz','20000011',12),('Christian','Ramos','Vega','20000012',12),('Oscar','Mendoza','Luna','20000013',12),('Walter','Solis','Torres','20000014',12);

INSERT INTO Cancha (nombre_cancha, tipo) VALUES 
('Cancha Coliseo Azul', 'Vóley'),
('Estadio Sintético Central', 'Fútbol 7');

INSERT INTO Condicion (nombre_condicion) VALUES 
('Local'), 
('Visitante');

INSERT INTO Partido (fecha, hora, estado, id_cancha, id_torneo) VALUES 
('2026-06-10', '19:00:00', 'Finalizado', 2, 2);

INSERT INTO Partido_Equipo (id_partido, id_equipo, id_condicion) VALUES 
(1, 11, 1),
(1, 12, 2);

INSERT INTO Resultado (puntaje, id_partido_equipo) VALUES 
(3, 1),
(1, 2);
