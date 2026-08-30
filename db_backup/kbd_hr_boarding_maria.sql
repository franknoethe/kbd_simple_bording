-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server-Version:               10.4.32-MariaDB - mariadb.org binary distribution
-- Server-Betriebssystem:        Win64
-- HeidiSQL Version:             12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Exportiere Datenbank-Struktur für kbd_hr_boarding
DROP DATABASE IF EXISTS `kbd_hr_boarding`;
CREATE DATABASE IF NOT EXISTS `kbd_hr_boarding` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `kbd_hr_boarding`;

-- Exportiere Struktur von Tabelle kbd_hr_boarding.email_templates
DROP TABLE IF EXISTS `email_templates`;
CREATE TABLE IF NOT EXISTS `email_templates` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `body_html` text DEFAULT NULL,
  `body_text` text DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.email_templates: ~9 rows (ungefähr)
DELETE FROM `email_templates`;
INSERT INTO `email_templates` (`id`, `name`, `subject`, `body_html`, `body_text`, `active`) VALUES
	(1, 'Begrüßungsmail', 'Willkommen im Team von [STANDORT]', '', 'Hallo lieber [RESPONSIBLE],\n\nunser Team freut sich dir mitteilen zu dürfen dich al neues Mitglied begrüßen zu können.\n\nHier kurz die Eckdaten: \n\nStandort:[LOCATION]\nFunktion: [JOB] \nName: [NEWBIE] \nStart: [STARTDATE]\n\nLG', 1),
	(2, 'Info neuer Mitarbeiter', 'Neuer Zugang zum [STARTDATE]', '', 'Hallo lieber [VERANTWORTLICHER],\n\nunser Team wird um einen neuen Kollegin/Kollegen erweitert.\n\nHier kurz die Eckdaten: \n\nStandort:[LOCATION]\nFunktion: [JOB] \nName: [NEWBIE] \nStart: [STARTDATE]\n\nLG', 1),
	(4, 'Info Buddy', 'Neuer Kollege [NEWBIE] zum [STARTDATE]', '', 'Hallo lieber [BUDDY],\n\nAm [STARTDATE] wird dein Team mit dem neuen [NEWBIE] erweitert. Er wird seine Tätigkeit als [JOB] am [STARTDATE]. \n\nLG', 1),
	(5, 'Antrag IT-Accounts', 'Neue Accounts für [NEWBIE]', '', 'Hallo lieber [RESPONSIBLE],\n\nunser Team freut sich auf einen neuen Zugang. Richtet doch bitte die nötigen Accounts für die folgende Funktion ein.\n\nHier kurz die Eckdaten:\n\nName: [NEWBIE]\nStandort:[LOCATION]\nFunktion: [JOB] \nStart: [STARTDATE]\n\nLG', 1),
	(6, 'Antrag IT Hardware', 'Antrag neuer Arbeitsplatz für [NEWBIE]', '', 'Hallo lieber [RESPONSIBLE],\n\nunser Team freut sich auf einen neuen Zugang. Richtet doch bitte einen IT-Arbeitsplatz für die folgende Funktion ein.\n\nHier kurz die Eckdaten:\n\nName: [NEWBIE]\nStandort:[LOCATION]\nFunktion: [JOB] \nStart: [STARTDATE]\n\nLG', 1),
	(7, 'Schulung DSGVO', 'Denken sie bitte an ihre DSGVO-Schulung', '', 'Hallo lieber [NEWBIE],\n\ndenke bitte daran deine DSGV - Unterweisung bis zum [DUEDATE] zu absolvieren. Den Lehrgang findest du hier:\n\nhttps://www.projobtraining.de/goto.php/crs/758243\n\nZugangsdaten:\nBenutzer: dein-vorname.dein-zuname\nPW: bildung\n\nNachdem Lehrgang, kannst du dir ein Zertifikat herunterladen, dass du uns bitte per Mail zukommen lässt\n\n\nLG', 1),
	(8, 'Schulung Arbeitssicherheit', 'Denken sie bitte an ihre Arbeitssicherheit-Schulung', '', 'Hallo lieber [NEWBIE],\n\ndenke bitte daran deine Arbeitssicherheit - Unterweisung bis zum [DUEDATE] zu absolvieren. Den Lehrgang findest du hier:\n\nhttps://www.projobtraining.de/goto.php/crs/758243\n\nZugangsdaten:\nBenutzer: dein-vorname.dein-zuname\nPW: bildung\n\nNachdem Lehrgang, kannst du dir ein Zertifikat herunterladen, dass du uns bitte per Mail zukommen lässt\n\n\nLG', 1),
	(9, 'Info Arbeitsplatz einrichten', 'Denke an den Arbeitsplatz für [NEWBIE]', '', 'Hallo lieber [BUDDY],\n\nunser Team freut sich auf einen neuen Zugang. Richte seinen  Arbeitsplatz für die folgende Funktion ein.\n\nHier kurz die Eckdaten:\n\nName: [NEWBIE]\nStandort:[LOCATION]\nFunktion: [JOB] \nStart: [STARTDATE]\n\nLG', 1),
	(10, 'Info Newbie empfangen', 'Morgen kommt [NEWBIE]', '', 'test', 1);

