from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum, to_date, weekofyear
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, DoubleType
import time

# Configuración del SparkSession
spark = SparkSession.builder \
    .appName("CSVDataTransformation") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
    .config("spark.hadoop.fs.s3a.access.key", "test") \
    .config("spark.hadoop.fs.s3a.secret.key", "test") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4") \
    .getOrCreate()


# Leer el archivo CSV
file_path = "s3a://bucket-1/CSV_Limpio/*.csv"
orders_df = spark.read.option("header", "true").csv(file_path)

# Asumiendo que ya tienes el DataFrame `orders_df` con la estructura mencionada

# 1. Obtener todas las órdenes de un usuario específico
user_id = 12345
orders_user = orders_df.filter(orders_df.user_id == user_id).select("order_id", "order_date", "total_amount")

# 2. Obtener la cantidad total de productos comprados por un usuario
total_quantity_user = orders_df.filter(orders_df.user_id == user_id) \
                               .groupBy("user_id") \
                               .agg(F.sum("quantity").alias("total_quantity"))

# 3. Obtener el total gastado por cada usuario
total_spent_by_user = orders_df.groupBy("user_id").agg(F.sum("total_amount").alias("total_spent"))

# 4. Listar los productos más vendidos por cantidad (ordenados de mayor a menor)
most_sold_products = orders_df.groupBy("order_item_id").agg(F.sum("quantity").alias("total_quantity")) \
                              .orderBy(F.desc("total_quantity"))

# 5. Obtener el total de ventas por país
total_sales_by_country = orders_df.groupBy("country").agg(F.sum("total_amount").alias("total_sales"))

# 6. Obtener la información de un pedido específico (por order_id)
order_id = 98765
order_info = orders_df.filter(orders_df.order_id == order_id).select("order_id", "order_date", "total_amount", 
                                                                     "order_item_id", "quantity", "unit_price", "username", "email")

# 7. Obtener la cantidad de productos y su total por order_id
order_summary = orders_df.groupBy("order_id").agg(F.sum("quantity").alias("total_quantity"), 
                                                  F.sum(orders_df.quantity * orders_df.unit_price).alias("total_order_amount"))

# 8. Listar todos los usuarios mayores de 30 años
users_over_30 = orders_df.filter(orders_df.age > 30).select("username", "email", "age")

# 9. Obtener el pedido más reciente de un usuario específico
latest_order_user = orders_df.filter(orders_df.user_id == user_id) \
                             .orderBy(F.desc("order_date")) \
                             .limit(1)

# 10. Obtener la cantidad total de productos por cada order_item_id
total_quantity_by_product = orders_df.groupBy("order_item_id").agg(F.sum("quantity").alias("total_quantity"))

# 11. Obtener el total de ventas por mes
sales_by_month = orders_df.withColumn("month", F.month("order_date")) \
                          .groupBy("month") \
                          .agg(F.sum("total_amount").alias("total_sales"))

# 12. Obtener los usuarios que han realizado al menos una compra por país
users_per_country = orders_df.groupBy("country").agg(F.countDistinct("user_id").alias("users_count"))

# 13. Listar los pedidos realizados en un rango de fechas
start_date = "2025-01-01"
end_date = "2025-03-31"
orders_in_range = orders_df.filter((orders_df.order_date >= start_date) & (orders_df.order_date <= end_date)) \
                           .select("order_id", "order_date", "total_amount")

# 14. Obtener los pedidos con un total_amount mayor a 100
high_value_orders = orders_df.filter(orders_df.total_amount > 100).select("order_id", "order_date", "total_amount")

# 15. Obtener el total de productos vendidos por cada usuario (usuario con más productos comprados)
total_quantity_per_user = orders_df.groupBy("user_id").agg(F.sum("quantity").alias("total_quantity")) \
                                   .orderBy(F.desc("total_quantity")) \
                                   .limit(1)

# 16. Obtener las ventas totales por día
sales_by_day = orders_df.groupBy("order_date").agg(F.sum("total_amount").alias("daily_sales"))

