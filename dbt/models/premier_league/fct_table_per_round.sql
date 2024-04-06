{{ config(
  materialized='table'
) }}

WITH match_data AS (
    SELECT 
        *
      , CASE WHEN HomeTeam_goals > AwayTeam_goals THEN 3 
             WHEN HomeTeam_goals < AwayTeam_goals THEN 0 
             WHEN HomeTeam_goals = AwayTeam_goals THEN 1
        END HomeTeam_points_gained
      , CASE WHEN HomeTeam_goals < AwayTeam_goals THEN 3 
             WHEN HomeTeam_goals > AwayTeam_goals THEN 0 
             WHEN HomeTeam_goals = AwayTeam_goals THEN 1
        END AwayTeam_points_gained
    FROM {{ ref('dim_match_data') }}
    ORDER BY 1
)

, home_team_data AS (
    SELECT 
      match_data.Date
    , match_data.HomeTeam AS Team
    , match_data.HomeTeam_points_gained AS points
    FROM match_data
    ORDER BY 1
)

, away_team_data AS (
    SELECT 
      match_data.Date
    , match_data.AwayTeam AS Team
    , match_data.AwayTeam_points_gained AS points
    FROM match_data
    ORDER BY 1
)

SELECT *
FROM home_team_data
UNION ALL 
SELECT  *
FROM away_team_data