-- 1. Tickets per assignee and status (workload)
SELECT a.assignee_name, s.status_name, COUNT(*) AS tickets
FROM fact_tickets f
JOIN dim_assignee a ON a.assignee_id = f.assignee_id
JOIN dim_status s   ON s.status_id   = f.status_id
GROUP BY a.assignee_name, s.status_name
ORDER BY a.assignee_name, tickets DESC;

-- 2. Average resolution days per assignee, with rank (window function)
WITH resolved AS (
    SELECT a.assignee_name, AVG(f.resolution_days) AS avg_days
    FROM fact_tickets f
    JOIN dim_assignee a ON a.assignee_id = f.assignee_id
    WHERE f.resolution_days IS NOT NULL
    GROUP BY a.assignee_name
)
SELECT assignee_name, ROUND(avg_days, 1) AS avg_days,
       RANK() OVER (ORDER BY avg_days) AS speed_rank
FROM resolved;

-- 3. Overdue open tickets
SELECT issue_key, summary, due_date, a.assignee_name
FROM fact_tickets f
JOIN dim_assignee a ON a.assignee_id = f.assignee_id
WHERE f.is_overdue
ORDER BY due_date;

-- 4. Tickets created per week with running total (window function)
WITH weekly AS (
    SELECT DATE_TRUNC('week', created_at)::date AS week_start, COUNT(*) AS created
    FROM fact_tickets GROUP BY 1
)
SELECT week_start, created,
       SUM(created) OVER (ORDER BY week_start) AS running_total
FROM weekly ORDER BY week_start;
