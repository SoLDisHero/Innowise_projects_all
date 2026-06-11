from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window
spark = (
    SparkSession.builder
    .appName("PagilaSparkProject")
    .config(
        "spark.jars.packages",
        "org.postgresql:postgresql:42.7.3"
    )
    .getOrCreate()
)
# Generic function for tables

def choose_table(table_name):
    df = (
        spark.read.format("jdbc")
        .option("url", "jdbc:postgresql://localhost:5432/postgres")
        .option("dbtable", table_name)
        .option("user", "postgres")
        .option("password", "123456")
        .option("driver", "org.postgresql.Driver")
        .load()
    )
    return df

# table_option = ["actor", "address", "category", "city", "country", "customer", "film", "film_actor", "film_category",
#                 "inventory", "language", "payment", "rental", "staff", "store"]

# -------------------------------------QUERIES--------------------------------

# 1. Output the number of movies in each category, sorted in descending order.

film_df = choose_table('film')
film_category_df = choose_table('film_category')
category_df = choose_table('category')
query_1_join = (film_df
                .join(film_category_df, film_df.film_id == film_category_df.film_id, "inner")
                .join(category_df, category_df.category_id == film_category_df.category_id, "inner"))
query_1_result = (query_1_join
                  .groupBy(category_df.name)
                  .agg(F.count(category_df.category_id).alias("number"))
                  .orderBy("number", ascending=False)
                )

# query_1_result.show()

# 2. Output the 10 actors whose movies rented the most, sorted in descending order. 

film_actor_df = choose_table("film_actor")
actor_df = choose_table("actor")
inventory_df = choose_table("inventory")
rental_df = choose_table("rental")
query_2_join = (film_df
                .join(film_actor_df, film_actor_df.film_id == film_df.film_id, "inner")
                .join(actor_df, actor_df.actor_id == film_actor_df.actor_id, "inner")
                .join(inventory_df, inventory_df.film_id == film_df.film_id, "inner")
                .join(rental_df, rental_df.inventory_id == inventory_df.inventory_id, "inner"))
query_2_result = (query_2_join
                  .groupBy(actor_df.actor_id, F.concat_ws(" ", actor_df.first_name, actor_df.last_name))
                  .agg(F.count(rental_df.rental_id).alias("rental_count"))
                  .orderBy("rental_count", ascending=False)
                  .limit(10))

# query_2_result.show()

# 3. Output the category of movies on which the most money was spent. 

payment_df = choose_table("payment")
query_3_join = (payment_df
                .join(rental_df, rental_df.rental_id == payment_df.rental_id, "inner")
                .join(inventory_df, inventory_df.inventory_id == rental_df.inventory_id, "inner")
                .join(film_category_df, film_category_df.film_id == inventory_df.film_id, "inner")
                .join(category_df, category_df.category_id == film_category_df.category_id, "inner"))
query_3_result = (query_3_join
                  .groupBy(category_df.name)
                  .agg(F.sum(payment_df.amount).alias("payment"))
                  .orderBy("payment", ascending=False)
                  .limit(1))

# query_3_result.show()

# 4. Output the names of movies that are not in the inventory.

query_4_join = (film_df
                .join(inventory_df, "film_id", "left"))
query_4_result = (query_4_join
                  .filter(inventory_df.inventory_id.isNull())
                  .select(film_df.title))

# query_4_result.show()

# 5. Output the top 3 actors who have appeared most in movies in the “Children” category. 
# If several actors have the same number of movies, output all of them. 

query_5_join = (actor_df
                .join(film_actor_df, "actor_id", "inner")
                .join(film_category_df, "film_id", "inner")
                .join(category_df, "category_id", "inner"))

query_5_filter = (query_5_join
                  .filter(category_df.name == "Children")
                  .groupBy(actor_df.actor_id, F.concat_ws(" ", actor_df.first_name, actor_df.last_name))
                  .agg(F.count(category_df.name).alias("movie_count"))
                  )
top_3 = (query_5_filter
         .orderBy("movie_count")
         .limit(3)
         .agg(F.min("movie_count"))
         .collect()[0][0])
query_5_result = (query_5_filter
                  .filter(F.col("movie_count") >= top_3)
                  .orderBy("movie_count", ascending=False))

# query_5_result.show()

# 6. Output cities with the number of active and inactive customers (active - customer.active = 1). 
# Sort by the number of inactive customers in descending order. 

city_df = choose_table("city")
address_df = choose_table("address")
customer_df = choose_table("customer")
query_6_join = (city_df
                .join(address_df, "city_id", "inner")
                .join(customer_df, "address_id", "inner"))
query_6_result = (query_6_join
                  .groupBy(city_df.city)
                  .agg(F.sum(F.when(customer_df.active == 1, 1).otherwise(0)).alias("active_customer"),
                       F.sum(F.when(customer_df.active == 0, 1).otherwise(0)).alias("inactive_customer"))
                  .orderBy("inactive_customer", ascending=False))

# query_6_result.show()

# 7. Output the category of movies that have the highest number of total rental hours in the cities 
# (customer.address_id in this city), and that start with the letter “a”. Do the same for cities with a “-” symbol.

query_7_join = (rental_df
                .join(customer_df, "customer_id", "inner")
                .join(address_df, "address_id", "inner")
                .join(city_df, "city_id", "inner")
                .join(inventory_df, "inventory_id", "inner")
                .join(film_df, "film_id", "inner")
                .join(film_category_df, "film_id", "inner")
                .join(category_df, "category_id", "inner"))

query_7_filter = (query_7_join
                  .filter((F.col("city").like("%-%")) | (F.col("city").rlike("(?i)^a")))
                  .withColumn("rental_hours", F.floor((F.unix_timestamp("return_date") - F.unix_timestamp("rental_date")) / 3600))
                  .groupBy("city", "name")
                  .agg(F.sum("rental_hours").alias("total_hours")))

query_7_window = Window.partitionBy("city").orderBy(F.col("total_hours").desc())
query_7_rank = query_7_filter.withColumn("rank", F.rank().over(query_7_window))

query_7_result = (query_7_rank
                  .filter(F.col("rank") == 1)
                  .select("city", "name", "total_hours")
                  .orderBy("total_hours", ascending=False))

query_7_result.show()