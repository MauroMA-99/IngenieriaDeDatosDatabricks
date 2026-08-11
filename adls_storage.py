# Databricks notebook source
# MAGIC %md
# MAGIC ##Formas de montado de databricks con ADLS Gen 2 o Blob storage

# COMMAND ----------

# MAGIC %md
# MAGIC ###Variables

# COMMAND ----------

dbutils.widgets.removeAll()

# COMMAND ----------

dbutils.widgets.text("storage-account", "adlssmartdata0704")

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
spark.conf.set(f"fs.azure.sas.fixed.token.{storage_account}.dfs.core.windows.net", "sp=racwdlmeop&st=2025-04-07T19:20:12Z&se=2025-04-08T03:20:12Z&spr=https&sv=2024-11-04&sr=c&sig=NfvnGvUu%2FdxkjdZOuKjPV4INS14Bo1VYhFEYLkCkLlI%3D")

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

configs = {"fs.azure.account.auth.type": "OAuth",
           "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
           "fs.azure.account.oauth2.client.id": f"{client_id}",
           "fs.azure.account.oauth2.client.secret": f"{client_secret}",
           "fs.azure.account.oauth2.client.endpoint": f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"}

# COMMAND ----------

def mount_adls(container_name):
  dbutils.fs.mount(
    source = f"abfss://{container_name}@{storage_account}.dfs.core.windows.net/",
    mount_point = f"/mnt/{storage_account}/{container_name}",
    extra_configs = configs)

# COMMAND ----------

display(dbutils.fs.mounts())

# COMMAND ----------

mount_adls("bronze")

# COMMAND ----------

mount_adls("silver")

# COMMAND ----------

mount_adls("golden")

# COMMAND ----------

# MAGIC %fs
# MAGIC ls "dbfs:/mnt/adlssmartdata0704/bronze/"

# COMMAND ----------

dbutils.fs.ls(f"/mnt/{storage_account}/{bronze}")

# COMMAND ----------

display(dbutils.fs.ls("/"))

# COMMAND ----------

display(dbutils.fs.mounts())

# COMMAND ----------

#Desmontar la ruta montada
dbutils.fs.unmount(f"/mnt/{storage_account}/{bronze}")

# COMMAND ----------

# MAGIC %md
# MAGIC ###Explorando dbutils secrets

# COMMAND ----------

dbutils.secrets.help()

# COMMAND ----------

dbutils.secrets.listScopes()

# COMMAND ----------

dbutils.secrets.list(scope="accessScopeforADLS")

# COMMAND ----------

dbutils.secrets.get(scope="accessScopeforADLS", key="storageAccessKey")

# COMMAND ----------

display(dbutils.fs.ls(f"abfss://{bronze}@{storage_account}.dfs.core.windows.net/"))