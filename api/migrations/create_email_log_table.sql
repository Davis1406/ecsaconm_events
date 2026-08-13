-- Email log table — records every outbound email (system + admin-triggered)
-- for the "Sent Emails" admin view. Includes open-tracking via a pixel and
-- the rendered HTML body so a log entry can be re-viewed later.
CREATE TABLE IF NOT EXISTS `email_log` (
  `id`               INT            NOT NULL AUTO_INCREMENT,
  `recipient_email`  VARCHAR(255)   NOT NULL,
  `subject`          VARCHAR(500)   NOT NULL,
  `email_type`       VARCHAR(100)   NOT NULL,
  `sent_by_user_id`  INT            NULL,
  `reply_to_email`   VARCHAR(255)   NULL,
  `status`           VARCHAR(20)    NOT NULL DEFAULT 'sent',
  `error_message`    TEXT           NULL,
  `body`             LONGTEXT       NULL,
  `opened_at`        TIMESTAMP      NULL,
  `opened_count`     INT            NOT NULL DEFAULT 0,
  `sent_at`          TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_email_log_sent_at` (`sent_at`),
  KEY `ix_email_log_type`    (`email_type`),
  CONSTRAINT `fk_email_log_user` FOREIGN KEY (`sent_by_user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
