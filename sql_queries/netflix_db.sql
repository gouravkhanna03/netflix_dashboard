CREATE DATABASE netftlix_db;

CREATE TABLE netflix_data(
						    show_id INT PRIMARY KEY,
						    type TEXT NOT NULL,
						    title VARCHAR(5),
						    director TEXT,
						    "cast" TEXT,
						    country TEXT,
						    date_added DATE,
						    release_year INT,
						    rating NUMERIC(10, 2),
						    genres TEXT,
						    "language" VARCHAR(5),
						    description TEXT,
						    popularity TEXT,
						    vote_count INT,
						    vote_average NUMERIC(10, 2),
						    budget INT,
						    revenue INT,
						    poster_url TEXT
);



CREATE TABLE revenue_summary(
											"month" TEXT,
											total_users INT,
											new_signups INT,
											cancellations INT,
											total_revenue INT
);


CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    signup_date DATE,
    country TEXT,
    age_group TEXT,
    device_type TEXT
);


CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    plan_type TEXT,
    monthly_fee INT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(9)
);



CREATE TABLE watch_history (
						    history_id SERIAL PRIMARY KEY,
						    user_id INT REFERENCES users(user_id),
						    show_id INT REFERENCES netflix_data(show_id),
						    watch_date DATE,
						    watch_duration_mins INT,
						    device_type VARCHAR(7)
);


ALTER TABLE netflix_data
ALTER COLUMN title TYPE TEXT;

ALTER TABLE netflix_data
ALTER COLUMN revenue TYPE BIGINT,
ALTER COLUMN budget TYPE BIGINT;



SELECT conname
FROM pg_constraint
WHERE conrelid = 'users'::regclass AND contype = 'u';

ALTER TABLE users DROP CONSTRAINT users_email_key;
--------------------------------------------------------------------------------------------------------------------------------

SELECT *
FROM netflix_data;


COPY netflix_data
FROM 'C:/netflix_data.csv'
DELIMITER ','
CSV HEADER;


-- ALLL TABLES
SELECT *
FROM netflix_data;

SELECT *
FROM revenue_summary;

SELECT *
FROM users;

SELECT *
FROM subscriptions;

SELECT *
FROM watch_history;


----------------------------
-- DATA CLEANING


SELECT COUNT(*) FILTER (WHERE show_id IS NULL) AS show_id,
       COUNT(*) FILTER (WHERE type IS NULL) AS type,
			 COUNT(*) FILTER (WHERE title IS NULL) AS title,
       COUNT(*) FILTER (WHERE director IS NULL) AS director,
			 COUNT(*) FILTER (WHERE "cast" IS NULL) AS cast,
			 COUNT(*) FILTER (WHERE country IS NULL) AS country,
			 COUNT(*) FILTER (WHERE date_added IS NULL) AS date_added,
			 COUNT(*) FILTER (WHERE release_year IS NULL) AS release_year,
			 COUNT(*) FILTER (WHERE rating IS NULL) AS rating,
			 COUNT(*) FILTER (WHERE genres IS NULL) AS genres,
			 COUNT(*) FILTER (WHERE language IS NULL) AS language,
			 COUNT(*) FILTER (WHERE description IS NULL) AS description,
			 COUNT(*) FILTER (WHERE popularity IS NULL) AS popularity,
			 COUNT(*) FILTER (WHERE vote_count IS NULL) AS vote_count,
			 COUNT(*) FILTER (WHERE vote_average IS NULL) AS vote_average,
			 COUNT(*) FILTER (WHERE budget IS NULL) AS budget,
			 COUNT(*) FILTER (WHERE revenue IS NULL) AS revenue,
			 COUNT(*) FILTER (WHERE poster_url IS NULL) AS poster_url
FROM netflix_data;


-- creating FUNCTION
CREATE OR REPLACE FUNCTION first_3_genres(genres TEXT)
RETURNS TEXT AS $$
BEGIN
  RETURN (
    SELECT string_agg(part, ', ')
    FROM (
      SELECT part
      FROM unnest(string_to_array(genres, ', ')) AS part
      LIMIT 3
    ) AS limited
  );
END;
$$ LANGUAGE plpgsql;

-- netflix_data table without NULL
CREATE OR REPLACE VIEW netflix_data_2
AS
SELECT *,
    split_part(genres, ',', 1) AS extracted_genres,
		first_3_genres(genres) AS top_genres,
		CASE
			WHEN rating= 0.00 THEN 'Not Rated'
			ELSE rating::text
		END rating_revised,
		CAST((release_year/10)*10 AS INTEGER) AS decade
FROM netflix_data
WHERE director IS NOT NULL
  AND "cast" IS NOT NULL
  AND country IS NOT NULL
  AND genres IS NOT NULL
  AND description IS NOT NULL
  AND poster_url IS NOT NULL;



-- watch_history table with show_id in netflix_data table
CREATE OR REPLACE VIEW watch_history_2 
AS
SELECT *,
      TO_CHAR(watch_date, 'DDD') AS watch_day,
			EXTRACT(DOW FROM watch_date) AS day_of_week
FROM watch_history
WHERE show_id IN (
		SELECT show_id
		FROM netflix_data
		WHERE director IS NOT NULL
		  AND "cast" IS NOT NULL
		  AND country IS NOT NULL
		  AND genres IS NOT NULL
		  AND description IS NOT NULL
		  AND poster_url IS NOT NULL
);


ALTER DATABASE netftlix_db RENAME TO netflix_db;


SELECT rating,
       
FROM netflix_data
ORDER BY 1;



--- decade to show in pbi visual silcer
SELECT ROUND((release_year/10)*10) AS decade
FROM netflix_data;


-- user by age GROUP
WITH age_users AS(
	SELECT COUNT(*) AS users,
	       age_group
	FROM users
	GROUP BY age_group
),
	total_users AS (
	SELECT COUNT(*) AS total_user
	FROM age_users
)
SELECT age_group,
       users,
			 (total_user/users)*100 AS total_ratio
FROM age_users AS a
INNER JOIN total_users AS




WITH age_summary AS (
  SELECT 
    age_group,
    COUNT(*) AS users_by_age
  FROM users
  GROUP BY age_group
),
total_users AS (
  SELECT SUM(users_by_age) AS total FROM age_summary
)
SELECT 
  a.age_group,
  a.users_by_age,
  ROUND((a.users_by_age / t.total) * 100, 2) AS to_user_percentage
FROM age_summary a
CROSS JOIN total_users t
ORDER BY to_user_percentage DESC;