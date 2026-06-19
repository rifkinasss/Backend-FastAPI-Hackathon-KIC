CREATE DATABASE iot_fuzzy_kideco

CREATE TABLE tb_debu_tambang (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    waktu DATETIME NOT NULL,
    sensor_id VARCHAR(20) NOT NULL,
    lokasi VARCHAR(100) NOT NULL,
    pm25 FLOAT NOT NULL COMMENT 'µg/m³',
    pm10 FLOAT NOT NULL COMMENT 'µg/m³',
    suhu FLOAT NOT NULL COMMENT '°C',
    kelembaban FLOAT NOT NULL COMMENT '%RH',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_sensor_waktu (sensor_id, waktu),
    INDEX idx_waktu (waktu)
);

CREATE TABLE tb_emisi_alat_berat (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    waktu DATETIME NOT NULL,
    sensor_id VARCHAR(20) NOT NULL,
    lokasi VARCHAR(100) NOT NULL,
    
    co FLOAT NOT NULL COMMENT 'ppm',
    co2 FLOAT NOT NULL COMMENT 'ppm',
    suhu FLOAT NOT NULL COMMENT '°C',
    kelembaban FLOAT NOT NULL COMMENT '%RH',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_waktu (waktu),
    INDEX idx_sensor (sensor_id),
    INDEX idx_lokasi (lokasi),
    INDEX idx_sensor_waktu (sensor_id, waktu)
);

CREATE TABLE tb_gas_tambang (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    waktu DATETIME NOT NULL,
    sensor_id VARCHAR(20) NOT NULL,
    lokasi VARCHAR(100) NOT NULL,
    
    ch4 FLOAT NOT NULL COMMENT 'Persen (% Volume)',
    h2s FLOAT NOT NULL COMMENT 'ppm',
    suhu FLOAT NOT NULL COMMENT '°C',
    kelembaban FLOAT NOT NULL COMMENT '%RH',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_waktu (waktu),
    INDEX idx_sensor (sensor_id),
    INDEX idx_lokasi (lokasi),
    INDEX idx_sensor_waktu (sensor_id, waktu)
);



INSERT INTO tb_debu_tambang
(waktu, sensor_id, lokasi, pm25, pm10, suhu, kelembaban)
VALUES
('2026-06-05 08:00:00','DB001','Jalan Tambang A',35,82,31.5,72),
('2026-06-05 08:05:00','DB001','Jalan Tambang A',38,90,31.7,71),
('2026-06-05 08:10:00','DB001','Jalan Tambang A',42,98,31.9,71),
('2026-06-05 08:15:00','DB001','Jalan Tambang A',47,108,32.2,70),
('2026-06-05 08:20:00','DB001','Jalan Tambang A',53,120,32.6,69),
('2026-06-05 08:25:00','DB001','Jalan Tambang A',58,128,32.9,68),
('2026-06-05 08:30:00','DB001','Jalan Tambang A',62,136,33.1,67),
('2026-06-05 08:35:00','DB001','Jalan Tambang A',68,148,33.4,66),
('2026-06-05 08:40:00','DB001','Jalan Tambang A',73,158,33.7,65),
('2026-06-05 08:45:00','DB001','Jalan Tambang A',77,166,34.0,64),

('2026-06-05 08:50:00','DB001','Jalan Tambang A',72,155,33.8,65),
('2026-06-05 08:55:00','DB001','Jalan Tambang A',66,142,33.5,66),
('2026-06-05 09:00:00','DB001','Jalan Tambang A',61,132,33.2,67),
('2026-06-05 09:05:00','DB001','Jalan Tambang A',55,122,32.9,68),
('2026-06-05 09:10:00','DB001','Jalan Tambang A',50,114,32.6,69),
('2026-06-05 09:15:00','DB001','Jalan Tambang A',45,105,32.3,70),
('2026-06-05 09:20:00','DB001','Jalan Tambang A',41,96,32.0,71),
('2026-06-05 09:25:00','DB001','Jalan Tambang A',38,89,31.8,72),
('2026-06-05 09:30:00','DB001','Jalan Tambang A',36,84,31.7,72),
('2026-06-05 09:35:00','DB001','Jalan Tambang A',40,92,31.9,71),

