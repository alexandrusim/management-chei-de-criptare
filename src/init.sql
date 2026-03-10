/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.5.29-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: SIproiect
-- ------------------------------------------------------
-- Server version	10.5.29-MariaDB-ubu2004

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Algoritm`
--

DROP TABLE IF EXISTS `Algoritm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Algoritm` (
  `algoritm_id` int(11) NOT NULL,
  `tip` varchar(100) NOT NULL,
  `nume` varchar(100) DEFAULT NULL,
  `dim_cheie` int(11) NOT NULL,
  `performanta_id` int(11) NOT NULL,
  PRIMARY KEY (`algoritm_id`),
  KEY `performanta_id` (`performanta_id`),
  CONSTRAINT `Algoritm_ibfk_1` FOREIGN KEY (`performanta_id`) REFERENCES `Performanta` (`performanta_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Algoritm`
--

LOCK TABLES `Algoritm` WRITE;
/*!40000 ALTER TABLE `Algoritm` DISABLE KEYS */;
/*!40000 ALTER TABLE `Algoritm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Cheie`
--

DROP TABLE IF EXISTS `Cheie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cheie` (
  `cheie_id` int(11) NOT NULL,
  `algoritm_id` int(11) NOT NULL,
  `status` varchar(10) NOT NULL,
  `val_cheie` varchar(100) NOT NULL,
  `data_creare` date NOT NULL,
  PRIMARY KEY (`cheie_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cheie`
--

LOCK TABLES `Cheie` WRITE;
/*!40000 ALTER TABLE `Cheie` DISABLE KEYS */;
/*!40000 ALTER TABLE `Cheie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Fisier`
--

DROP TABLE IF EXISTS `Fisier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Fisier` (
  `fisier_id` int(11) NOT NULL,
  `nume` varchar(100) NOT NULL,
  `extensie` varchar(10) NOT NULL,
  `dimensiune` int(11) NOT NULL,
  `path` varchar(100) NOT NULL,
  `performanta_id` int(11) NOT NULL,
  PRIMARY KEY (`fisier_id`),
  KEY `performanta_id` (`performanta_id`),
  CONSTRAINT `Fisier_ibfk_1` FOREIGN KEY (`performanta_id`) REFERENCES `Performanta` (`performanta_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Fisier`
--

LOCK TABLES `Fisier` WRITE;
/*!40000 ALTER TABLE `Fisier` DISABLE KEYS */;
/*!40000 ALTER TABLE `Fisier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Framework`
--

DROP TABLE IF EXISTS `Framework`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Framework` (
  `framework_id` int(11) NOT NULL,
  `nume` varchar(100) NOT NULL,
  `performanta_id` int(11) NOT NULL,
  PRIMARY KEY (`framework_id`),
  KEY `performanta_id` (`performanta_id`),
  CONSTRAINT `Framework_ibfk_1` FOREIGN KEY (`performanta_id`) REFERENCES `Performanta` (`performanta_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Framework`
--

LOCK TABLES `Framework` WRITE;
/*!40000 ALTER TABLE `Framework` DISABLE KEYS */;
/*!40000 ALTER TABLE `Framework` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Performanta`
--

DROP TABLE IF EXISTS `Performanta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Performanta` (
  `performanta_id` int(11) NOT NULL,
  `timp` int(11) NOT NULL,
  `memorie` int(11) NOT NULL,
  `tip_operatiune` varchar(100) NOT NULL,
  PRIMARY KEY (`performanta_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Performanta`
--

LOCK TABLES `Performanta` WRITE;
/*!40000 ALTER TABLE `Performanta` DISABLE KEYS */;
/*!40000 ALTER TABLE `Performanta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-10 10:14:39
