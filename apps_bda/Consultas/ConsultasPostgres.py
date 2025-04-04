from pyspark.sql import SparkSession

# Configuración del SparkSession
spark = SparkSession.builder \
    .appName("PostgreSQL Queries") \
    .config("spark.jars", "/path/to/jdbc/postgresql-42.2.5.jar") \
    .getOrCreate()

# Conexión a la base de datos PostgreSQL usando JDBC
url = "jdbc:postgresql://localhost:5432/retail_db"
properties = {
    "user": "postgres",  # Cambia con tu usuario
    "password": "password",  # Cambia con tu contraseña
    "driver": "org.postgresql.Driver"
}

# Realizar una consulta SQL directamente en la base de datos PostgreSQL
df_sales = spark.read.jdbc(url=url, table="orders_data", properties=properties)

# Registrar el DataFrame como una tabla temporal para ejecutar consultas SQL
df_sales.createOrReplaceTempView("orders_data_view")

# Ejemplo de consulta: Total de ventas por día
query_total_sales_per_day = """
    SELECT TO_DATE(order_date, 'YYYY-MM-DD') AS order_day, SUM(total_amount) AS total_sales
    FROM orders_data_view
    GROUP BY TO_DATE(order_date, 'YYYY-MM-DD')
    ORDER BY order_day
"""
result_df_sales_per_day = spark.sql(query_total_sales_per_day)

# Mostrar los resultados de ventas por día
result_df_sales_per_day.show()

# Ejemplo de consulta: Promedio de ventas por usuario
query_avg_sales_per_user = """
    SELECT user_id, AVG(total_amount) AS avg_sales
    FROM orders_data_view
    GROUP BY user_id
    ORDER BY avg_sales DESC
"""
result_df_avg_sales_per_user = spark.sql(query_avg_sales_per_user)

# Mostrar los resultados de ventas promedio por usuario
result_df_avg_sales_per_user.show()

# Ejemplo de consulta: Total de ventas por país
query_sales_by_country = """
    SELECT country, SUM(total_amount) AS total_sales
    FROM orders_data_view
    GROUP BY country
    ORDER BY total_sales DESC
"""
result_df_sales_by_country = spark.sql(query_sales_by_country)

# Mostrar los resultados de ventas por país
result_df_sales_by_country.show()

# Ejemplo de consulta: Productos más vendidos (en función de la cantidad)
query_top_products = """
    SELECT order_item_id, SUM(quantity) AS total_quantity_sold
    FROM orders_data_view
    GROUP BY order_item_id
    ORDER BY total_quantity_sold DESC
"""
result_df_top_products = spark.sql(query_top_products)

# Mostrar los productos más vendidos
result_df_top_products.show()

# Ejemplo de consulta: Ventas por edad (promedio de ventas por grupos de edad)
query_sales_by_age_group = """
    SELECT CASE
                WHEN age BETWEEN 18 AND 25 THEN '18-25'
                WHEN age BETWEEN 26 AND 35 THEN '26-35'
                WHEN age BETWEEN 36 AND 45 THEN '36-45'
                WHEN age BETWEEN 46 AND 60 THEN '46-60'
                ELSE '60+' END AS age_group,
           SUM(total_amount) AS total_sales
    FROM orders_data_view
    GROUP BY age_group
    ORDER BY total_sales DESC
"""
result_df_sales_by_age_group = spark.sql(query_sales_by_age_group)

# Mostrar las ventas por grupos de edad
result_df_sales_by_age_group.show()

# Detener Spark
spark.stop()