('2026-06-05 09:40:00','DB001','Jalan Tambang A',46,104,32.2,70),
('2026-06-05 09:45:00','DB001','Jalan Tambang A',54,118,32.6,69),
('2026-06-05 09:50:00','DB001','Jalan Tambang A',63,136,33.0,68),
('2026-06-05 09:55:00','DB001','Jalan Tambang A',72,154,33.4,66),
('2026-06-05 10:00:00','DB001','Jalan Tambang A',81,172,33.8,65),
('2026-06-05 10:05:00','DB001','Jalan Tambang A',88,185,34.1,64),
('2026-06-05 10:10:00','DB001','Jalan Tambang A',93,196,34.4,63),
('2026-06-05 10:15:00','DB001','Jalan Tambang A',98,205,34.7,62),
('2026-06-05 10:20:00','DB001','Jalan Tambang A',102,214,35.0,61),
('2026-06-05 10:25:00','DB001','Jalan Tambang A',97,202,34.8,62),

('2026-06-05 10:30:00','DB001','Jalan Tambang A',90,188,34.5,63),
('2026-06-05 10:35:00','DB001','Jalan Tambang A',84,176,34.2,64),
('2026-06-05 10:40:00','DB001','Jalan Tambang A',77,162,33.9,65),
('2026-06-05 10:45:00','DB001','Jalan Tambang A',70,150,33.6,66),
('2026-06-05 10:50:00','DB001','Jalan Tambang A',63,138,33.2,67),
('2026-06-05 10:55:00','DB001','Jalan Tambang A',57,126,32.9,68),
('2026-06-05 11:00:00','DB001','Jalan Tambang A',51,116,32.6,69),
('2026-06-05 11:05:00','DB001','Jalan Tambang A',46,107,32.3,70),
('2026-06-05 11:10:00','DB001','Jalan Tambang A',42,98,32.0,71),
('2026-06-05 11:15:00','DB001','Jalan Tambang A',39,90,31.8,72),

('2026-06-05 11:20:00','DB001','Jalan Tambang A',44,101,32.1,71),
('2026-06-05 11:25:00','DB001','Jalan Tambang A',52,115,32.5,69),
('2026-06-05 11:30:00','DB001','Jalan Tambang A',61,132,32.9,68),
('2026-06-05 11:35:00','DB001','Jalan Tambang A',70,149,33.3,67),
('2026-06-05 11:40:00','DB001','Jalan Tambang A',78,166,33.7,65),
('2026-06-05 11:45:00','DB001','Jalan Tambang A',85,180,34.0,64),
('2026-06-05 11:50:00','DB001','Jalan Tambang A',79,170,33.8,65),
('2026-06-05 11:55:00','DB001','Jalan Tambang A',71,154,33.5,66),
('2026-06-05 12:00:00','DB001','Jalan Tambang A',63,138,33.1,67),
('2026-06-05 12:05:00','DB001','Jalan Tambang A',56,124,32.8,68);

INSERT INTO tb_emisi_alat_berat
(waktu, sensor_id, lokasi, co, co2, suhu, kelembaban)
VALUES
('2026-06-05 08:00:00','EM001','Bengkel Alat Berat',12,680,33.5,73),
('2026-06-05 08:05:00','EM001','Bengkel Alat Berat',14,720,33.8,72),
('2026-06-05 08:10:00','EM001','Bengkel Alat Berat',17,770,34.1,71),
('2026-06-05 08:15:00','EM001','Bengkel Alat Berat',20,830,34.5,70),
('2026-06-05 08:20:00','EM001','Bengkel Alat Berat',24,900,34.9,69),
('2026-06-05 08:25:00','EM001','Bengkel Alat Berat',28,980,35.3,68),
('2026-06-05 08:30:00','EM001','Bengkel Alat Berat',33,1080,35.8,67),
('2026-06-05 08:35:00','EM001','Bengkel Alat Berat',38,1180,36.2,66),
('2026-06-05 08:40:00','EM001','Bengkel Alat Berat',42,1270,36.5,65),
('2026-06-05 08:45:00','EM001','Bengkel Alat Berat',46,1360,36.8,64),

('2026-06-05 08:50:00','EM001','Bengkel Alat Berat',43,1280,36.6,65),
('2026-06-05 08:55:00','EM001','Bengkel Alat Berat',39,1190,36.2,66),
('2026-06-05 09:00:00','EM001','Bengkel Alat Berat',34,1080,35.8,67),
('2026-06-05 09:05:00','EM001','Bengkel Alat Berat',29,990,35.4,68),
('2026-06-05 09:10:00','EM001','Bengkel Alat Berat',25,910,35.0,69),
('2026-06-05 09:15:00','EM001','Bengkel Alat Berat',21,840,34.6,70),
('2026-06-05 09:20:00','EM001','Bengkel Alat Berat',18,780,34.3,71),
('2026-06-05 09:25:00','EM001','Bengkel Alat Berat',15,730,34.0,72),
('2026-06-05 09:30:00','EM001','Bengkel Alat Berat',13,690,33.8,72),
('2026-06-05 09:35:00','EM001','Bengkel Alat Berat',16,750,34.1,71),

