{{ config(
  materialized='table',
  unique_key='Team'
) }}

SELECT 
    Team AS team_name
FROM final_project.points_table