ALTER TABLE tasks
    ADD COLUMN email_template_id BIGINT NULL,
    ADD CONSTRAINT fk_tasks_email_template
        FOREIGN KEY (email_template_id) REFERENCES email_templates (id)
        ON DELETE SET NULL;