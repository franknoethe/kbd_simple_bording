CREATE TABLE IF NOT EXISTS tasks (
    id INT NOT NULL AUTO_INCREMENT,
    employee_id BIGINT NOT NULL,
    template_task_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    status ENUM('open', 'in_progress', 'completed') NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reminder_sent_at TIMESTAMP NULL DEFAULT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_tasks_employee FOREIGN KEY (employee_id) REFERENCES employees (id),
    CONSTRAINT fk_tasks_template_task FOREIGN KEY (template_task_id) REFERENCES template_tasks (id),
    INDEX idx_tasks_due_date (due_date, status, reminder_sent_at)
);