# 17. Obtener la cantidad de productos vendidos en un pedido específico (por order_id)
order_details = orders_df.filter(orders_df.order_id == order_id) \
                         .groupBy("order_id") \
                         .agg(F.sum("quantity").alias("total_quantity"))

# 18. Obtener los productos más caros en cada orden (por unit_price)
highest_price_products = orders_df.groupBy("order_id", "order_item_id") \
                                  .agg(F.max("unit_price").alias("highest_price"))

# 19. Listar todos los usuarios con sus edades y países
users_info = orders_df.select("username", "age", "country").distinct()

# 20. Obtener el total de ventas de un usuario en un período de tiempo
start_date = "2025-01-01"
end_date = "2025-12-31"
total_spent_period_user = orders_df.filter((orders_df.user_id == user_id) & 
                                           (orders_df.order_date >= start_date) & 
                                           (orders_df.order_date <= end_date)) \
                                   .groupBy("user_id") \
                                   .agg(F.sum("total_amount").alias("total_spent"))

# 21. Obtener el total de ventas de cada producto por mes
sales_by_product_month = orders_df.withColumn("month", F.month("order_date")) \
                                  .groupBy("order_item_id", "month") \
                                  .agg(F.sum("total_amount").alias("total_sales"))

# 22. Obtener el número total de productos vendidos en un trimestre
sales_by_quarter = orders_df.withColumn("quarter", F.quarter("order_date")) \
                            .groupBy("quarter") \
                            .agg(F.sum("quantity").alias("total_quantity"))

# 23. Listar los usuarios que han realizado más de 5 pedidos
users_more_than_5_orders = orders_df.groupBy("user_id") \
                                     .agg(F.count("order_id").alias("order_count")) \
                                     .filter("order_count > 5")

# 24. Obtener el total de ventas de cada producto con un precio unitario mayor a 30
sales_by_expensive_products = orders_df.filter(orders_df.unit_price > 30) \
                                       .groupBy("order_item_id") \
                                       .agg(F.sum("total_amount").alias("total_sales"))

# 25. Obtener los productos comprados por más de 10 usuarios distintos
popular_products = orders_df.groupBy("order_item_id") \
                            .agg(F.countDistinct("user_id").alias("distinct_users_count")) \
                            .filter("distinct_users_count > 10")

# 26. Obtener las ventas totales por año y producto
sales_by_year_product = orders_df.withColumn("year", F.year("order_date")) \
                                 .groupBy("year", "order_item_id") \
                                 .agg(F.sum("total_amount").alias("total_sales"))

# 27. Listar todos los usuarios que no han realizado ninguna compra
users_no_purchase = orders_df.select("user_id").distinct() \
                              .subtract(orders_df.select("user_id").distinct())

# 28. Obtener el total de ventas por cada usuario y cada producto
sales_by_user_product = orders_df.groupBy("user_id", "order_item_id") \
                                 .agg(F.sum("total_amount").alias("total_sales"))

# 29. Obtener las órdenes realizadas en el mes de abril
orders_in_april = orders_df.filter(F.month("order_date") == 4) \
                           .select("order_id", "order_date", "total_amount")

# 30. Obtener el pedido con el mayor total_amount
max_value_order = orders_df.orderBy(F.desc("total_amount")).limit(1)

# 31. Obtener el total de ventas por país y mes
sales_by_country_month = orders_df.withColumn("month", F.month("order_date")) \
                                  .groupBy("country", "month") \
                                  .agg(F.sum("total_amount").alias("total_sales"))

# 32. Obtener los usuarios que compraron en un rango de fechas
orders_in_date_range = orders_df.filter((orders_df.order_date >= '2025-01-01') & 
                                        (orders_df.order_date <= '2025-06-30')) \
                                .select("user_id", "order_id", "total_amount")

