-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 13, 2020 at 01:26 PM
-- Server version: 5.7.19
-- PHP Version: 5.6.31

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `esd`
--

-- --------------------------------------------------------

--
-- Table structure for table `baggage`
--

DROP TABLE IF EXISTS `baggage`;
CREATE TABLE IF NOT EXISTS `baggage` (
  `baggage_id` int(11) NOT NULL,
  `baggage_description` varchar(40) NOT NULL,
  `price` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `baggage`
--

INSERT INTO `baggage` (`baggage_id`, `baggage_description`, `price`) VALUES
(1, 'long_standard', 70),
(2, 'short_standard', 50),
(3, 'long_add30', 80),
(4, 'short_add30', 65);

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

-- --------------------------------------------------------

--
-- Table structure for table `class`
--

DROP TABLE IF EXISTS `class`;
CREATE TABLE IF NOT EXISTS `class` (
  `class` varchar(20) DEFAULT NULL,
  `percentage` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `class`
--

INSERT INTO `class` (`class`, `percentage`) VALUES
('long_economy', 150),
('short_economy', 100),
('long_business', 250),
('short_business', 170),
('long_first', 350),
('short_first', 210);

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
('100', 'SIN', 'JUL', '2020-03-26 23:00:00', '2020-03-27 00:00:00', 65, 's'),
('101', 'KUL', 'SIN', '2020-03-28 04:00:00', '2020-03-28 05:00:00', 67, 's'),
('200', 'SIN', 'MEL', '2020-04-07 22:35:00', '2020-04-08 06:00:00', 238, 'l'),
('201', 'MEL', 'SIN', '2020-03-27 02:00:00', '2020-03-28 09:00:00', 244, 'l');

-- --------------------------------------------------------

--
-- Table structure for table `meal`
--

DROP TABLE IF EXISTS `meal`;
CREATE TABLE IF NOT EXISTS `meal` (
  `meal_id` int(11) NOT NULL,
  `meal_description` varchar(40) NOT NULL,
  `price` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `meal`
--

INSERT INTO `meal` (`meal_id`, `meal_description`, `price`) VALUES
(1, 'fruit_cup', 7),
(2, 'breakfast_set', 15);

-- --------------------------------------------------------

--
-- Table structure for table `passenger`
--

DROP TABLE IF EXISTS `passenger`;
CREATE TABLE IF NOT EXISTS `passenger` (
  `PID` varchar(20) NOT NULL,
  `lastName` varchar(10) NOT NULL,
  `firstName` varchar(30) NOT NULL,
  `email` varchar(30) NOT NULL,
  `dateOfBirth` date NOT NULL,
  `contactNo` int(11) NOT NULL,
  PRIMARY KEY (`PID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
