
-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 10, 2020 at 08:10 AM
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


drop database if exists flight_booking;
create database flight_booking;
use flight_booking;
--
-- Database: `flight_booking`
--

-- --------------------------------------------------------

--
-- Table structure for table `booking`
--

DROP TABLE IF EXISTS `booking`;
CREATE TABLE IF NOT EXISTS `booking` (
  `refCode` varchar(10) NOT NULL,
  `PID` varchar(20) NOT NULL,
  `flightNo` varchar(8) NOT NULL,
  `deptTime` timestamp NOT NULL,
  `departDate` date NOT NULL,
  `price` double NOT NULL,
  `class` int(11) NOT NULL,
  `add-on` varchar(50) NOT NULL,
  PRIMARY KEY (`refCode`),
  KEY `booking_fk2` (`flightNo`,`deptTime`),
  KEY `booking_fk1` (`PID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `booking`
--
ALTER TABLE `booking`
  ADD CONSTRAINT `booking_fk1` FOREIGN KEY (`PID`) REFERENCES `flight_passenger`.`passenger` (`PID`),
  ADD CONSTRAINT `booking_fk2` FOREIGN KEY (`flightNo`,`deptTime`) REFERENCES `flight_name`.`flight` (`flightNo`, `deptTime`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
