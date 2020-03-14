-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 14, 2020 at 07:49 AM
-- Server version: 5.7.23
-- PHP Version: 7.2.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

drop database if exists flight_name;
create database flight_name;
use flight_name;
--
-- Database: `flight_name`
--

-- --------------------------------------------------------

--
-- Table structure for table `flight`
--

DROP TABLE IF EXISTS `flight`;
CREATE TABLE IF NOT EXISTS `flight` (
  `flightNo` varchar(8) NOT NULL,
  `departDest` varchar(5) NOT NULL,
  `arrivalDest` varchar(5) NOT NULL,
  `deptTime` timestamp NOT NULL,
  `arrivalTime` timestamp NOT NULL,
  `basePrice` double NOT NULL,
  `type` varchar(1) NOT NULL,
  PRIMARY KEY (`flightNo`,`deptTime`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `flight`
--

INSERT INTO `flight` (`flightNo`, `departDest`, `arrivalDest`, `deptTime`, `arrivalTime`, `basePrice`, `type`) VALUES
('100', 'SIN', 'JUL', '2020-03-26 15:00:00', '2020-03-26 16:00:00', 65, 's'),
('101', 'KUL', 'SIN', '2020-03-27 20:00:00', '2020-03-27 21:00:00', 67, 's'),
('200', 'SIN', 'MEL', '2020-04-07 14:35:00', '2020-04-07 22:00:00', 238, 'l'),
('201', 'MEL', 'SIN', '2020-03-26 18:00:00', '2020-03-28 01:00:00', 244, 'l');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