-- Exportiere Struktur von Tabelle kbd_hr_boarding.employees
DROP TABLE IF EXISTS `employees`;
CREATE TABLE IF NOT EXISTS `employees` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `employee_number` varchar(50) DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `email_business` varchar(255) DEFAULT NULL,
  `email_private` varchar(255) DEFAULT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password_hash` text DEFAULT NULL,
  `location_id` tinyint(4) DEFAULT NULL,
  `job_id` tinyint(4) DEFAULT NULL,
  `role_id` tinyint(4) DEFAULT NULL,
  `function_id` tinyint(4) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.employees: ~14 rows (ungefähr)
DELETE FROM `employees`;
INSERT INTO `employees` (`id`, `employee_number`, `first_name`, `last_name`, `email_business`, `email_private`, `username`, `password_hash`, `location_id`, `job_id`, `role_id`, `function_id`, `active`, `created_at`, `department`) VALUES
	(1, NULL, 'Eiti', 'Nerd', 'frank.noethe@kolping-bildung-deutschland.de', NULL, 'enerd', 'test', 1, 1, 4, 3, NULL, NULL, 'IT'),
	(4, '1001', 'Frank', 'Nöthe', 'frank.noethe@kolping-bildung-deutschland.de', 'frank.noethe@gmail.com', 'fnoethe', 'admin', 1, 1, 1, 6, 1, '2026-08-12 11:45:38', 'IT'),
	(5, '1002', 'Jörg', 'Roßmannek', 'joerg.rossmannek@kolping-bildung-deutschland.de', NULL, 'jrossmannek', 'test', 1, 3, 3, 2, 1, '2026-08-12 11:45:38', 'IT'),
	(6, '1003', 'Jens', 'Urban', 'jens.urban@kolping-bildung-deutschland.de', NULL, 'jurban', 'test', 1, 2, 4, 5, 1, '2026-08-12 11:45:38', 'IT'),
	(7, NULL, 'Jan', 'Winter', 'jan.winter@kolping-bildung-deutschland.de', NULL, 'jwinter', '', 1, 1, 3, 4, 1, '2026-08-13 09:40:00', 'IT'),
	(8, NULL, 'Thomas', 'Honrath', 'thomas.honrath@kolping-bildung-deutschland.de', NULL, 'thonrath', 'test', 1, 1, 4, 2, 1, '2026-08-13 13:37:13', 'IT'),
	(9, NULL, 'Micha', 'Tronik', 'frank.noethe@kolping-bildung-deutschland.de', NULL, 'mtronik', 'test', 3, 6, 4, 3, 1, '2026-08-15 16:48:43', 'Ausbilder'),
	(10, NULL, 'Frank', 'Bahnsen', 'frank.noethe@kolping-bildung-deutschland.de', NULL, 'fbahnsen', 'test', 3, 9, 3, 5, NULL, NULL, ''),
	(11, NULL, 'Marcel', 'van de Twer', 'frank.noethe@kolping-bildung-deutschland.de', NULL, 'mvandetwer', '', 3, 8, 3, 4, NULL, NULL, ''),
	(12, NULL, 'Lisa Marie', 'Bergmeier', 'frank.noethe@kolping-bildung-deutschland.de', NULL, 'lbermeier', 'test', 3, 7, 3, 2, NULL, NULL, ''),
	(13, NULL, 'Thomas', 'Braune', 'frank.noethe@kolping-bildung-deutschland.de', NULL, 'tbraune', 'test', 3, 6, 3, 6, NULL, NULL, ''),
	(14, NULL, 'IT', 'Helpdesk', 'it-support@kolping-bildung-deutschland.de', NULL, '', '', 1, 17, 4, 7, NULL, NULL, 'IT'),
	(15, NULL, 'Diggi', 'Tal', 'frenk.noethe@gmail.com', NULL, 'dtal', 'test', 1, 2, 4, 3, NULL, NULL, 'IT'),
	(16, NULL, 'Bit', 'Coin', 'frank.noethe@gmail.com', NULL, 'bcoin', 'test', 1, 1, 4, 3, NULL, NULL, 'IT');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.functions
DROP TABLE IF EXISTS `functions`;
CREATE TABLE IF NOT EXISTS `functions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  UNIQUE KEY `functions_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.functions: ~5 rows (ungefähr)
DELETE FROM `functions`;
INSERT INTO `functions` (`id`, `name`) VALUES
	(2, 'Buddy'),
	(3, 'Newbie'),
	(4, 'Abteilungsleitung'),
	(5, 'Standortleitung'),
	(6, 'Teamleiter'),
	(7, 'IT-Verwaltung');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.jobs
DROP TABLE IF EXISTS `jobs`;
CREATE TABLE IF NOT EXISTS `jobs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `location_id` tinyint(4) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  KEY `jobs_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.jobs: ~16 rows (ungefähr)
DELETE FROM `jobs`;
INSERT INTO `jobs` (`id`, `location_id`, `name`) VALUES
	(1, 1, 'Systemadministrator'),
	(2, 1, 'Anwendungsentwickler'),
	(3, 1, 'IT-Leiter'),
	(4, 2, 'Sachbearbeiter HR'),
	(5, 8, 'Praktikant'),
	(6, 3, 'Ausbilder Mechatroniker'),
	(7, 3, 'Ausbilder Productdesign'),
	(9, 3, 'BZ Leitung'),
	(8, 3, 'Ausbilder Elektrotechnik'),
	(10, 3, 'Sachbearbeiter Verwaltung'),
	(11, 3, 'Ausbilder'),
	(12, 9, 'Ausbilder Elektrotechnik'),
	(13, 9, 'Ausbilder Mechatronik'),
	(14, 9, 'Standortleitung'),
	(15, 9, 'Abteilungsleitung'),
	(17, 1, 'IT');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.locations
DROP TABLE IF EXISTS `locations`;
CREATE TABLE IF NOT EXISTS `locations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  UNIQUE KEY `locations_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.locations: ~7 rows (ungefähr)
DELETE FROM `locations`;
INSERT INTO `locations` (`id`, `name`, `active`) VALUES
	(1, 'HV Recklinghausen', 1),
	(2, 'HV Essen', 1),
	(3, 'BZ Essen', 1),
	(4, 'BZ Dortmund', 1),
	(5, 'PS Recklinghausen', 1),
	(6, 'PS Dortmund', 1),
	(8, 'BZ Recklinghausen', 1),
	(9, 'KBD allgemein', 1);

-- Exportiere Struktur von Tabelle kbd_hr_boarding.notification_queue
DROP TABLE IF EXISTS `notification_queue`;
CREATE TABLE IF NOT EXISTS `notification_queue` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `task_id` tinyint(4) DEFAULT NULL,
  `recipient_email` varchar(255) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `body_html` text DEFAULT NULL,
  `send_at` timestamp NULL DEFAULT NULL,
  `sent_at` timestamp NULL DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL,
  UNIQUE KEY `notification_queue_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.notification_queue: ~0 rows (ungefähr)
