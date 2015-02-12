CREATE TABLE `lemgram_index` (
  `lemgram` varchar(64) NOT NULL,
  `freq` int(11) DEFAULT NULL,
  `freqprefix` int(11) DEFAULT NULL,
  `freqsuffix` int(11) DEFAULT NULL,
  `corpus` varchar(64) NOT NULL,
  UNIQUE KEY `lemgram_corpus` (`lemgram`, `corpus`),
  KEY `lemgram` (`lemgram`),
  KEY `corpus` (`corpus`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
