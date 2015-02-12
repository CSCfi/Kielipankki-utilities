CREATE TABLE IF NOT EXISTS `relations_@CORPNAME@` (
        `id` int(11) UNIQUE NOT NULL,
	`head` varchar(100) NOT NULL,
	`rel` char(3) NOT NULL,
	`dep` varchar(100) NOT NULL,
	`depextra` varchar(32) DEFAULT NULL,
	`freq` int(11) NOT NULL,
	`wf` tinyint(4) NOT NULL,
	PRIMARY KEY (`id`),
	KEY `head` (`head`),
	KEY `dep` (`dep`)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 DEFAULT COLLATE=utf8_bin;
CREATE TABLE IF NOT EXISTS `relations_@CORPNAME@_rel` (
	`rel` char(3) NOT NULL,
	`freq` int(11) NOT NULL,
	KEY `rel` (`rel`)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 DEFAULT COLLATE=utf8_bin;
CREATE TABLE IF NOT EXISTS `relations_@CORPNAME@_head_rel` (
	`head` varchar(100) NOT NULL,
	`rel` char(3) NOT NULL,
	`freq` int(11) NOT NULL,
	KEY `head` (`head`),
	KEY `rel` (`rel`)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 DEFAULT COLLATE=utf8_bin;
CREATE TABLE IF NOT EXISTS `relations_@CORPNAME@_dep_rel` (
	`dep` varchar(100) NOT NULL,
	`depextra` varchar(32) DEFAULT NULL,
	`rel` char(3) NOT NULL,
	`freq` int(11) NOT NULL,
	KEY `dep` (`dep`),
	KEY `rel` (`rel`)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 DEFAULT COLLATE=utf8_bin;
CREATE TABLE IF NOT EXISTS `relations_@CORPNAME@_sentences` (
        `id` int(11) NOT NULL,
	`sentence` varchar(64) NOT NULL,
	`start` int(11) NOT NULL,
	`end` int(11) NOT NULL,
	KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 DEFAULT COLLATE=utf8_bin;