DELETE FROM `notification_queue`;

-- Exportiere Struktur von Tabelle kbd_hr_boarding.process_cases
DROP TABLE IF EXISTS `process_cases`;
CREATE TABLE IF NOT EXISTS `process_cases` (
  `id` tinyint(4) NOT NULL AUTO_INCREMENT,
  `employee_id` tinyint(4) DEFAULT NULL,
  `template_id` tinyint(4) DEFAULT NULL,
  `start_date` date NOT NULL,
  `status` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  UNIQUE KEY `process_cases_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.process_cases: ~2 rows (ungefähr)
DELETE FROM `process_cases`;
INSERT INTO `process_cases` (`id`, `employee_id`, `template_id`, `start_date`, `status`, `created_at`) VALUES
	(1, 9, 1, '2026-09-15', 'OPEN', '2026-08-15 16:55:20'),
	(3, 1, 6, '2026-10-01', 'OPEN', '2026-08-18 08:17:06');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.process_types
DROP TABLE IF EXISTS `process_types`;
CREATE TABLE IF NOT EXISTS `process_types` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  UNIQUE KEY `process_types_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.process_types: ~3 rows (ungefähr)
DELETE FROM `process_types`;
INSERT INTO `process_types` (`id`, `name`) VALUES
	(1, 'Onboarding'),
	(2, 'Reboarding'),
	(3, 'Offboarding');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.roles
DROP TABLE IF EXISTS `roles`;
CREATE TABLE IF NOT EXISTS `roles` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  UNIQUE KEY `roles_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.roles: ~3 rows (ungefähr)
DELETE FROM `roles`;
INSERT INTO `roles` (`id`, `name`) VALUES
	(1, 'Admin'),
	(3, 'Manager'),
	(4, 'User');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.tasks
DROP TABLE IF EXISTS `tasks`;
CREATE TABLE IF NOT EXISTS `tasks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `term` varchar(255) DEFAULT NULL,
  `theme` varchar(255) DEFAULT NULL,
  `employee_id` bigint(20) NOT NULL,
  `template_task_id` bigint(20) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `due_date` date NOT NULL,
  `status` enum('open','in_progress','completed') NOT NULL DEFAULT 'open',
  `created_at` date NOT NULL DEFAULT current_timestamp(),
  `reminder_sent_at` date DEFAULT NULL,
  `email_template_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_tasks_employee` (`employee_id`),
  KEY `fk_tasks_template_task` (`template_task_id`),
  KEY `idx_tasks_due_date` (`due_date`,`status`,`reminder_sent_at`),
  KEY `fk_tasks_email_template` (`email_template_id`),
  CONSTRAINT `fk_tasks_email_template` FOREIGN KEY (`email_template_id`) REFERENCES `email_templates` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_tasks_employee` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`),
  CONSTRAINT `fk_tasks_template_task` FOREIGN KEY (`template_task_id`) REFERENCES `template_tasks` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=118 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.tasks: ~17 rows (ungefähr)