# 33. Obtener los productos que más han generado ventas
top_selling_products = orders_df.groupBy("order_item_id") \
                                .agg(F.sum("total_amount").alias("total_sales")) \
                                .orderBy(F.desc("total_sales"))

# 34. Obtener el total de ventas por día de la semana
sales_by_day_of_week = orders_df.withColumn("day_of_week", F.date_format("order_date", "EEEE")) \
                                .groupBy("day_of_week") \
                                .agg(F.sum("total_amount").alias("total_sales"))

# 35. Listar los usuarios con más de 10 productos vendidos
users_more_than_10_products = orders_df.groupBy("user_id") \
                                        .agg(F.sum("quantity").alias("total_quantity")) \
                                        .filter("total_quantity > 10")

# 36. Obtener el total de ventas de productos en un rango de fechas
sales_in_date_range = orders_df.filter((orders_df.order_date >= '2025-01-01') & 
                                       (orders_df.order_date <= '2025-06-30')) \
                               .groupBy("order_item_id") \
                               .agg(F.sum("total_amount").alias("total_sales"))

# 37. Obtener la cantidad total de productos vendidos por cada usuario y cada país
sales_by_user_country = orders_df.groupBy("user_id", "country") \
                                .agg(F.sum("quantity").alias("total_quantity"))

# 38. Listar los productos que fueron comprados más de 100 veces
products_more_than_100_sales = orders_df.groupBy("order_item_id") \
                                         .agg(F.sum("quantity").alias("total_quantity")) \
                                         .filter("total_quantity > 100")

# 39. Obtener los usuarios que han realizado compras en todos los países
users_in_all_countries = orders_df.groupBy("user_id") \
                                  .agg(F.countDistinct("country").alias("countries_count")) \
                                  .filter("countries_count = (SELECT COUNT(DISTINCT country) FROM orders_df)")

# 40. Obtener los pedidos con más de 5 productos
orders_with_more_than_5_items = orders_df.groupBy("order_id") \
                                          .agg(F.sum("quantity").alias("total_quantity")) \
                                          .filter("total_quantity > 5")

# 41. Obtener las ventas totales por cada usuario y año
sales_by_user_year = orders_df.withColumn("year", F.year("order_date")) \
                              .groupBy("user_id", "year") \
                              .agg(F.sum("total_amount").alias("total_sales"))

# 42. Listar los usuarios que han comprado más de 5 veces un producto específico
product_id = 123  # Especificar el ID del producto
users_more_than_5_purchases = orders_df.filter(orders_df.order_item_id == product_id) \
                                        .groupBy("user_id") \
                                        .agg(F.count("order_id").alias("order_count")) \
                                        .filter("order_count > 5")

# 43. Obtener el total de ventas por usuario y producto
sales_by_user_product = orders_df.groupBy("user_id", "order_item_id") \
                                 .agg(F.sum("total_amount").alias("total_sales"))

# 44. Obtener el total gastado por un usuario específico en un rango de fechas
user_id = 12345
start_date = '2025-01-01'
end_date = '2025-06-30'
total_spent_user_period = orders_df.filter((orders_df.user_id == user_id) & 
                                           (orders_df.order_date >= start_date) & 
                                           (orders_df.order_date <= end_date)) \
                                   .groupBy("user_id") \
                                   .agg(F.sum("total_amount").alias("total_spent"))

# 45. Obtener los productos vendidos más de 50 veces
products_more_than_50_sales = orders_df.groupBy("order_item_id") \
                                        .agg(F.sum("quantity").alias("total_quantity")) \
                                        .filter("total_quantity > 50")

# 46. Obtener los usuarios que han comprado productos de más de 3 categorías diferentes
users_different_categories = orders_df.groupBy("user_id") \
                                      .agg(F.countDistinct("order_item_id").alias("distinct_categories")) \
                                      .filter("distinct_categories > 3")

# 47. Obtener los productos vendidos más de 5 veces por un usuario específico
user_id = 12345
products_more_than_5_sales_by_user = orders_df.filter(orders_df.user_id == user_id) \
                                              .groupBy("order_item_id") \
                                              .agg(F.sum("quantity").alias("total_quantity")) \
                                              .filter("total_quantity > 5")

