PySpark Demo: Pagila Database Analysis

This project demonstrates the use of PySpark to perform data analysis on the Pagila demo database, which simulates a DVD rental business. The goal is to perform complex queries and aggregations using PySpark DataFrame operations and window functions — without using SQL syntax.

Project Features

The project includes code to:

Count movies by category
Output the number of movies in each category, sorted in descending order.
Top rented actors
Identify the 10 actors whose movies have been rented the most, sorted in descending order.
Category with highest revenue
Determine the category of movies on which the most money was spent.
Movies not in inventory
List all movie titles that are currently not in the inventory.
Top actors in the "Children" category
Find the top 3 actors who have appeared in the most “Children” category movies. If multiple actors have the same number of movies, all are included.
Customer activity by city
Output cities with the number of active and inactive customers (active customers have customer.active = 1), sorted by the number of inactive customers in descending order.
Top rental hours by category in selected cities
Identify the movie category with the highest total rental hours in cities whose names start with the letter “a” or contain a “-” symbol.

Technologies Used
PySpark: Data processing and analysis using DataFrames and window functions
Python 3.11
Pagila database: PostgreSQL-based DVD rental demo database