DELETE FROM `tasks`;
INSERT INTO `tasks` (`id`, `term`, `theme`, `employee_id`, `template_task_id`, `title`, `description`, `due_date`, `status`, `created_at`, `reminder_sent_at`, `email_template_id`) VALUES
	(101, 'Onboarding | IT-Systemadministrator | Diggi Tal', 'Newbie', 1, 7, 'Begrüßung', 'Der Newbie wird über sein Einstellungsdatum und diesem Prozessstart informiert.', '2026-11-01', 'open', '2026-08-30', NULL, 1),
	(102, 'Onboarding | IT-Systemadministrator | Diggi Tal', 'Abteilungsleitung', 7, 8, 'Info an Abteilungsleitung', 'Die Abteilungsleitung wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', '2026-11-01', 'open', '2026-08-30', NULL, 2),
	(103, 'Onboarding | IT-Systemadministrator | Diggi Tal', 'Teamleiter', 4, 9, 'Info Teamleader', 'Der Teamleader wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', '2026-11-01', 'open', '2026-08-30', NULL, 2),
	(104, 'Onboarding | IT-Systemadministrator | Diggi Tal', 'Buddy', 5, 10, 'Info an Buddy', 'Die Begleitung wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', '2026-11-01', 'open', '2026-08-30', NULL, 4),
	(105, 'Onboarding | IT-Systemadministrator | Diggi Tal', 'IT-Verwaltung', 14, 11, 'Antrag IT-Accounts', 'Die IT wird über den Zugang des neuen Zugangs mit seinen Eckdaten informiert und gebeten dem Job angepassten Accounts im System anzulegen.', '2026-11-06', 'open', '2026-08-30', NULL, 5),
	(106, 'Onboarding | IT-Systemadministrator | Diggi Tal', 'IT-Verwaltung', 14, 12, 'Antrag auf Hardware', 'Die IT wird über den Zugang des neuen Zugangs mit seinen Eckdaten informiert und gebeten der dem Job angepassten Hardware zur Verfügung zu stellen.', '2026-11-01', 'open', '2026-08-30', NULL, 6),
	(107, 'Onboarding | IT-Systemadministrator | Diggi Tal', 'Abteilungsleitung', 7, 13, 'Seelische Vorbereitung auf den Newbie', 'Eine Aufgabe ohne EMAIL', '2026-11-08', 'open', '2026-08-30', NULL, NULL),
	(108, 'Onboarding | Ausbilder Elektrotechnik | Micha Tronik', 'Newbie', 9, 1, 'Begrüssungsmail', 'Der neue Mitarbeiter erhält eine Nachricht darüber das er Registriert wurde und wie es nun weitergeht', '2026-10-01', 'open', '2026-08-30', NULL, 1),
	(109, 'Onboarding | Ausbilder Elektrotechnik | Micha Tronik', 'Teamleiter', 13, 3, 'Mail an die Teamleitung', 'Info darüber das ein neuer Mitarbeiter für sein BZ registriert wurde.', '2026-10-01', 'open', '2026-08-30', NULL, 2),
	(110, 'Onboarding | Ausbilder Elektrotechnik | Micha Tronik', 'Abteilungsleitung', 11, 2, 'Mail an die Abteilungsleitung', 'Info darüber das ein neuer Mitarbeiter für sein BZ registriert wurde', '2026-10-02', 'open', '2026-08-30', NULL, 2),
	(111, 'Onboarding | IT-Systemadministrator | Bit Coin', 'Newbie', 1, 7, 'Begrüßung', 'Der Newbie wird über sein Einstellungsdatum und diesem Prozessstart informiert.', '2026-12-01', 'open', '2026-08-30', NULL, 1),
	(112, 'Onboarding | IT-Systemadministrator | Bit Coin', 'Abteilungsleitung', 7, 8, 'Info an Abteilungsleitung', 'Die Abteilungsleitung wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', '2026-12-01', 'open', '2026-08-30', NULL, 2),
	(113, 'Onboarding | IT-Systemadministrator | Bit Coin', 'Teamleiter', 4, 9, 'Info Teamleader', 'Der Teamleader wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', '2026-12-01', 'open', '2026-08-30', NULL, 2),
	(114, 'Onboarding | IT-Systemadministrator | Bit Coin', 'Buddy', 5, 10, 'Info an Buddy', 'Die Begleitung wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', '2026-12-01', 'open', '2026-08-30', NULL, 4),
	(115, 'Onboarding | IT-Systemadministrator | Bit Coin', 'IT-Verwaltung', 14, 11, 'Antrag IT-Accounts', 'Die IT wird über den Zugang des neuen Zugangs mit seinen Eckdaten informiert und gebeten dem Job angepassten Accounts im System anzulegen.', '2026-12-06', 'open', '2026-08-30', NULL, 5),
	(116, 'Onboarding | IT-Systemadministrator | Bit Coin', 'IT-Verwaltung', 14, 12, 'Antrag auf Hardware', 'Die IT wird über den Zugang des neuen Zugangs mit seinen Eckdaten informiert und gebeten der dem Job angepassten Hardware zur Verfügung zu stellen.', '2026-12-01', 'open', '2026-08-30', NULL, 6),
	(117, 'Onboarding | IT-Systemadministrator | Bit Coin', 'Abteilungsleitung', 7, 13, 'Seelische Vorbereitung auf den Newbie', 'Eine Aufgabe ohne EMAIL', '2026-12-08', 'open', '2026-08-30', NULL, NULL);

