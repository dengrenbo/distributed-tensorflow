CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `password` varchar(512) NOT NULL,
  `email` varchar(255) DEFAULT foo@bar.com,
  `status` tinyint(1) DEFAULT 1,
  `priority` int(11) DEFAULT 1,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
)

