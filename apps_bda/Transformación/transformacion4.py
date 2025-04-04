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


# Leer el archivo CSV
file_path = "s3a://bucket-1/CSV_Limpio/*.csv"
df = spark.read.option("header", "true").csv(file_path)

# Convertir las columnas necesarias
df = df.withColumn("quantity", col("quantity").cast("integer"))
df = df.withColumn("total_amount", col("total_amount").cast("double"))

# Limpiar datos nulos
df_cleaned = df.dropna(subset=["quantity", "total_amount"])

# Opcional: filtrar valores erróneos
df_cleaned = df_cleaned.filter((col("quantity") > 0) & (col("total_amount") > 0))

# Realizar un GroupBy y un sum
df_grouped = df_cleaned.groupBy("country").agg(
    sum("quantity").alias("total_quantity"),
    sum("total_amount").alias("total_sales")
)

# Mostrar los resultados
df_grouped.show()
