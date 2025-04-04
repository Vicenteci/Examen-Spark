from pyspark.sql import SparkSession

# Configuración de acceso a S3 (LocalStack)
aws_access_key_id = 'test'
aws_secret_access_key = 'test'

# Configuración de Spark
spark = SparkSession.builder \
    .appName("MySQL to S3") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
    .config("spark.hadoop.fs.s3a.access.key", aws_access_key_id) \
    .config("spark.hadoop.fs.s3a.secret.key", aws_secret_access_key) \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.jars", "/opt/spark/jars/mysql-connector-java-8.0.33.jar") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

# Conectar a MySQL y leer las tablas
mysql_url = "jdbc:mysql://mysql:3306/retail-db"
properties = {"user": "root", "password": "root", "driver": "com.mysql.cj.jdbc.Driver"}

df_tienda = spark.read.jdbc(mysql_url, "tienda", properties=properties)
df_ventas = spark.read.jdbc(mysql_url, "ventas", properties=properties)

# Hacer INNER JOIN
df_joined = df_tienda.join(df_ventas, df_tienda["store_id"] == df_ventas["store_id"], "inner")

# Si el JOIN no es necesario, puedes usar un SELECT *
# df_joined = spark.read.jdbc(mysql_url, "ventas", properties=properties)

# Guardar en S3
df_joined.write.mode('overwrite').csv('s3a://bucket/mysql_data', header=True, sep=',')

spark.stop()
