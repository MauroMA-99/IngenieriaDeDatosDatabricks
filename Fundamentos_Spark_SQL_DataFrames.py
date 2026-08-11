# Databricks notebook source
# MAGIC %md
# MAGIC # Fundamentos de Apache Spark

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# COMMAND ----------

# MAGIC %md
# MAGIC ### Crear la sesión de Spark 

# COMMAND ----------

spark

# COMMAND ----------

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Crear el DataFrame

# COMMAND ----------

emp = [(1, "AAA", "dept1", 1000),
    (2, "BBB", "dept1", 1100),
    (3, "CCC", "dept1", 3000),
    (4, "DDD", "dept1", 1500),
    (5, "EEE", "dept2", 8000),
    (6, "FFF", "dept2", 7200),
    (7, "GGG", "dept3", 7100),
    (8, "HHH", "dept3", 3700),
    (9, "III", "dept3", 4500),
    (10, "JJJ", "dept5", 3400)]

dept = [("dept1", "Department - 1"),
        ("dept2", "Department - 2"),
        ("dept3", "Department - 3"),
        ("dept4", "Department - 4")
       ]

df = spark.createDataFrame(emp, ["id", "name", "dept", "salary"])

deptdf = spark.createDataFrame(dept, ["id", "name"])

# COMMAND ----------

df.show()

# COMMAND ----------

display(df)

# COMMAND ----------

df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC # Operaciones básicas en DataFrames

# COMMAND ----------

# MAGIC %md
# MAGIC ### count
# MAGIC * Cuenta el número de filas

# COMMAND ----------

df.count()

# COMMAND ----------

df.select("id").display()

# COMMAND ----------

df.select("id").distinct().count()

# COMMAND ----------

df.select("dept").distinct().count()

# COMMAND ----------

# MAGIC %md
# MAGIC ### columns

# COMMAND ----------

df.columns

# COMMAND ----------

# MAGIC %md
# MAGIC ### dtypes
# MAGIC ** Accede al DataType de columnas dentro del DataFrame

# COMMAND ----------

df.dtypes

# COMMAND ----------

# MAGIC %md
# MAGIC ### schema
# MAGIC ** Comprueba cómo Spark almacena el esquema del DataFrame

# COMMAND ----------

df.schema

# COMMAND ----------

# MAGIC %md
# MAGIC ### printSchema

# COMMAND ----------

df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ### select
# MAGIC * Seleccione columnas del DataFrame

# COMMAND ----------

df.select("id", "name").show()

# COMMAND ----------

df.select("id", "dept").display()

# COMMAND ----------

df.select("*").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### filter
# MAGIC
# MAGIC * Filtrar las filas según alguna condición.
# MAGIC * Intentemos encontrar las filas con id = 1.
# MAGIC * Hay diferentes formas de especificar la condición.

# COMMAND ----------

df.filter(df["id"] == 2).display()
df.filter(df.id == 1).display()

# COMMAND ----------

df.filter(col("id") == 3).display()
df.filter("id = 4").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### drop
# MAGIC * Elimina una columna en particular

# COMMAND ----------

newdf = df.drop("id")
newdf.display(2)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Aggregations
# MAGIC * Podemos usar la función groupBy para agrupar los datos y luego usar la función "agg" para realizar la agregación de datos agrupados.

# COMMAND ----------

display(df)

# COMMAND ----------