# 48. Obtener las órdenes que fueron realizadas por usuarios con un total_amount mayor a 500
high_value_orders_by_user = orders_df.filter(orders_df.total_amount > 500) \
                                      .select("order_id", "user_id", "total_amount")

# 49. Obtener el total de ventas de un producto por país
sales_by_product_country = orders_df.groupBy("order_item_id", "country") \
                                   .agg(F.sum("total_amount").alias("total_sales"))

# 50. Listar los productos que tienen una cantidad total vendida mayor a la media
products_more_than_avg_sales = orders_df.groupBy("order_item_id") \
                                        .agg(F.sum("quantity").alias("total_quantity")) \
                                        .filter("total_quantity > (SELECT AVG(quantity) FROM orders_df)")

# 51. Obtener el total de ventas de un producto específico por mes
product_id = 123  # Especificar el ID del producto
sales_by_product_month = orders_df.filter(orders_df.order_item_id == product_id) \
                                  .withColumn("month", F.month("order_date")) \
                                  .groupBy("month") \
                                  .agg(F.sum("total_amount").alias("total_sales"))

# 52. Obtener el total de ventas de un producto en un rango de fechas
sales_by_product_date_range = orders_df.filter((orders_df.order_item_id == product_id) &
                                               (orders_df.order_date >= '2025-01-01') &
                                               (orders_df.order_date <= '2025-03-31')) \
                                       .groupBy("order_item_id") \
                                       .agg(F.sum("total_amount").alias("total_sales"))

# 53. Obtener el promedio de ventas por usuario
avg_sales_by_user = orders_df.groupBy("user_id") \
                             .agg(F.avg("total_amount").alias("average_sales"))

# 54. Obtener los productos vendidos en un país específico y ordenarlos por ventas
sales_by_country_product = orders_df.filter(orders_df.country == "USA") \
                                    .groupBy("order_item_id") \
                                    .agg(F.sum("total_amount").alias("total_sales")) \
                                    .orderBy(F.desc("total_sales"))

# 55. Obtener los productos vendidos más caros en una fecha específica
specific_date = '2025-04-01'
expensive_products_on_date = orders_df.filter(orders_df.order_date == specific_date) \
                                      .groupBy("order_item_id") \
                                      .agg(F.max("unit_price").alias("highest_price"))

# 56. Obtener el total de ventas por país y año
sales_by_country_year = orders_df.withColumn("year", F.year("order_date")) \
                                .groupBy("country", "year") \
                                .agg(F.sum("total_amount").alias("total_sales"))

# 57. Obtener los productos que tienen más de 100 compras en un país específico
sales_by_product_country_threshold = orders_df.filter(orders_df.country == "UK") \
                                              .groupBy("order_item_id") \
                                              .agg(F.sum("quantity").alias("total_quantity")) \
                                              .filter("total_quantity > 100")

# 58. Obtener los usuarios que han realizado más compras en un país específico
users_more_than_5_in_country = orders_df.filter(orders_df.country == "Germany") \
                                         .groupBy("user_id") \
                                         .agg(F.count("order_id").alias("order_count")) \
                                         .filter("order_count > 5")

# 59. Obtener los productos vendidos por un rango de usuarios
users_range_start = 100  # Reemplazar con el ID de usuario inicial
users_range_end = 200    # Reemplazar con el ID de usuario final
sales_by_users_range = orders_df.filter((orders_df.user_id >= users_range_start) & 
                                        (orders_df.user_id <= users_range_end)) \
                                .groupBy("order_item_id") \
                                .agg(F.sum("total_amount").alias("total_sales"))

# 60. Obtener el total de ventas por cada semana
sales_by_week = orders_df.withColumn("week", F.weekofyear("order_date")) \
                         .groupBy("week") \
                         .agg(F.sum("total_amount").alias("total_sales"))