('2026-06-05 09:40:00','EM001','Bengkel Alat Berat',20,830,34.5,70),
('2026-06-05 09:45:00','EM001','Bengkel Alat Berat',25,930,35.0,69),
('2026-06-05 09:50:00','EM001','Bengkel Alat Berat',31,1050,35.5,68),
('2026-06-05 09:55:00','EM001','Bengkel Alat Berat',37,1170,36.0,67),
('2026-06-05 10:00:00','EM001','Bengkel Alat Berat',43,1290,36.4,66),
('2026-06-05 10:05:00','EM001','Bengkel Alat Berat',48,1400,36.8,65),
('2026-06-05 10:10:00','EM001','Bengkel Alat Berat',53,1520,37.2,64),
('2026-06-05 10:15:00','EM001','Bengkel Alat Berat',57,1620,37.5,63),
('2026-06-05 10:20:00','EM001','Bengkel Alat Berat',60,1700,37.8,62),
('2026-06-05 10:25:00','EM001','Bengkel Alat Berat',55,1580,37.4,63),

('2026-06-05 10:30:00','EM001','Bengkel Alat Berat',49,1450,37.0,64),
('2026-06-05 10:35:00','EM001','Bengkel Alat Berat',43,1320,36.5,65),
('2026-06-05 10:40:00','EM001','Bengkel Alat Berat',38,1210,36.1,66),
('2026-06-05 10:45:00','EM001','Bengkel Alat Berat',32,1090,35.7,67),
('2026-06-05 10:50:00','EM001','Bengkel Alat Berat',27,980,35.3,68),
('2026-06-05 10:55:00','EM001','Bengkel Alat Berat',22,890,34.9,69),
('2026-06-05 11:00:00','EM001','Bengkel Alat Berat',18,810,34.5,70),
('2026-06-05 11:05:00','EM001','Bengkel Alat Berat',15,740,34.1,71),
('2026-06-05 11:10:00','EM001','Bengkel Alat Berat',13,700,33.9,72),
('2026-06-05 11:15:00','EM001','Bengkel Alat Berat',17,780,34.2,71),

('2026-06-05 11:20:00','EM001','Bengkel Alat Berat',23,900,34.8,70),
('2026-06-05 11:25:00','EM001','Bengkel Alat Berat',30,1040,35.4,68),
('2026-06-05 11:30:00','EM001','Bengkel Alat Berat',38,1200,36.0,67),
('2026-06-05 11:35:00','EM001','Bengkel Alat Berat',46,1360,36.6,65),
('2026-06-05 11:40:00','EM001','Bengkel Alat Berat',54,1530,37.1,64),
('2026-06-05 11:45:00','EM001','Bengkel Alat Berat',59,1660,37.6,63),
('2026-06-05 11:50:00','EM001','Bengkel Alat Berat',52,1500,37.1,64),
('2026-06-05 11:55:00','EM001','Bengkel Alat Berat',44,1320,36.5,65),
('2026-06-05 12:00:00','EM001','Bengkel Alat Berat',35,1140,35.9,67),
('2026-06-05 12:05:00','EM001','Bengkel Alat Berat',27,980,35.2,68);

INSERT INTO tb_gas_tambang
(waktu, sensor_id, lokasi, ch4, h2s, suhu, kelembaban)
VALUES
('2026-06-05 08:00:00','GS001','Area Dasar Tambang',0.4,2,30.8,78),
('2026-06-05 08:05:00','GS001','Area Dasar Tambang',0.5,3,31.0,78),
('2026-06-05 08:10:00','GS001','Area Dasar Tambang',0.7,4,31.2,77),
('2026-06-05 08:15:00','GS001','Area Dasar Tambang',0.9,6,31.4,76),
('2026-06-05 08:20:00','GS001','Area Dasar Tambang',1.1,8,31.6,75),
('2026-06-05 08:25:00','GS001','Area Dasar Tambang',1.4,11,31.9,74),
('2026-06-05 08:30:00','GS001','Area Dasar Tambang',1.7,14,32.2,73),
('2026-06-05 08:35:00','GS001','Area Dasar Tambang',2.0,18,32.5,72),
('2026-06-05 08:40:00','GS001','Area Dasar Tambang',2.3,22,32.8,71),
('2026-06-05 08:45:00','GS001','Area Dasar Tambang',2.6,26,33.1,70),

