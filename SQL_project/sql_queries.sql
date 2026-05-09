--Output the number of movies in each category, sorted descending.

SELECT c.name AS category, COUNT(c.category_id) AS number
FROM film AS f
INNER JOIN film_category AS fc ON f.film_id = fc.film_id
INNER JOIN category AS c ON fc.category_id = c.category_id
GROUP BY category
ORDER BY number DESC

-- Output the 10 actors whose movies rented the most, sorted in descending order.

SELECT a.actor_id, CONCAT(a.first_name, ' ', a.last_name) AS full_name, COUNT(r.rental_id) AS rental_count
FROM film AS f
INNER JOIN film_actor AS fa ON f.film_id = fa.film_id
INNER JOIN actor AS a ON a.actor_id = fa.actor_id
INNER JOIN inventory AS i ON f.film_id = i.film_id
INNER JOIN rental AS r ON r.inventory_id = i.inventory_id
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY rental_count DESC
LIMIT 10;

-- Output the category of movies on which the most money was spent.

SELECT c.name AS category, SUM(p.amount) AS payment
FROM payment AS p
INNER JOIN rental AS r ON p.rental_id = r.rental_id
INNER JOIN inventory AS i ON r.inventory_id = i.inventory_id
INNER JOIN film_category AS fc ON i.film_id = fc.film_id
INNER JOIN category AS c ON fc.category_id = c.category_id
GROUP BY category
ORDER BY payment DESC
LIMIT 1

-- Print the names of movies that are not in the inventory. Write a query without using the IN operator.

SELECT f.title
FROM film AS f
LEFT JOIN inventory AS i ON f.film_id = i.film_id
WHERE i.inventory_id IS NULL;

-- Output the top 3 actors who have appeared the most in movies in the “Children” category. If several actors have the same number of movies, output all of them.

/* ---DOES NOT WORK COMPLETELY. ONLY SHOW TOP3 BUT NEED TO SHOW ALL THE RESULT IF EQUAL VALUE-------------------
SELECT a.actor_id, CONCAT(a.first_name, ' ', a.last_name) AS actor_name, COUNT(c.name) AS cat_name 
FROM actor AS a 
INNER JOIN film_actor AS fa ON a.actor_id = fa.actor_id 
INNER JOIN film_category AS fc ON fa.film_id = fc.film_id 
INNER JOIN category AS c ON fc.category_id = c.category_id 
WHERE c.name='Children' 
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY cat_name DESC
LIMIT 3
*/

WITH actor_counts_all AS (
    SELECT a.actor_id, CONCAT(a.first_name, ' ', a.last_name) AS actor_name, COUNT(c.name) AS movie_count
    FROM actor AS a
    INNER JOIN film_actor AS fa ON a.actor_id = fa.actor_id
    INNER JOIN film_category AS fc ON fa.film_id = fc.film_id
    INNER JOIN category AS c ON fc.category_id = c.category_id
    WHERE c.name = 'Children'
    GROUP BY a.actor_id
)
SELECT actor_name, movie_count
FROM actor_counts_all
WHERE movie_count >= (
    SELECT MIN(movie_count)
    FROM (
        SELECT movie_count
        FROM actor_counts_all
        ORDER BY movie_count DESC
        LIMIT 3
    ) AS top3
)
ORDER BY movie_count DESC;

-- Output cities with the number of active and inactive customers (active - customer.active = 1). Sort by the number of inactive customers in descending order.

SELECT city.city, 
COUNT(*) FILTER (WHERE customer.active = 1) AS active_customer,
COUNT(*) FILTER (WHERE customer.active = 0) AS inactive_customer
FROM city
INNER JOIN address ON city.city_id = address.city_id
INNER JOIN customer ON address.address_id = customer.address_id
GROUP BY city.city
ORDER BY inactive_customer DESC

-- Output the category of movies that have the highest number of total rental hours in the city (customer.address_id in this city) and that start with the letter “a”. Do the same for cities that have a “-” in them. Write everything in one query.

WITH supporting_table AS (
	SELECT city.city AS city_name, cat.name AS category_name, SUM(FLOOR(EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) / 3600)) AS total_hours
	FROM rental r
	INNER JOIN customer c ON r.customer_id = c.customer_id
	INNER JOIN address a ON c.address_id = a.address_id
	INNER JOIN city ON a.city_id = city.city_id
	INNER JOIN inventory i ON r.inventory_id = i.inventory_id
	INNER JOIN film f ON i.film_id = f.film_id
	INNER JOIN film_category fc ON f.film_id = fc.film_id
	INNER JOIN category cat ON fc.category_id = cat.category_id
	WHERE (city.city ILIKE 'a%' OR city.city LIKE '%-%') AND r.return_date IS NOT NULL
	GROUP BY city.city, cat.name
)
SELECT city_name, category_name, total_hours
FROM (
    SELECT *,
           RANK() OVER (PARTITION BY city_name ORDER BY total_hours DESC) AS rank
    FROM supporting_table
) AS ranked_table
WHERE rank = 1
ORDER BY total_hours DESC