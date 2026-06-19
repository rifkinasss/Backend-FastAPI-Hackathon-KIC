-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Jun 10, 2026 at 12:37 AM
-- Server version: 8.0.35
-- PHP Version: 8.2.20

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `iot_fuzzy_kideco`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_debu_tambang`
--

CREATE TABLE `tb_debu_tambang` (
  `id` bigint UNSIGNED NOT NULL,
  `waktu` datetime NOT NULL,
  `sensor_id` varchar(20) NOT NULL,
  `lokasi` varchar(100) NOT NULL,
  `pm25` float NOT NULL COMMENT 'µg/m³',
  `pm10` float NOT NULL COMMENT 'µg/m³',
  `suhu` float NOT NULL COMMENT '°C',
  `kelembaban` float NOT NULL COMMENT '%RH',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_debu_tambang`
--

INSERT INTO `tb_debu_tambang` (`id`, `waktu`, `sensor_id`, `lokasi`, `pm25`, `pm10`, `suhu`, `kelembaban`, `created_at`) VALUES
(101, '2026-06-05 08:00:00', 'DB001', 'Jalan Tambang A', 35, 82, 31.5, 72, '2026-06-08 03:28:15'),
(102, '2026-06-05 08:05:00', 'DB001', 'Jalan Tambang A', 38, 90, 31.7, 71, '2026-06-08 03:28:15'),
(103, '2026-06-05 08:10:00', 'DB001', 'Jalan Tambang A', 42, 98, 31.9, 71, '2026-06-08 03:28:15'),
(104, '2026-06-05 08:15:00', 'DB001', 'Jalan Tambang A', 47, 108, 32.2, 70, '2026-06-08 03:28:15'),
(105, '2026-06-05 08:20:00', 'DB001', 'Jalan Tambang A', 53, 120, 32.6, 69, '2026-06-08 03:28:15'),
(106, '2026-06-05 08:25:00', 'DB001', 'Jalan Tambang A', 58, 128, 32.9, 68, '2026-06-08 03:28:15'),
(107, '2026-06-05 08:30:00', 'DB001', 'Jalan Tambang A', 62, 136, 33.1, 67, '2026-06-08 03:28:15'),
(108, '2026-06-05 08:35:00', 'DB001', 'Jalan Tambang A', 68, 148, 33.4, 66, '2026-06-08 03:28:15'),
(109, '2026-06-05 08:40:00', 'DB001', 'Jalan Tambang A', 73, 158, 33.7, 65, '2026-06-08 03:28:15'),
(110, '2026-06-05 08:45:00', 'DB001', 'Jalan Tambang A', 77, 166, 34, 64, '2026-06-08 03:28:15'),
(111, '2026-06-05 08:50:00', 'DB001', 'Jalan Tambang A', 72, 155, 33.8, 65, '2026-06-08 03:28:15'),
(112, '2026-06-05 08:55:00', 'DB001', 'Jalan Tambang A', 66, 142, 33.5, 66, '2026-06-08 03:28:15'),
(113, '2026-06-05 09:00:00', 'DB001', 'Jalan Tambang A', 61, 132, 33.2, 67, '2026-06-08 03:28:15'),
(114, '2026-06-05 09:05:00', 'DB001', 'Jalan Tambang A', 55, 122, 32.9, 68, '2026-06-08 03:28:15'),
(115, '2026-06-05 09:10:00', 'DB001', 'Jalan Tambang A', 50, 114, 32.6, 69, '2026-06-08 03:28:15'),
(116, '2026-06-05 09:15:00', 'DB001', 'Jalan Tambang A', 45, 105, 32.3, 70, '2026-06-08 03:28:15'),
(117, '2026-06-05 09:20:00', 'DB001', 'Jalan Tambang A', 41, 96, 32, 71, '2026-06-08 03:28:15'),
(118, '2026-06-05 09:25:00', 'DB001', 'Jalan Tambang A', 38, 89, 31.8, 72, '2026-06-08 03:28:15'),
(119, '2026-06-05 09:30:00', 'DB001', 'Jalan Tambang A', 36, 84, 31.7, 72, '2026-06-08 03:28:15'),
(120, '2026-06-05 09:35:00', 'DB001', 'Jalan Tambang A', 40, 92, 31.9, 71, '2026-06-08 03:28:15'),
(121, '2026-06-05 09:40:00', 'DB001', 'Jalan Tambang A', 46, 104, 32.2, 70, '2026-06-08 03:28:15'),
(122, '2026-06-05 09:45:00', 'DB001', 'Jalan Tambang A', 54, 118, 32.6, 69, '2026-06-08 03:28:15'),
(123, '2026-06-05 09:50:00', 'DB001', 'Jalan Tambang A', 63, 136, 33, 68, '2026-06-08 03:28:15'),
(124, '2026-06-05 09:55:00', 'DB001', 'Jalan Tambang A', 72, 154, 33.4, 66, '2026-06-08 03:28:15'),
(125, '2026-06-05 10:00:00', 'DB001', 'Jalan Tambang A', 81, 172, 33.8, 65, '2026-06-08 03:28:15'),
(126, '2026-06-05 10:05:00', 'DB001', 'Jalan Tambang A', 88, 185, 34.1, 64, '2026-06-08 03:28:15'),
(127, '2026-06-05 10:10:00', 'DB001', 'Jalan Tambang A', 93, 196, 34.4, 63, '2026-06-08 03:28:15'),
(128, '2026-06-05 10:15:00', 'DB001', 'Jalan Tambang A', 98, 205, 34.7, 62, '2026-06-08 03:28:15'),
(129, '2026-06-05 10:20:00', 'DB001', 'Jalan Tambang A', 102, 214, 35, 61, '2026-06-08 03:28:15'),
(130, '2026-06-05 10:25:00', 'DB001', 'Jalan Tambang A', 97, 202, 34.8, 62, '2026-06-08 03:28:15'),
(131, '2026-06-05 10:30:00', 'DB001', 'Jalan Tambang A', 90, 188, 34.5, 63, '2026-06-08 03:28:15'),
(132, '2026-06-05 10:35:00', 'DB001', 'Jalan Tambang A', 84, 176, 34.2, 64, '2026-06-08 03:28:15'),
(133, '2026-06-05 10:40:00', 'DB001', 'Jalan Tambang A', 77, 162, 33.9, 65, '2026-06-08 03:28:15'),
(134, '2026-06-05 10:45:00', 'DB001', 'Jalan Tambang A', 70, 150, 33.6, 66, '2026-06-08 03:28:15'),
(135, '2026-06-05 10:50:00', 'DB001', 'Jalan Tambang A', 63, 138, 33.2, 67, '2026-06-08 03:28:15'),
(136, '2026-06-05 10:55:00', 'DB001', 'Jalan Tambang A', 57, 126, 32.9, 68, '2026-06-08 03:28:15'),
(137, '2026-06-05 11:00:00', 'DB001', 'Jalan Tambang A', 51, 116, 32.6, 69, '2026-06-08 03:28:15'),
(138, '2026-06-05 11:05:00', 'DB001', 'Jalan Tambang A', 46, 107, 32.3, 70, '2026-06-08 03:28:15'),
(139, '2026-06-05 11:10:00', 'DB001', 'Jalan Tambang A', 42, 98, 32, 71, '2026-06-08 03:28:15'),
(140, '2026-06-05 11:15:00', 'DB001', 'Jalan Tambang A', 39, 90, 31.8, 72, '2026-06-08 03:28:15'),
(141, '2026-06-05 11:20:00', 'DB001', 'Jalan Tambang A', 44, 101, 32.1, 71, '2026-06-08 03:28:15'),
(142, '2026-06-05 11:25:00', 'DB001', 'Jalan Tambang A', 52, 115, 32.5, 69, '2026-06-08 03:28:15'),
(143, '2026-06-05 11:30:00', 'DB001', 'Jalan Tambang A', 61, 132, 32.9, 68, '2026-06-08 03:28:15'),
(144, '2026-06-05 11:35:00', 'DB001', 'Jalan Tambang A', 70, 149, 33.3, 67, '2026-06-08 03:28:15'),
(145, '2026-06-05 11:40:00', 'DB001', 'Jalan Tambang A', 78, 166, 33.7, 65, '2026-06-08 03:28:15'),
(146, '2026-06-05 11:45:00', 'DB001', 'Jalan Tambang A', 85, 180, 34, 64, '2026-06-08 03:28:15'),
(147, '2026-06-05 11:50:00', 'DB001', 'Jalan Tambang A', 79, 170, 33.8, 65, '2026-06-08 03:28:15'),
(148, '2026-06-05 11:55:00', 'DB001', 'Jalan Tambang A', 71, 154, 33.5, 66, '2026-06-08 03:28:15'),
(149, '2026-06-05 12:00:00', 'DB001', 'Jalan Tambang A', 63, 138, 33.1, 67, '2026-06-08 03:28:15'),
(150, '2026-06-05 12:05:00', 'DB001', 'Jalan Tambang A', 56, 124, 32.8, 68, '2026-06-08 03:28:15');

