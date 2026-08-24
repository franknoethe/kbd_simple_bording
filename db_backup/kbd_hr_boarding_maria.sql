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
  `id` bigint(20) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `body_html` text DEFAULT NULL,
  `body_text` text DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.email_templates: ~30 rows (ungefähr)
DELETE FROM `email_templates`;
INSERT INTO `email_templates` (`id`, `name`, `subject`, `body_html`, `body_text`, `active`) VALUES
	(11, 'Onboarding Begrüßung an Newbie', 'Willkommen im Team', '', 'Hallo [NAME],\n\nwir freuen uns sie am [STARTDATUM] als neuen Kollegen am Standort [LOCATION] als [JOB] begrüßen zu dürfen.\n\nWir halten sie auf diesem Wege auf Stand um einen reibungslosen Start in den neuen Job zu gewährleisten\n\nViele Grüße\n[MITARBEITER]', 1),
	(1, 'Infomail an BZ Leitung Mitarbeiterzugang', 'Mitarbeiterzugang [STARTDATE]', '', 'Hallo [NAME],\n\nich hoffe, es geht Ihnen gut! Ich möchte Ihnen ganz herzlich zu Ihrer neuen Position als Ausbilder im [LOCATION] als [JOB] gratulieren. Das ist wirklich eine großartige Neuigkeit! Ich bin überzeugt, dass Sie mit Ihrem Engagement und Ihrer Erfahrung das Team bereichern und einen wertvollen Beitrag leisten werden. Für Ihren Start wünsche ich Ihnen viel Freude und Erfolg und freue mich auf die Zusammenarbeit.\n\nViele Grüße\n[MITARBEITER]', 1),
	(10, 'Reminder Verpasste Aufgabe', '[THEME]: Reminder verpasste Aufgabe', '', 'Hallo [NAME],\n\nim Rahmen des [THEME] steht noch eine Aufgabe offen.\n\nBitte bestätigen sie unter diesem Link die Kenntnisnahme!\n\nViele Grüße\n[MITARBEITER]', 1),
	(12, 'Onboarding Abteilungsleitung Begleiter bestimmen', 'Bgleitung für neuen Mitarbeiter', '', 'Hallo,\n\n', 1),
	(13, 'Onboarding Begleiter Arbeitsplatz einrichten', 'Arbeitsplatz für [NEWBIE]', '', 'Hallo,', 1),
	(8, 'Onboarding Infomail Abteilungsleitung', 'Neuer Mitarbeiter als [JOB] am  [STARTDATE]', '', 'Hallo [NAME],\n\nam [STARTDATUM] wird ein neuer Kollege am Standort [LOCATION] als [JOB] seine Tätigkeit aufnehmen.\n\nBitte bestätigen sie unter diesem Link die Kenntnisnahme!\n\nViele Grüße\n[MITARBEITER]', 1),
	(9, 'Onboarding Infomail an die Standortleitung', 'Neuer Mitarbeiter am [LOCATION] am [STARTDATE]', '', 'Hallo [NAME],\n\nam [STARTDATUM] wird ein neuer Kollege am Standort [LOCATION] als [JOB] seine Tätigkeit aufnehmen.\n\nBitte bestätigen sie unter diesem Link die Kenntnisnahme!\n\nViele Grüße\n[MITARBEITER]', 1),
	(14, 'Onboarding Newbie Schulung Arbeitsschutz', 'Eine Unterweisung wartet auf dich', '', 'Hallo,\n\n', 1),
	(15, 'Onboarding Newbie Schulung DSGV', 'Eine Unterweisung wartet auf dich', '', 'Hallo,\n\n', 1),
	(16, 'Onboarding Begleiter Newbie Begrüßung', 'Bicht Vergessen dein [NEWBIE] kommt [STARTDATE]', '', 'Hallo,', 1),
	(11, 'Onboarding Begrüßung an Newbie', 'Willkommen im Team', '', 'Hallo [NAME],\n\nwir freuen uns sie am [STARTDATUM] als neuen Kollegen am Standort [LOCATION] als [JOB] begrüßen zu dürfen.\n\nWir halten sie auf diesem Wege auf Stand um einen reibungslosen Start in den neuen Job zu gewährleisten\n\nViele Grüße\n[MITARBEITER]', 1),
	(1, 'Infomail an BZ Leitung Mitarbeiterzugang', 'Mitarbeiterzugang [STARTDATE]', '', 'Hallo [NAME],\n\nich hoffe, es geht Ihnen gut! Ich möchte Ihnen ganz herzlich zu Ihrer neuen Position als Ausbilder im [LOCATION] als [JOB] gratulieren. Das ist wirklich eine großartige Neuigkeit! Ich bin überzeugt, dass Sie mit Ihrem Engagement und Ihrer Erfahrung das Team bereichern und einen wertvollen Beitrag leisten werden. Für Ihren Start wünsche ich Ihnen viel Freude und Erfolg und freue mich auf die Zusammenarbeit.\n\nViele Grüße\n[MITARBEITER]', 1),
	(10, 'Reminder Verpasste Aufgabe', '[THEME]: Reminder verpasste Aufgabe', '', 'Hallo [NAME],\n\nim Rahmen des [THEME] steht noch eine Aufgabe offen.\n\nBitte bestätigen sie unter diesem Link die Kenntnisnahme!\n\nViele Grüße\n[MITARBEITER]', 1),
	(12, 'Onboarding Abteilungsleitung Begleiter bestimmen', 'Bgleitung für neuen Mitarbeiter', '', 'Hallo,\n\n', 1),
	(13, 'Onboarding Begleiter Arbeitsplatz einrichten', 'Arbeitsplatz für [NEWBIE]', '', 'Hallo,', 1),
	(8, 'Onboarding Infomail Abteilungsleitung', 'Neuer Mitarbeiter als [JOB] am  [STARTDATE]', '', 'Hallo [NAME],\n\nam [STARTDATUM] wird ein neuer Kollege am Standort [LOCATION] als [JOB] seine Tätigkeit aufnehmen.\n\nBitte bestätigen sie unter diesem Link die Kenntnisnahme!\n\nViele Grüße\n[MITARBEITER]', 1),
	(9, 'Onboarding Infomail an die Standortleitung', 'Neuer Mitarbeiter am [LOCATION] am [STARTDATE]', '', 'Hallo [NAME],\n\nam [STARTDATUM] wird ein neuer Kollege am Standort [LOCATION] als [JOB] seine Tätigkeit aufnehmen.\n\nBitte bestätigen sie unter diesem Link die Kenntnisnahme!\n\nViele Grüße\n[MITARBEITER]', 1),
	(14, 'Onboarding Newbie Schulung Arbeitsschutz', 'Eine Unterweisung wartet auf dich', '', 'Hallo,\n\n', 1),
	(15, 'Onboarding Newbie Schulung DSGV', 'Eine Unterweisung wartet auf dich', '', 'Hallo,\n\n', 1),
	(16, 'Onboarding Begleiter Newbie Begrüßung', 'Bicht Vergessen dein [NEWBIE] kommt [STARTDATE]', '', 'Hallo,', 1),
	(11, 'Onboarding Begrüßung an Newbie', 'Willkommen im Team', '', 'Hallo [NAME],\n\nwir freuen uns sie am [STARTDATUM] als neuen Kollegen am Standort [LOCATION] als [JOB] begrüßen zu dürfen.\n\nWir halten sie auf diesem Wege auf Stand um einen reibungslosen Start in den neuen Job zu gewährleisten\n\nViele Grüße\n[MITARBEITER]', 1),
	(1, 'Infomail an BZ Leitung Mitarbeiterzugang', 'Mitarbeiterzugang [STARTDATE]', '', 'Hallo [NAME],\n\nich hoffe, es geht Ihnen gut! Ich möchte Ihnen ganz herzlich zu Ihrer neuen Position als Ausbilder im [LOCATION] als [JOB] gratulieren. Das ist wirklich eine großartige Neuigkeit! Ich bin überzeugt, dass Sie mit Ihrem Engagement und Ihrer Erfahrung das Team bereichern und einen wertvollen Beitrag leisten werden. Für Ihren Start wünsche ich Ihnen viel Freude und Erfolg und freue mich auf die Zusammenarbeit.\n\nViele Grüße\n[MITARBEITER]', 1),
	(10, 'Reminder Verpasste Aufgabe', '[THEME]: Reminder verpasste Aufgabe', '', 'Hallo [NAME],\n\nim Rahmen des [THEME] steht noch eine Aufgabe offen.\n\nBitte bestätigen sie unter diesem Link die Kenntnisnahme!\n\nViele Grüße\n[MITARBEITER]', 1),
	(12, 'Onboarding Abteilungsleitung Begleiter bestimmen', 'Bgleitung für neuen Mitarbeiter', '', 'Hallo,\n\n', 1),
	(13, 'Onboarding Begleiter Arbeitsplatz einrichten', 'Arbeitsplatz für [NEWBIE]', '', 'Hallo,', 1),
	(8, 'Onboarding Infomail Abteilungsleitung', 'Neuer Mitarbeiter als [JOB] am  [STARTDATE]', '', 'Hallo [NAME],\n\nam [STARTDATUM] wird ein neuer Kollege am Standort [LOCATION] als [JOB] seine Tätigkeit aufnehmen.\n\nBitte bestätigen sie unter diesem Link die Kenntnisnahme!\n\nViele Grüße\n[MITARBEITER]', 1),
	(9, 'Onboarding Infomail an die Standortleitung', 'Neuer Mitarbeiter am [LOCATION] am [STARTDATE]', '', 'Hallo [NAME],\n\nam [STARTDATUM] wird ein neuer Kollege am Standort [LOCATION] als [JOB] seine Tätigkeit aufnehmen.\n\nBitte bestätigen sie unter diesem Link die Kenntnisnahme!\n\nViele Grüße\n[MITARBEITER]', 1),
	(14, 'Onboarding Newbie Schulung Arbeitsschutz', 'Eine Unterweisung wartet auf dich', '', 'Hallo,\n\n', 1),
	(15, 'Onboarding Newbie Schulung DSGV', 'Eine Unterweisung wartet auf dich', '', 'Hallo,\n\n', 1),
	(16, 'Onboarding Begleiter Newbie Begrüßung', 'Bicht Vergessen dein [NEWBIE] kommt [STARTDATE]', '', 'Hallo,', 1);

