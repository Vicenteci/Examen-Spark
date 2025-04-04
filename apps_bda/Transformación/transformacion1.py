from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum, to_date, weekofyear
from pyspark.sql.types import IntegerType, DoubleType

# Crear sesión de Spark conectada a LocalStack y S3
spark = SparkSession.builder \
    .appName("TransformacionDatosPedidos") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
    .config("spark.hadoop.fs.s3a.access.key", "test") \
    .config("spark.hadoop.fs.s3a.secret.key", "test") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4") \
    .getOrCreate()

# Leer los archivos CSV limpios desde S3
file_path = "s3a://bucket-1/CSV_Limpio/*.csv"
df = spark.read.option("header", "true").csv(file_path)

# Convertir columnas a tipos correctos para procesamiento numérico y fechas
df = df.withColumn("quantity", col("quantity").cast(IntegerType())) \
       .withColumn("unit_price", col("unit_price").cast(DoubleType())) \
       .withColumn("total_amount", col("total_amount").cast(DoubleType())) \
       .withColumn("age", col("age").cast(IntegerType())) \
       .withColumn("order_date", col("order_date").cast("date"))

### MANEJO DE NULOS ###

# OPCIÓN 1: Eliminar filas con nulos en columnas críticas (comentada por si no se quiere usar)
# df_cleaned = df.dropna(subset=["quantity", "unit_price", "total_amount", "order_date"])

# OPCIÓN 2: Rellenar nulos con la media de la columna correspondiente (usada por defecto)
# Se calcula la media y se asigna para reemplazar nulos
df_filled = df.fillna({
    "quantity": df.agg(avg("quantity")).first()[0],
    "unit_price": df.agg(avg("unit_price")).first()[0],
    "total_amount": df.agg(avg("total_amount")).first()[0]
})

### TRANSFORMACIONES TEMPORALES ###

# Crear nueva columna con el número de semana del año (para agrupar por semana)
df_filled = df_filled.withColumn("week", weekofyear(col("order_date")))

# Agrupar por semana y país, calculando la media y la suma
df_grouped = df_filled.groupBy("week", "country").agg(
    avg("total_amount").alias("avg_total_amount"),
    sum("quantity").alias("total_quantity")
)

# Ordenar los resultados por semana
df_sorted = df_grouped.orderBy("week")

# Mostrar algunos resultados por pantalla (opcional, útil para depurar)
df_sorted.show()

# Escribir el resultado final en PostgreSQL (la base ya debe estar corriendo en el contenedor)
df_sorted.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://postgres:5432/retail_db") \
    .option("dbtable", "sales_summary") \
    .option("header", "true") \
    .option("user", "postgres") \
    .option("password", "casa1234") \
    .mode("overwrite") \
    .save()

# Cerrar la sesión de Spark
spark.stop()
