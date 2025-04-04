from pyspark.sql import SparkSession

# Configuración de acceso a S3 (LocalStack)
aws_access_key_id = 'test'
aws_secret_access_key = 'test'

# Configuración de Spark
spark = SparkSession.builder \
    .appName("Neo4j to S3") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
    .config("spark.hadoop.fs.s3a.access.key", aws_access_key_id) \
    .config("spark.hadoop.fs.s3a.secret.key", aws_secret_access_key) \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.jars", "/opt/spark/jars/neo4j-connector-apache-spark_2.12-4.1.3_for_spark_3.jar") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

# Conectar a Neo4j y leer datos
neo4j_url = "bolt://neo4j:7687"
neo4j_options = {
    "url": neo4j_url,
    "authentication.type": "basic",
    "authentication.basic.username": "neo4j",
    "authentication.basic.password": "password",
    "query": "MATCH (s:Store)-[:HAS_SALE]->(v:Sale) RETURN s.store_id, s.name, v.product_id, v.revenue"
}

df_neo4j = spark.read.format("org.neo4j.spark.DataSource").options(**neo4j_options).load()

# Si el JOIN no es necesario, puedes usar un SELECT * básico
# neo4j_options["query"] = "MATCH (s:Store) RETURN s.store_id, s.name"
# df_neo4j = spark.read.format("org.neo4j.spark.DataSource").options(**neo4j_options).load()

# Guardar en S3
df_neo4j.write.mode('overwrite').csv('s3a://bucket/neo4j_data', header=True, sep=',')

spark.stop()