-- Exportiere Struktur von Tabelle kbd_hr_boarding.task_history
DROP TABLE IF EXISTS `task_history`;
CREATE TABLE IF NOT EXISTS `task_history` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `task_id` tinyint(4) DEFAULT NULL,
  `action` varchar(100) DEFAULT NULL,
  `old_status` varchar(50) DEFAULT NULL,
  `new_status` varchar(50) DEFAULT NULL,
  `changed_by` tinyint(4) DEFAULT NULL,
  `changed_at` timestamp NULL DEFAULT NULL,
  UNIQUE KEY `task_history_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.task_history: ~0 rows (ungefähr)
DELETE FROM `task_history`;

-- Exportiere Struktur von Tabelle kbd_hr_boarding.task_reminders
DROP TABLE IF EXISTS `task_reminders`;
CREATE TABLE IF NOT EXISTS `task_reminders` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `task_id` tinyint(4) DEFAULT NULL,
  `reminder_date` timestamp NULL DEFAULT NULL,
  `sent` tinyint(1) DEFAULT NULL,
  UNIQUE KEY `task_reminders_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.task_reminders: ~0 rows (ungefähr)
DELETE FROM `task_reminders`;

-- Exportiere Struktur von Tabelle kbd_hr_boarding.templates
DROP TABLE IF EXISTS `templates`;
CREATE TABLE IF NOT EXISTS `templates` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `process_type_id` tinyint(4) DEFAULT NULL,
  `location_id` tinyint(4) DEFAULT NULL,
  `job_id` tinyint(4) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  UNIQUE KEY `templates_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.templates: ~5 rows (ungefähr)
DELETE FROM `templates`;
INSERT INTO `templates` (`id`, `process_type_id`, `location_id`, `job_id`, `name`, `active`, `created_at`) VALUES
	(1, 1, 3, 11, 'Ausbilder Elektrotechnik', 1, '2026-08-15 17:16:51'),
	(4, 1, 3, 11, 'Ausbilder TPD', 1, '2026-08-15 18:03:04'),
	(5, 1, 1, 17, 'IT-Systemadministrator', 1, '2026-08-17 09:55:26'),
	(6, 1, 3, 11, 'Ausbilder Mechatroniker', 1, '2026-08-18 06:08:10'),
	(7, 1, 1, 17, 'IT-Systemprogrammierer', 1, NULL);

-- Exportiere Struktur von Tabelle kbd_hr_boarding.template_tasks
DROP TABLE IF EXISTS `template_tasks`;
CREATE TABLE IF NOT EXISTS `template_tasks` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `template_id` tinyint(4) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `responsible_function_id` tinyint(4) DEFAULT NULL,
  `due_offset_days` tinyint(4) NOT NULL,
  `email_template_id` tinyint(4) DEFAULT NULL,
  `mandatory` tinyint(1) DEFAULT NULL,
  `step` tinyint(4) DEFAULT NULL,
  UNIQUE KEY `template_tasks_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.template_tasks: ~18 rows (ungefähr)