('2026-06-05 08:50:00','GS001','Area Dasar Tambang',2.3,21,32.8,71),
('2026-06-05 08:55:00','GS001','Area Dasar Tambang',2.0,18,32.5,72),
('2026-06-05 09:00:00','GS001','Area Dasar Tambang',1.7,15,32.2,73),
('2026-06-05 09:05:00','GS001','Area Dasar Tambang',1.4,12,31.9,74),
('2026-06-05 09:10:00','GS001','Area Dasar Tambang',1.1,9,31.6,75),
('2026-06-05 09:15:00','GS001','Area Dasar Tambang',0.9,7,31.4,76),
('2026-06-05 09:20:00','GS001','Area Dasar Tambang',0.7,5,31.2,77),
('2026-06-05 09:25:00','GS001','Area Dasar Tambang',0.6,4,31.1,78),
('2026-06-05 09:30:00','GS001','Area Dasar Tambang',0.5,3,31.0,78),
('2026-06-05 09:35:00','GS001','Area Dasar Tambang',0.8,5,31.2,77),

('2026-06-05 09:40:00','GS001','Area Dasar Tambang',1.2,9,31.6,75),
('2026-06-05 09:45:00','GS001','Area Dasar Tambang',1.6,13,32.0,74),
('2026-06-05 09:50:00','GS001','Area Dasar Tambang',2.0,18,32.4,73),
('2026-06-05 09:55:00','GS001','Area Dasar Tambang',2.5,24,32.9,71),
('2026-06-05 10:00:00','GS001','Area Dasar Tambang',3.0,31,33.4,70),
('2026-06-05 10:05:00','GS001','Area Dasar Tambang',3.5,38,33.8,69),
('2026-06-05 10:10:00','GS001','Area Dasar Tambang',4.0,45,34.2,68),
('2026-06-05 10:15:00','GS001','Area Dasar Tambang',4.4,52,34.6,67),
('2026-06-05 10:20:00','GS001','Area Dasar Tambang',4.8,58,35.0,66),
('2026-06-05 10:25:00','GS001','Area Dasar Tambang',4.3,50,34.7,67),

('2026-06-05 10:30:00','GS001','Area Dasar Tambang',3.8,42,34.3,68),
('2026-06-05 10:35:00','GS001','Area Dasar Tambang',3.3,35,33.9,69),
('2026-06-05 10:40:00','GS001','Area Dasar Tambang',2.8,28,33.5,70),
('2026-06-05 10:45:00','GS001','Area Dasar Tambang',2.3,22,33.1,71),
('2026-06-05 10:50:00','GS001','Area Dasar Tambang',1.8,16,32.7,72),
('2026-06-05 10:55:00','GS001','Area Dasar Tambang',1.4,11,32.3,73),
('2026-06-05 11:00:00','GS001','Area Dasar Tambang',1.0,7,31.9,74),
('2026-06-05 11:05:00','GS001','Area Dasar Tambang',0.8,5,31.6,75),
('2026-06-05 11:10:00','GS001','Area Dasar Tambang',0.6,4,31.3,76),
('2026-06-05 11:15:00','GS001','Area Dasar Tambang',1.0,8,31.7,75),

('2026-06-05 11:20:00','GS001','Area Dasar Tambang',1.5,13,32.1,74),
('2026-06-05 11:25:00','GS001','Area Dasar Tambang',2.1,20,32.6,72),
('2026-06-05 11:30:00','GS001','Area Dasar Tambang',2.8,29,33.1,71),
('2026-06-05 11:35:00','GS001','Area Dasar Tambang',3.6,40,33.7,69),
('2026-06-05 11:40:00','GS001','Area Dasar Tambang',4.3,51,34.3,68),
('2026-06-05 11:45:00','GS001','Area Dasar Tambang',5.0,63,35.0,66),
('2026-06-05 11:50:00','GS001','Area Dasar Tambang',4.4,54,34.5,67),
('2026-06-05 11:55:00','GS001','Area Dasar Tambang',3.6,42,33.9,69),
('2026-06-05 12:00:00','GS001','Area Dasar Tambang',2.8,30,33.3,70),
('2026-06-05 12:05:00','GS001','Area Dasar Tambang',2.0,19,32.7,72);