-- --------------------------------------------------------

--
-- Table structure for table `tb_emisi_alat_berat`
--

CREATE TABLE `tb_emisi_alat_berat` (
  `id` bigint UNSIGNED NOT NULL,
  `waktu` datetime NOT NULL,
  `sensor_id` varchar(20) NOT NULL,
  `lokasi` varchar(100) NOT NULL,
  `co` float NOT NULL COMMENT 'ppm',
  `co2` float NOT NULL COMMENT 'ppm',
  `suhu` float NOT NULL COMMENT '°C',
  `kelembaban` float NOT NULL COMMENT '%RH',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_emisi_alat_berat`
--

INSERT INTO `tb_emisi_alat_berat` (`id`, `waktu`, `sensor_id`, `lokasi`, `co`, `co2`, `suhu`, `kelembaban`, `created_at`) VALUES
(101, '2026-06-05 08:00:00', 'EM001', 'Bengkel Alat Berat', 12, 680, 33.5, 73, '2026-06-08 03:28:15'),
(102, '2026-06-05 08:05:00', 'EM001', 'Bengkel Alat Berat', 14, 720, 33.8, 72, '2026-06-08 03:28:15'),
(103, '2026-06-05 08:10:00', 'EM001', 'Bengkel Alat Berat', 17, 770, 34.1, 71, '2026-06-08 03:28:15'),
(104, '2026-06-05 08:15:00', 'EM001', 'Bengkel Alat Berat', 20, 830, 34.5, 70, '2026-06-08 03:28:15'),
(105, '2026-06-05 08:20:00', 'EM001', 'Bengkel Alat Berat', 24, 900, 34.9, 69, '2026-06-08 03:28:15'),
(106, '2026-06-05 08:25:00', 'EM001', 'Bengkel Alat Berat', 28, 980, 35.3, 68, '2026-06-08 03:28:15'),
(107, '2026-06-05 08:30:00', 'EM001', 'Bengkel Alat Berat', 33, 1080, 35.8, 67, '2026-06-08 03:28:15'),
(108, '2026-06-05 08:35:00', 'EM001', 'Bengkel Alat Berat', 38, 1180, 36.2, 66, '2026-06-08 03:28:15'),
(109, '2026-06-05 08:40:00', 'EM001', 'Bengkel Alat Berat', 42, 1270, 36.5, 65, '2026-06-08 03:28:15'),
(110, '2026-06-05 08:45:00', 'EM001', 'Bengkel Alat Berat', 46, 1360, 36.8, 64, '2026-06-08 03:28:15'),
(111, '2026-06-05 08:50:00', 'EM001', 'Bengkel Alat Berat', 43, 1280, 36.6, 65, '2026-06-08 03:28:15'),
(112, '2026-06-05 08:55:00', 'EM001', 'Bengkel Alat Berat', 39, 1190, 36.2, 66, '2026-06-08 03:28:15'),
(113, '2026-06-05 09:00:00', 'EM001', 'Bengkel Alat Berat', 34, 1080, 35.8, 67, '2026-06-08 03:28:15'),
(114, '2026-06-05 09:05:00', 'EM001', 'Bengkel Alat Berat', 29, 990, 35.4, 68, '2026-06-08 03:28:15'),
(115, '2026-06-05 09:10:00', 'EM001', 'Bengkel Alat Berat', 25, 910, 35, 69, '2026-06-08 03:28:15'),
(116, '2026-06-05 09:15:00', 'EM001', 'Bengkel Alat Berat', 21, 840, 34.6, 70, '2026-06-08 03:28:15'),
(117, '2026-06-05 09:20:00', 'EM001', 'Bengkel Alat Berat', 18, 780, 34.3, 71, '2026-06-08 03:28:15'),
(118, '2026-06-05 09:25:00', 'EM001', 'Bengkel Alat Berat', 15, 730, 34, 72, '2026-06-08 03:28:15'),
(119, '2026-06-05 09:30:00', 'EM001', 'Bengkel Alat Berat', 13, 690, 33.8, 72, '2026-06-08 03:28:15'),
(120, '2026-06-05 09:35:00', 'EM001', 'Bengkel Alat Berat', 16, 750, 34.1, 71, '2026-06-08 03:28:15'),
(121, '2026-06-05 09:40:00', 'EM001', 'Bengkel Alat Berat', 20, 830, 34.5, 70, '2026-06-08 03:28:15'),
(122, '2026-06-05 09:45:00', 'EM001', 'Bengkel Alat Berat', 25, 930, 35, 69, '2026-06-08 03:28:15'),
(123, '2026-06-05 09:50:00', 'EM001', 'Bengkel Alat Berat', 31, 1050, 35.5, 68, '2026-06-08 03:28:15'),
(124, '2026-06-05 09:55:00', 'EM001', 'Bengkel Alat Berat', 37, 1170, 36, 67, '2026-06-08 03:28:15'),
(125, '2026-06-05 10:00:00', 'EM001', 'Bengkel Alat Berat', 43, 1290, 36.4, 66, '2026-06-08 03:28:15'),
(126, '2026-06-05 10:05:00', 'EM001', 'Bengkel Alat Berat', 48, 1400, 36.8, 65, '2026-06-08 03:28:15'),
(127, '2026-06-05 10:10:00', 'EM001', 'Bengkel Alat Berat', 53, 1520, 37.2, 64, '2026-06-08 03:28:15'),
(128, '2026-06-05 10:15:00', 'EM001', 'Bengkel Alat Berat', 57, 1620, 37.5, 63, '2026-06-08 03:28:15'),
(129, '2026-06-05 10:20:00', 'EM001', 'Bengkel Alat Berat', 60, 1700, 37.8, 62, '2026-06-08 03:28:15'),
(130, '2026-06-05 10:25:00', 'EM001', 'Bengkel Alat Berat', 55, 1580, 37.4, 63, '2026-06-08 03:28:15'),
(131, '2026-06-05 10:30:00', 'EM001', 'Bengkel Alat Berat', 49, 1450, 37, 64, '2026-06-08 03:28:15'),
(132, '2026-06-05 10:35:00', 'EM001', 'Bengkel Alat Berat', 43, 1320, 36.5, 65, '2026-06-08 03:28:15'),
(133, '2026-06-05 10:40:00', 'EM001', 'Bengkel Alat Berat', 38, 1210, 36.1, 66, '2026-06-08 03:28:15'),
(134, '2026-06-05 10:45:00', 'EM001', 'Bengkel Alat Berat', 32, 1090, 35.7, 67, '2026-06-08 03:28:15'),
(135, '2026-06-05 10:50:00', 'EM001', 'Bengkel Alat Berat', 27, 980, 35.3, 68, '2026-06-08 03:28:15'),
(136, '2026-06-05 10:55:00', 'EM001', 'Bengkel Alat Berat', 22, 890, 34.9, 69, '2026-06-08 03:28:15'),
(137, '2026-06-05 11:00:00', 'EM001', 'Bengkel Alat Berat', 18, 810, 34.5, 70, '2026-06-08 03:28:15'),
(138, '2026-06-05 11:05:00', 'EM001', 'Bengkel Alat Berat', 15, 740, 34.1, 71, '2026-06-08 03:28:15'),
(139, '2026-06-05 11:10:00', 'EM001', 'Bengkel Alat Berat', 13, 700, 33.9, 72, '2026-06-08 03:28:15'),
(140, '2026-06-05 11:15:00', 'EM001', 'Bengkel Alat Berat', 17, 780, 34.2, 71, '2026-06-08 03:28:15'),
(141, '2026-06-05 11:20:00', 'EM001', 'Bengkel Alat Berat', 23, 900, 34.8, 70, '2026-06-08 03:28:15'),
(142, '2026-06-05 11:25:00', 'EM001', 'Bengkel Alat Berat', 30, 1040, 35.4, 68, '2026-06-08 03:28:15'),
(143, '2026-06-05 11:30:00', 'EM001', 'Bengkel Alat Berat', 38, 1200, 36, 67, '2026-06-08 03:28:15'),
(144, '2026-06-05 11:35:00', 'EM001', 'Bengkel Alat Berat', 46, 1360, 36.6, 65, '2026-06-08 03:28:15'),
(145, '2026-06-05 11:40:00', 'EM001', 'Bengkel Alat Berat', 54, 1530, 37.1, 64, '2026-06-08 03:28:15'),
(146, '2026-06-05 11:45:00', 'EM001', 'Bengkel Alat Berat', 59, 1660, 37.6, 63, '2026-06-08 03:28:15'),
(147, '2026-06-05 11:50:00', 'EM001', 'Bengkel Alat Berat', 52, 1500, 37.1, 64, '2026-06-08 03:28:15'),
(148, '2026-06-05 11:55:00', 'EM001', 'Bengkel Alat Berat', 44, 1320, 36.5, 65, '2026-06-08 03:28:15'),
(149, '2026-06-05 12:00:00', 'EM001', 'Bengkel Alat Berat', 35, 1140, 35.9, 67, '2026-06-08 03:28:15'),
(150, '2026-06-05 12:05:00', 'EM001', 'Bengkel Alat Berat', 27, 980, 35.2, 68, '2026-06-08 03:28:15');

-- --------------------------------------------------------

--
-- Table structure for table `tb_gas_tambang`
--

CREATE TABLE `tb_gas_tambang` (
  `id` bigint UNSIGNED NOT NULL,
  `waktu` datetime NOT NULL,
  `sensor_id` varchar(20) NOT NULL,
  `lokasi` varchar(100) NOT NULL,
  `ch4` float NOT NULL COMMENT 'Persen (% Volume)',
  `h2s` float NOT NULL COMMENT 'ppm',
  `suhu` float NOT NULL COMMENT '°C',
  `kelembaban` float NOT NULL COMMENT '%RH',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tb_gas_tambang`
--

INSERT INTO `tb_gas_tambang` (`id`, `waktu`, `sensor_id`, `lokasi`, `ch4`, `h2s`, `suhu`, `kelembaban`, `created_at`) VALUES
(101, '2026-06-05 08:00:00', 'GS001', 'Area Dasar Tambang', 0.4, 2, 30.8, 78, '2026-06-08 03:28:15'),
(102, '2026-06-05 08:05:00', 'GS001', 'Area Dasar Tambang', 0.5, 3, 31, 78, '2026-06-08 03:28:15'),
(103, '2026-06-05 08:10:00', 'GS001', 'Area Dasar Tambang', 0.7, 4, 31.2, 77, '2026-06-08 03:28:15'),
(104, '2026-06-05 08:15:00', 'GS001', 'Area Dasar Tambang', 0.9, 6, 31.4, 76, '2026-06-08 03:28:15'),
(105, '2026-06-05 08:20:00', 'GS001', 'Area Dasar Tambang', 1.1, 8, 31.6, 75, '2026-06-08 03:28:15'),
(106, '2026-06-05 08:25:00', 'GS001', 'Area Dasar Tambang', 1.4, 11, 31.9, 74, '2026-06-08 03:28:15'),
(107, '2026-06-05 08:30:00', 'GS001', 'Area Dasar Tambang', 1.7, 14, 32.2, 73, '2026-06-08 03:28:15'),
(108, '2026-06-05 08:35:00', 'GS001', 'Area Dasar Tambang', 2, 18, 32.5, 72, '2026-06-08 03:28:15'),
(109, '2026-06-05 08:40:00', 'GS001', 'Area Dasar Tambang', 2.3, 22, 32.8, 71, '2026-06-08 03:28:15'),
(110, '2026-06-05 08:45:00', 'GS001', 'Area Dasar Tambang', 2.6, 26, 33.1, 70, '2026-06-08 03:28:15'),
(111, '2026-06-05 08:50:00', 'GS001', 'Area Dasar Tambang', 2.3, 21, 32.8, 71, '2026-06-08 03:28:15'),
(112, '2026-06-05 08:55:00', 'GS001', 'Area Dasar Tambang', 2, 18, 32.5, 72, '2026-06-08 03:28:15'),
(113, '2026-06-05 09:00:00', 'GS001', 'Area Dasar Tambang', 1.7, 15, 32.2, 73, '2026-06-08 03:28:15'),
(114, '2026-06-05 09:05:00', 'GS001', 'Area Dasar Tambang', 1.4, 12, 31.9, 74, '2026-06-08 03:28:15'),
(115, '2026-06-05 09:10:00', 'GS001', 'Area Dasar Tambang', 1.1, 9, 31.6, 75, '2026-06-08 03:28:15'),
(116, '2026-06-05 09:15:00', 'GS001', 'Area Dasar Tambang', 0.9, 7, 31.4, 76, '2026-06-08 03:28:15'),
(117, '2026-06-05 09:20:00', 'GS001', 'Area Dasar Tambang', 0.7, 5, 31.2, 77, '2026-06-08 03:28:15'),
(118, '2026-06-05 09:25:00', 'GS001', 'Area Dasar Tambang', 0.6, 4, 31.1, 78, '2026-06-08 03:28:15'),
(119, '2026-06-05 09:30:00', 'GS001', 'Area Dasar Tambang', 0.5, 3, 31, 78, '2026-06-08 03:28:15'),
(120, '2026-06-05 09:35:00', 'GS001', 'Area Dasar Tambang', 0.8, 5, 31.2, 77, '2026-06-08 03:28:15'),
(121, '2026-06-05 09:40:00', 'GS001', 'Area Dasar Tambang', 1.2, 9, 31.6, 75, '2026-06-08 03:28:15'),
(122, '2026-06-05 09:45:00', 'GS001', 'Area Dasar Tambang', 1.6, 13, 32, 74, '2026-06-08 03:28:15'),
(123, '2026-06-05 09:50:00', 'GS001', 'Area Dasar Tambang', 2, 18, 32.4, 73, '2026-06-08 03:28:15'),
(124, '2026-06-05 09:55:00', 'GS001', 'Area Dasar Tambang', 2.5, 24, 32.9, 71, '2026-06-08 03:28:15'),
(125, '2026-06-05 10:00:00', 'GS001', 'Area Dasar Tambang', 3, 31, 33.4, 70, '2026-06-08 03:28:15'),
(126, '2026-06-05 10:05:00', 'GS001', 'Area Dasar Tambang', 3.5, 38, 33.8, 69, '2026-06-08 03:28:15'),
(127, '2026-06-05 10:10:00', 'GS001', 'Area Dasar Tambang', 4, 45, 34.2, 68, '2026-06-08 03:28:15'),
(128, '2026-06-05 10:15:00', 'GS001', 'Area Dasar Tambang', 4.4, 52, 34.6, 67, '2026-06-08 03:28:15'),
(129, '2026-06-05 10:20:00', 'GS001', 'Area Dasar Tambang', 4.8, 58, 35, 66, '2026-06-08 03:28:15'),
(130, '2026-06-05 10:25:00', 'GS001', 'Area Dasar Tambang', 4.3, 50, 34.7, 67, '2026-06-08 03:28:15'),
(131, '2026-06-05 10:30:00', 'GS001', 'Area Dasar Tambang', 3.8, 42, 34.3, 68, '2026-06-08 03:28:15'),
(132, '2026-06-05 10:35:00', 'GS001', 'Area Dasar Tambang', 3.3, 35, 33.9, 69, '2026-06-08 03:28:15'),
(133, '2026-06-05 10:40:00', 'GS001', 'Area Dasar Tambang', 2.8, 28, 33.5, 70, '2026-06-08 03:28:15'),
(134, '2026-06-05 10:45:00', 'GS001', 'Area Dasar Tambang', 2.3, 22, 33.1, 71, '2026-06-08 03:28:15'),
(135, '2026-06-05 10:50:00', 'GS001', 'Area Dasar Tambang', 1.8, 16, 32.7, 72, '2026-06-08 03:28:15'),
(136, '2026-06-05 10:55:00', 'GS001', 'Area Dasar Tambang', 1.4, 11, 32.3, 73, '2026-06-08 03:28:15'),
(137, '2026-06-05 11:00:00', 'GS001', 'Area Dasar Tambang', 1, 7, 31.9, 74, '2026-06-08 03:28:15'),
(138, '2026-06-05 11:05:00', 'GS001', 'Area Dasar Tambang', 0.8, 5, 31.6, 75, '2026-06-08 03:28:15'),
(139, '2026-06-05 11:10:00', 'GS001', 'Area Dasar Tambang', 0.6, 4, 31.3, 76, '2026-06-08 03:28:15'),
(140, '2026-06-05 11:15:00', 'GS001', 'Area Dasar Tambang', 1, 8, 31.7, 75, '2026-06-08 03:28:15'),
(141, '2026-06-05 11:20:00', 'GS001', 'Area Dasar Tambang', 1.5, 13, 32.1, 74, '2026-06-08 03:28:15'),
(142, '2026-06-05 11:25:00', 'GS001', 'Area Dasar Tambang', 2.1, 20, 32.6, 72, '2026-06-08 03:28:15'),
(143, '2026-06-05 11:30:00', 'GS001', 'Area Dasar Tambang', 2.8, 29, 33.1, 71, '2026-06-08 03:28:15'),
(144, '2026-06-05 11:35:00', 'GS001', 'Area Dasar Tambang', 3.6, 40, 33.7, 69, '2026-06-08 03:28:15'),
(145, '2026-06-05 11:40:00', 'GS001', 'Area Dasar Tambang', 4.3, 51, 34.3, 68, '2026-06-08 03:28:15'),
(146, '2026-06-05 11:45:00', 'GS001', 'Area Dasar Tambang', 5, 63, 35, 66, '2026-06-08 03:28:15'),
(147, '2026-06-05 11:50:00', 'GS001', 'Area Dasar Tambang', 4.4, 54, 34.5, 67, '2026-06-08 03:28:15'),
(148, '2026-06-05 11:55:00', 'GS001', 'Area Dasar Tambang', 3.6, 42, 33.9, 69, '2026-06-08 03:28:15'),
(149, '2026-06-05 12:00:00', 'GS001', 'Area Dasar Tambang', 2.8, 30, 33.3, 70, '2026-06-08 03:28:15'),
(150, '2026-06-05 12:05:00', 'GS001', 'Area Dasar Tambang', 2, 19, 32.7, 72, '2026-06-08 03:28:15');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_debu_tambang`
--
ALTER TABLE `tb_debu_tambang`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sensor_waktu` (`sensor_id`,`waktu`),
  ADD KEY `idx_waktu` (`waktu`);

--
-- Indexes for table `tb_emisi_alat_berat`
--
ALTER TABLE `tb_emisi_alat_berat`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_waktu` (`waktu`),
  ADD KEY `idx_sensor` (`sensor_id`),
  ADD KEY `idx_lokasi` (`lokasi`),
  ADD KEY `idx_sensor_waktu` (`sensor_id`,`waktu`);

--
-- Indexes for table `tb_gas_tambang`
--
ALTER TABLE `tb_gas_tambang`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_waktu` (`waktu`),
  ADD KEY `idx_sensor` (`sensor_id`),
  ADD KEY `idx_lokasi` (`lokasi`),
  ADD KEY `idx_sensor_waktu` (`sensor_id`,`waktu`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_debu_tambang`
--
ALTER TABLE `tb_debu_tambang`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=151;

--
-- AUTO_INCREMENT for table `tb_emisi_alat_berat`
--
ALTER TABLE `tb_emisi_alat_berat`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=151;

--
-- AUTO_INCREMENT for table `tb_gas_tambang`
--
ALTER TABLE `tb_gas_tambang`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=151;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