DELETE FROM `template_tasks`;
INSERT INTO `template_tasks` (`id`, `template_id`, `title`, `description`, `responsible_function_id`, `due_offset_days`, `email_template_id`, `mandatory`, `step`) VALUES
	(1, 1, 'Begrüssungsmail', 'Der neue Mitarbeiter erhält eine Nachricht darüber das er Registriert wurde und wie es nun weitergeht', 3, 0, 1, 1, 1),
	(2, 1, 'Mail an die Abteilungsleitung', 'Info darüber das ein neuer Mitarbeiter für sein BZ registriert wurde', 4, 1, 2, 1, 3),
	(3, 1, 'Mail an die Teamleitung', 'Info darüber das ein neuer Mitarbeiter für sein BZ registriert wurde.', 6, 0, 2, 1, 2),
	(7, 5, 'Begrüßung', 'Der Newbie wird über sein Einstellungsdatum und diesem Prozessstart informiert.', 3, 0, 1, 1, 1),
	(8, 5, 'Info an Abteilungsleitung', 'Die Abteilungsleitung wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', 4, 0, 2, 1, 2),
	(9, 5, 'Info Teamleader', 'Der Teamleader wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', 6, 0, 2, 1, 3),
	(10, 5, 'Info an Buddy', 'Die Begleitung wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', 2, 0, 4, 1, 4),
	(11, 5, 'Antrag IT-Accounts', 'Die IT wird über den Zugang des neuen Zugangs mit seinen Eckdaten informiert und gebeten dem Job angepassten Accounts im System anzulegen.', 7, 5, 5, 1, 5),
	(12, 5, 'Antrag auf Hardware', 'Die IT wird über den Zugang des neuen Zugangs mit seinen Eckdaten informiert und gebeten der dem Job angepassten Hardware zur Verfügung zu stellen.', 7, 0, 6, 1, 6),
	(13, 5, 'Seelische Vorbereitung auf den Newbie', 'Eine Aufgabe ohne EMAIL', 4, 7, NULL, 0, 7),
	(24, 7, 'Begrüßung', 'Der Newbie wird über sein Einstellungsdatum und diesem Prozessstart informiert.', 2, 0, 1, 1, 1),
	(25, 7, 'Info an Abteilungsleitung', 'Die Abteilungsleitung wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', 4, 0, 2, 1, 2),
	(26, 7, 'Info Teamleader', 'Der Teamleader wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', 6, 0, 2, 1, 3),
	(27, 7, 'Info an Buddy', 'Die Begleitung wird über den Zugang eines neuen Mitarbeiters und dessen Eckdaten informiert.', 2, 0, 4, 1, 4),
	(28, 7, 'Antrag IT-Accounts', 'Die IT wird über den Zugang des neuen Zugangs mit seinen Eckdaten informiert und gebeten dem Job angepassten Accounts im System anzulegen.', 7, 5, 5, 1, 5),
	(29, 7, 'Antrag auf Hardware', 'Die IT wird über den Zugang des neuen Zugangs mit seinen Eckdaten informiert und gebeten der dem Job angepassten Hardware zur Verfügung zu stellen.', 7, 0, 6, 1, 6),
	(30, 7, 'Seelische Vorbereitung auf den Newbie', 'Eine Aufgabe ohne EMAIL', 2, 7, NULL, 0, 7),
	(31, 4, 'Begrüßungsmail an Newbie', 'In diesem Schritt wird der Newbie darüber informiert, dass er als neuer Mitarbeiter im Betrieb registriert wurde.', 2, 0, 1, 1, 0);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