-- Exportiere Struktur von Tabelle kbd_hr_boarding.employees
DROP TABLE IF EXISTS `employees`;
CREATE TABLE IF NOT EXISTS `employees` (
  `id` bigint(20) NOT NULL,
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
  `department` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.employees: ~7 rows (ungefähr)
DELETE FROM `employees`;
INSERT INTO `employees` (`id`, `employee_number`, `first_name`, `last_name`, `email_business`, `email_private`, `username`, `password_hash`, `location_id`, `job_id`, `role_id`, `function_id`, `active`, `created_at`, `department`) VALUES
	(5, '1002', 'Jörg', 'Roßmannek', 'joerg.rossmannek@kolping-bildung-deutschland.de', NULL, 'jrossmannek', '', 1, 3, 3, 2, 1, '2026-08-12 11:45:38', 'IT'),
	(6, '1003', 'Jens', 'Urban', 'jens.urban@kolping-bildung-deutschland.de', NULL, 'jurban', '', 1, 2, 4, 1, 1, '2026-08-12 11:45:38', 'IT'),
	(7, NULL, 'Jan', 'Winter', 'jan.winter@kolping-bildung-deutschland.de', NULL, 'jwinter', '', 1, 1, 3, 2, 1, '2026-08-13 09:40:00', 'IT'),
	(4, '1001', 'Frank', 'Nöthe', 'frank.noethe@kolping-bildung-deutschland.de', 'frank.noethe@gmail.com', 'fnoethe', '', 1, 1, 1, 1, 1, '2026-08-12 11:45:38', 'IT'),
	(8, NULL, 'Thomas', 'Honrath', 'thomas.honrath@kolping-bildung-deutschland.de', NULL, 'thonrath', '', 1, 1, 4, 2, 1, '2026-08-13 13:37:13', 'IT'),
	(9, NULL, 'New', 'Bie', 'new.bie@gmail.com', NULL, '', '', 3, 8, 4, 3, 1, '2026-08-15 16:48:43', ''),
	(10, NULL, 'Neuer', 'Mitarbeiter', 'a@b.de', NULL, 'neuer.mitarbeiter', '', 3, 11, 4, 3, 1, '2026-08-18 08:02:15', 'Teszabteilung in Mitarbeiter festgelegt');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.functions
DROP TABLE IF EXISTS `functions`;
CREATE TABLE IF NOT EXISTS `functions` (
  `id` bigint(20) NOT NULL,
  `name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.functions: ~5 rows (ungefähr)
DELETE FROM `functions`;
INSERT INTO `functions` (`id`, `name`) VALUES
	(1, 'Verantwortlicher'),
	(2, 'Begleitung'),
	(4, 'Abteilungsleitung'),
	(3, 'Newbie'),
	(5, 'BZ Leitung');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.jobs
DROP TABLE IF EXISTS `jobs`;
CREATE TABLE IF NOT EXISTS `jobs` (
  `id` bigint(20) NOT NULL,
  `location_id` tinyint(4) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.jobs: ~11 rows (ungefähr)
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
	(11, 3, 'Ausbilder');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.locations
DROP TABLE IF EXISTS `locations`;
CREATE TABLE IF NOT EXISTS `locations` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.locations: ~7 rows (ungefähr)
DELETE FROM `locations`;
INSERT INTO `locations` (`id`, `name`, `active`) VALUES
	(1, 'HV Recklinghausen', 1),
	(2, 'HV Essen', 1),
	(3, 'BZ Essen', 1),
	(5, 'PS Recklinghausen', 1),
	(6, 'PS Dortmund', 1),
	(4, 'BZ Dortmund', 1),
	(8, 'BZ Recklinghausen', 1);

-- Exportiere Struktur von Tabelle kbd_hr_boarding.notification_queue
DROP TABLE IF EXISTS `notification_queue`;
CREATE TABLE IF NOT EXISTS `notification_queue` (
  `id` bigint(20) NOT NULL,
  `task_id` tinyint(4) DEFAULT NULL,
  `recipient_email` varchar(255) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `body_html` text DEFAULT NULL,
  `send_at` timestamp NULL DEFAULT NULL,
  `sent_at` timestamp NULL DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.notification_queue: ~0 rows (ungefähr)
DELETE FROM `notification_queue`;

-- Exportiere Struktur von Tabelle kbd_hr_boarding.process_cases
DROP TABLE IF EXISTS `process_cases`;
CREATE TABLE IF NOT EXISTS `process_cases` (
  `id` tinyint(4) NOT NULL,
  `employee_id` tinyint(4) DEFAULT NULL,
  `template_id` tinyint(4) DEFAULT NULL,
  `start_date` date NOT NULL,
  `status` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.process_cases: ~2 rows (ungefähr)
DELETE FROM `process_cases`;
INSERT INTO `process_cases` (`id`, `employee_id`, `template_id`, `start_date`, `status`, `created_at`) VALUES
	(1, 9, 1, '2026-09-15', 'OPEN', '2026-08-15 16:55:20'),
	(3, 10, 6, '2026-10-01', 'OPEN', '2026-08-18 08:17:06');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.process_types
DROP TABLE IF EXISTS `process_types`;
CREATE TABLE IF NOT EXISTS `process_types` (
  `id` bigint(20) NOT NULL,
  `name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.process_types: ~3 rows (ungefähr)
DELETE FROM `process_types`;
INSERT INTO `process_types` (`id`, `name`) VALUES
	(1, 'Onboarding'),
	(2, 'Reboarding'),
	(3, 'Offboarding');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.roles
DROP TABLE IF EXISTS `roles`;
CREATE TABLE IF NOT EXISTS `roles` (
  `id` bigint(20) NOT NULL,
  `name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.roles: ~5 rows (ungefähr)
DELETE FROM `roles`;
INSERT INTO `roles` (`id`, `name`) VALUES
	(1, 'Admin'),
	(2, 'HR'),
	(3, 'Manager'),
	(4, 'User'),
	(5, 'Newbie');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.tasks
DROP TABLE IF EXISTS `tasks`;
CREATE TABLE IF NOT EXISTS `tasks` (
  `id` bigint(20) NOT NULL,
  `process_case_id` tinyint(4) DEFAULT NULL,
  `template_task_id` tinyint(4) DEFAULT NULL,
  `assigned_to` tinyint(4) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `completed_at` timestamp NULL DEFAULT NULL,
  `completed_by` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.tasks: ~0 rows (ungefähr)
DELETE FROM `tasks`;

-- Exportiere Struktur von Tabelle kbd_hr_boarding.task_history
DROP TABLE IF EXISTS `task_history`;
CREATE TABLE IF NOT EXISTS `task_history` (
  `id` bigint(20) NOT NULL,
  `task_id` tinyint(4) DEFAULT NULL,
  `action` varchar(100) DEFAULT NULL,
  `old_status` varchar(50) DEFAULT NULL,
  `new_status` varchar(50) DEFAULT NULL,
  `changed_by` tinyint(4) DEFAULT NULL,
  `changed_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.task_history: ~0 rows (ungefähr)
DELETE FROM `task_history`;

-- Exportiere Struktur von Tabelle kbd_hr_boarding.task_reminders
DROP TABLE IF EXISTS `task_reminders`;
CREATE TABLE IF NOT EXISTS `task_reminders` (
  `id` bigint(20) NOT NULL,
  `task_id` tinyint(4) DEFAULT NULL,
  `reminder_date` timestamp NULL DEFAULT NULL,
  `sent` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.task_reminders: ~0 rows (ungefähr)
DELETE FROM `task_reminders`;

-- Exportiere Struktur von Tabelle kbd_hr_boarding.templates
DROP TABLE IF EXISTS `templates`;
CREATE TABLE IF NOT EXISTS `templates` (
  `id` bigint(20) NOT NULL,
  `process_type_id` tinyint(4) DEFAULT NULL,
  `location_id` tinyint(4) DEFAULT NULL,
  `job_id` tinyint(4) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.templates: ~4 rows (ungefähr)
DELETE FROM `templates`;
INSERT INTO `templates` (`id`, `process_type_id`, `location_id`, `job_id`, `name`, `active`, `created_at`) VALUES
	(5, 1, 1, 1, 'HV Recklinghausen IT-Systemadmin', 1, '2026-08-17 09:55:26'),
	(6, 1, 3, 11, 'Ausbilder Mechatroniker', 1, '2026-08-18 06:08:10'),
	(4, 1, 3, 7, 'Ausbilder TPD', 1, '2026-08-15 18:03:04'),
	(1, 1, 3, 6, 'Ausbilder Mechatronik', 1, '2026-08-15 17:16:51');

-- Exportiere Struktur von Tabelle kbd_hr_boarding.template_tasks
DROP TABLE IF EXISTS `template_tasks`;
CREATE TABLE IF NOT EXISTS `template_tasks` (
  `id` bigint(20) NOT NULL,
  `template_id` tinyint(4) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `responsible_function_id` tinyint(4) DEFAULT NULL,
  `due_offset_days` tinyint(4) NOT NULL,
  `email_template_id` tinyint(4) DEFAULT NULL,
  `mandatory` tinyint(1) DEFAULT NULL,
  `step` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Exportiere Daten aus Tabelle kbd_hr_boarding.template_tasks: ~6 rows (ungefähr)
DELETE FROM `template_tasks`;
INSERT INTO `template_tasks` (`id`, `template_id`, `title`, `description`, `responsible_function_id`, `due_offset_days`, `email_template_id`, `mandatory`, `step`) VALUES
	(34, 6, 'Newbie Begrüßung', 'Der Newbie wird über sein Einstellungsdatum und diesem Prozessstart informiert.', 3, 0, 7, 0, 1),
	(1, 1, 'Begrüssungsmail', 'Der neue Mitarbeiter ergält eine Nachricht darüber das er Registriert wurde und wie es nun weitergeht', 3, 0, 1, 1, 3),
	(35, 6, 'Betriebsleitung über Newbie', 'Die BZ-Leitung über den Starttermin des Newbies informieren', 5, 0, 1, 0, 2),
	(3, 1, 'Mail an die Abteilungsleitung', 'Info darüber das ein neuer Mitarbeiter für sein BZ registriert wurde.', 4, 0, 8, 1, 1),
	(13, 1, 'Test Aufgabe', 'Beschreibung', 4, 3, 7, 1, 1),
	(2, 1, 'Mail an die BZ Leitung', 'Info darüber das ein neuer Mitarbeiter für sein BZ registriert wurde', 5, 1, 7, 1, 2);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
