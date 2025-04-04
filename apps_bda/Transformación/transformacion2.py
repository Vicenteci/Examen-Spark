from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum, to_date, weekofyear
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

# Ruta al archivo CSV
file_path = "s3a://bucket-1/CSV_Limpio/*.csv"
df = spark.read.option("header", "true").csv(file_path)

# Convertir las columnas necesarias a los tipos correctos
df = df.withColumn("quantity", col("quantity").cast("integer"))
df = df.withColumn("total_amount", col("total_amount").cast("double"))

# Realizar un GroupBy y una suma sobre la columna 'quantity' y 'total_amount', agrupando por 'country'
df_grouped = df.groupBy("country").agg(
    sum("quantity").alias("total_quantity"),
    sum("total_amount").alias("total_sales")
)

# Mostrar el resultado
df_grouped.show()

# Guardar el resultado en PostgreSQL (si fuera necesario)
df_grouped.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/retail_db") \
    .option("dbtable", "sales_by_country") \
    .option("user", "postgres") \
    .option("password", "password") \
    .mode("overwrite") \
    .save()