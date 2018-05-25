-- --------------------------------------------------------
-- Host:                         arwen
-- Server version:               5.5.60-0ubuntu0.14.04.1 - (Ubuntu)
-- Server OS:                    debian-linux-gnu
-- HeidiSQL Version:             9.4.0.5125
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for rsspy
CREATE DATABASE IF NOT EXISTS `rsspy` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `rsspy`;

-- Dumping structure for table rsspy.bookmark
CREATE TABLE IF NOT EXISTS `bookmark` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `userID` int(10) unsigned NOT NULL DEFAULT '0',
  `entryID` int(10) unsigned NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `only_one` (`entryID`,`userID`),
  KEY `user` (`userID`),
  KEY `entry` (`entryID`),
  CONSTRAINT `FK_bookmark_user` FOREIGN KEY (`userID`) REFERENCES `user` (`ID`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8 COMMENT='holds bookmarks, favourite, likes ..';

-- Data exporting was unselected.
-- Dumping structure for table rsspy.entry
CREATE TABLE IF NOT EXISTS `entry` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `feedID` int(10) unsigned NOT NULL DEFAULT '0',
  `title` varchar(255) DEFAULT NULL,
  `description` mediumtext,
  `contents` mediumtext,
  `url` varchar(255) DEFAULT NULL,
  `guid` varchar(255) DEFAULT NULL,
  `last_update` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `item_created` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `published` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `published` (`published`),
  KEY `FK__feed` (`feedID`),
  CONSTRAINT `FK__feed` FOREIGN KEY (`feedID`) REFERENCES `feed` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=28125 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table rsspy.feed
CREATE TABLE IF NOT EXISTS `feed` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text,
  `update_interval` int(11) DEFAULT '60',
  `feed_last_update` timestamp NULL DEFAULT NULL,
  `web_url` varchar(255) DEFAULT NULL,
  `last_update` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `active` tinyint(4) DEFAULT '1',
  `request_options` text,
  PRIMARY KEY (`ID`),
  KEY `url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table rsspy.group
CREATE TABLE IF NOT EXISTS `group` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `description` text,
  `userID` int(10) unsigned DEFAULT NULL,
  `aggregation` varchar(50) DEFAULT NULL,
  `frequency` int(11) DEFAULT NULL,
  `last_sent` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `issue` int(7) DEFAULT '1',
  PRIMARY KEY (`ID`),
  KEY `FK_group_user` (`userID`),
  CONSTRAINT `FK_group_user` FOREIGN KEY (`userID`) REFERENCES `user` (`ID`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
-- Dumping structure for table rsspy.group_feed
CREATE TABLE IF NOT EXISTS `group_feed` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `groupID` int(10) unsigned NOT NULL DEFAULT '0',
  `feedID` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `only_one` (`groupID`,`feedID`),
  KEY `FK_group_feed_feed` (`feedID`),
  CONSTRAINT `FK_group_feed_feed` FOREIGN KEY (`feedID`) REFERENCES `feed` (`ID`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_group_feed_group` FOREIGN KEY (`groupID`) REFERENCES `group` (`ID`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8 COMMENT='Links feeds to users by means of groups';

-- Data exporting was unselected.
-- Dumping structure for table rsspy.user
CREATE TABLE IF NOT EXISTS `user` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `lastvisit` varchar(255) DEFAULT NULL,
  `das_hash` varchar(128) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