(df.groupBy("dept","id")
    .agg(
        count("salary").alias("count"),
        sum("salary").alias("sum"),
        max("salary").alias("max"),
        min("salary").alias("min"),
        avg("salary").alias("avg")
        ).display()
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Sorting
# MAGIC
# MAGIC * Ordena los datos según el "salario". De forma predeterminada, la clasificación se realizará en orden ascendente.

# COMMAND ----------

df.sort("salary").display(5)

# COMMAND ----------

display(df.sort(desc("dept"), asc("salary")).limit(6))

# COMMAND ----------

display(df.sort(desc("dept"), desc("salary")).limit(6))

# COMMAND ----------

df.sort(desc("dept"), desc("salary")).limit(6).display()

# COMMAND ----------

df.sort(desc("salary")).show(5)

# COMMAND ----------

df.sort(asc("salary")).display(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Columnas derivadas
# MAGIC * Podemos usar la función "withColumn" para derivar la columna en función de las columnas existentes ...

# COMMAND ----------

df.withColumn("bonus", col("salary") * 0.1).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Joins
# MAGIC
# MAGIC * Podemos realizar varios tipos de combinaciones en múltiples DataFrames.

# COMMAND ----------

display(deptdf)

# COMMAND ----------

#mala practica
deptdf = deptdf.withColumnRenamed("id","id_2")

# COMMAND ----------

newdeptdf_2 = deptdf.select(col("id_2").alias("id_nuevo"),col("name").alias("nombre"))

# COMMAND ----------

display(newdeptdf_2)

# COMMAND ----------

display(df)

# COMMAND ----------

display(deptdf)

# COMMAND ----------

df.join(deptdf, df["dept"] == deptdf["id_2"]).display()

# COMMAND ----------

deptdf = deptdf.select(col("id_2"),col("name").alias("nom_dept"))

# COMMAND ----------

# Inner JOIN.
array = ['id','name']
df_join = df.join(deptdf, df["dept"] == deptdf["id_2"],"inner").select([col(column) for column in array])
df_join.display()

# COMMAND ----------

df_join.select(col("id"),col("name"),col("dept"),col("salary"),col("nom_dept")).display()

# COMMAND ----------

df.select(col("id"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Left Outer Join

# COMMAND ----------

df.join(deptdf, df["dept"] == deptdf["id_2"], "left_outer").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Right Outer Join

# COMMAND ----------

df.join(deptdf, df["dept"] == deptdf["id_2"], "right_outer").display()

# COMMAND ----------

df.join(deptdf, df["dept"] == deptdf["id_2"], "right").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Full Outer Join

# COMMAND ----------

df.join(deptdf, df["dept"] == deptdf["id_2"], "outer").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Consultas SQL
# MAGIC * Ejecución de consultas tipo SQL.
# MAGIC * También podemos realizar análisis de datos escribiendo consultas similares a SQL. Para realizar consultas similares a SQL, necesitamos registrar el DataFrame como una Vista temporal.

# COMMAND ----------

display(df)

# COMMAND ----------

bd = "smart_data"

# COMMAND ----------

df = spark.sql("""with  b1 (
                    select *
                    from {bd}.users
                ) 
                select *
                from b1 
               """.replace(bd))

df.createOrReplaceTempView("temp_table")

# COMMAND ----------

# Register DataFrame as Temporary Table
df.createOrReplaceTempView("temp_table")

# Execute SQL-Like query.
spark.sql("select * from temp_table where id = 2").display()

# COMMAND ----------

# MAGIC %sql
# MAGIC select *
# MAGIC from temp_table where id = 5

# COMMAND ----------

df_2 = spark.sql("""select * 
                    from temp_table limit 2
                    """)

df_2.display()

# COMMAND ----------

#df = df.withColumn("salary",col("salary").cast("string"))
df = df.withColumn("salary",replace("salary","TT",""))
df = df.withColumn("salary",col("salary").cast("float"))

# COMMAND ----------

df_2.createOrReplaceTempView("temp_table_2")

# COMMAND ----------

# MAGIC %sql
# MAGIC select *
# MAGIC from temp_table_2

# COMMAND ----------

spark.sql("select distinct id from temp_table").display(10)

# COMMAND ----------

spark.sql("select * from temp_table where salary >= 1500").show(10)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Leyendo la tabla HIVE como DataFrame

# COMMAND ----------

# DB_NAME : Name of the the HIVE Database
# TBL_NAME : Name of the HIVE Table


df = spark.table("DB_NAME"."TBL_NAME")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Guardar DataFrame como tabla HIVE

# COMMAND ----------

df.write.saveAsTable("DB_NAME.TBL_NAME")

## También podemos seleccionar el argumento "modo" con overwrite", "append", "error" etc.
df.write.saveAsTable("DB_NAME.TBL_NAME", mode="overwrite")

# De forma predeterminada, la operación guardará el DataFrame como una tabla interna / administrada de HIVE

# COMMAND ----------

# MAGIC %md
# MAGIC ### Guardar el DataFrame como una tabla externa HIVE

# COMMAND ----------

df.write.saveAsTable("DB_NAME.TBL_NAME", path=<location_of_external_table>)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Crea un DataFrame a partir de un archivo CSV
# MAGIC * Podemos crear un DataFrame usando un archivo CSV y podemos especificar varias opciones como un separador, encabezado, esquema, inferSchema y varias otras opciones.

# COMMAND ----------

 df = spark.read.csv("path_to_csv_file", sep="|", header=True, inferSchema=True)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Guardar un DataFrame como un archivo CSV

# COMMAND ----------

df.write.csv("path_to_CSV_File", sep="|", header=True, mode="overwrite")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Crea un DataFrame a partir de una tabla relacional
# MAGIC * Podemos leer los datos de bases de datos relacionales usando una URL JDBC.

# COMMAND ----------

# url : a JDBC URL of the form jdbc:subprotocol:subname
# TBL_NAME : Name of the relational table.
# USER_NAME : user name to connect to DataBase.
# PASSWORD: password to connect to DataBase.


relational_df = spark.read.format('jdbc')
                        .options(url=url, dbtable= <TBL_NAME>, user= <USER_NAME>, password = <PASSWORD>)
                        .load()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Guardar el DataFrame como una tabla relacional
# MAGIC * Podemos guardar el DataFrame como una tabla relacional usando una URL JDBC.

# COMMAND ----------

# url : a JDBC URL of the form jdbc:subprotocol:subname
# TBL_NAME : Name of the relational table.
# USER_NAME : user name to connect to DataBase.
# PASSWORD: password to connect to DataBase.


relational_df.write.format('jdbc')
                    .options(url=url, dbtable= <TBL_NAME>, user= <USER_NAME>, password = <PASSWORD>)
                    .mode('overwrite')
                    .save()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conexión con Databricks Community

# COMMAND ----------

paciente_outputh_path = "/FileStore/dataset/smart_data/paciente.csv"

# COMMAND ----------

df_paciente = spark.read.csv(paciente_outputh_path, header=True)

# COMMAND ----------

df_paciente.display()