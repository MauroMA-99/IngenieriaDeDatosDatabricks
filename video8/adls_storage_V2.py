# Databricks notebook source
# MAGIC %md
# MAGIC ##Formas de montado de databricks con ADLS Gen 2 o Blob storage

# COMMAND ----------

# MAGIC %md
# MAGIC ###Variables

# COMMAND ----------

dbutils.widgets.removeAll()

# COMMAND ----------

dbutils.widgets.text("storage-account", "adlsedu01")

# COMMAND ----------

storage_account = dbutils.widgets.get("storage-account")
bronze = "bronze"
silver = "silver"
golden = "golden"

scope = "accessScopeforADLS"
key = "storageAccessKey"

# COMMAND ----------

# MAGIC %md
# MAGIC ##Exponer tu key de forma directa

# COMMAND ----------

#spark.conf.set(
#    f"fs.azure.account.key.{storage_account}.dfs.core.windows.net",
#    f"...")

# COMMAND ----------

df_valoracion_usuarios = spark.read.csv(f"abfss://{bronze}@{storage_account}.dfs.core.windows.net/valoracion_usuarios.csv", header=True)

# COMMAND ----------

df_valoracion_usuarios.limit(5).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ###Account key

# COMMAND ----------

dbutils.secrets.listScopes()

# COMMAND ----------

spark.conf.set(
    f"fs.azure.account.key.{storage_account}.dfs.core.windows.net",
    dbutils.secrets.get(scope=f"{scope}", key=f"{key}"))

# COMMAND ----------

df_valoracion_usuarios = spark.read.csv(f"abfss://{bronze}@{storage_account}.dfs.core.windows.net/valoracion_usuarios.csv", header=True)

# COMMAND ----------

df_valoracion_usuarios.limit(5).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ###SAS Token

# COMMAND ----------

spark.conf.set(f"fs.azure.account.auth.type.{storage_account}.dfs.core.windows.net", "SAS")
spark.conf.set(f"fs.azure.sas.token.provider.type.{storage_account}.dfs.core.windows.net", "org.apache.hadoop.fs.azurebfs.sas.FixedSASTokenProvider")
spark.conf.set(f"fs.azure.sas.fixed.token.{storage_account}.dfs.core.windows.net", "sv=2026-02-06&ss=bfqt&srt=sco&sp=rwdlacupyx&se=2026-05-29T04:54:27Z&st=2026-05-28T20:39:27Z&spr=https&sig=hbhRcmwm75JyhhLbunu7QSSghS72WqcmtxK93CXm9Mk%3D")

# COMMAND ----------

df_valoracion_usuarios = spark.read.csv(f"abfss://{bronze}@{storage_account}.dfs.core.windows.net/valoracion_usuarios.csv", header=True)

# COMMAND ----------

df_valoracion_usuarios.limit(5).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ###Service Principal

# COMMAND ----------

# MAGIC %md
# MAGIC Este codigo podemos colocarlo directamnente en nuestra configuarcion de spark cluster

# COMMAND ----------

#spark.hadoop.fs.azure.account.auth.type.<storage-account>.dfs.core.windows.net OAuth
#spark.hadoop.fs.azure.account.oauth.provider.type.<storage-account>.dfs.core.windows.net org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider
#spark.hadoop.fs.azure.account.oauth2.client.id.<storage-account>.dfs.core.windows.net <application-id>
#spark.hadoop.fs.azure.account.oauth2.client.secret.<storage-account>.dfs.core.windows.net {{secrets/<secret-scope>/<service-credential-key>}}
#spark.hadoop.fs.azure.account.oauth2.client.endpoint.<storage-account>.dfs.core.windows.net https://login.microsoftonline.com/<directory-id>/oauth2/token

# COMMAND ----------

# MAGIC %md
# MAGIC Podemos obtar por colocar la configuracion en nuestro notebook.

# COMMAND ----------

client_id            = dbutils.secrets.get(scope="accessScopeforADLS", key="databricks-app-client-id")
tenant_id            = dbutils.secrets.get(scope="accessScopeforADLS", key="databricks-app-tenant-id")
client_secret        = dbutils.secrets.get(scope="accessScopeforADLS", key="databricks-app-client-secret")

# COMMAND ----------

#client_id            = "CLIENT_ID"
#tenant_id            = "TENANT_ID"
#client_secret        = "CLIENT_SECRET"

# COMMAND ----------

spark.conf.set(
  f"fs.azure.account.auth.type.{storage_account}.dfs.core.windows.net",
  "OAuth"
)

spark.conf.set(
  f"fs.azure.account.oauth.provider.type.{storage_account}.dfs.core.windows.net",
  "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider"
)

spark.conf.set(
  f"fs.azure.account.oauth2.client.id.{storage_account}.dfs.core.windows.net",
  client_id
)

spark.conf.set(
  f"fs.azure.account.oauth2.client.secret.{storage_account}.dfs.core.windows.net",
  client_secret
)

spark.conf.set(
  f"fs.azure.account.oauth2.client.endpoint.{storage_account}.dfs.core.windows.net",
  f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
)

# COMMAND ----------

df = spark.read.csv(
    f"abfss://bronze@{storage_account}.dfs.core.windows.net/valoracion_usuarios.csv",
    header=True,
    inferSchema=True
)

# COMMAND ----------

print(client_id)

# COMMAND ----------

display(df)

# COMMAND ----------

dbutils.secrets.help()

# COMMAND ----------

dbutils.secrets.listScopes()

# COMMAND ----------

dbutils.secrets.list(scope="accessScopeforADLS")

# COMMAND ----------

dbutils.secrets.get(scope="accessScopeforADLS", key="databricks-app-tenant-id")

# COMMAND ----------

display(dbutils.fs.ls(f"abfss://{bronze}@{storage_account}.dfs.core.windows.net/"))

# COMMAND ----------



# COMMAND ----------

