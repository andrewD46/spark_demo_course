import pyspark.sql.types as T
from pyspark.sql.functions import when, col, lit, regexp_extract
from pyspark.sql import SparkSession

people_schema = T.StructType([ \
    T.StructField("rank", T.IntegerType(), True), \
    T.StructField("name", T.StringType(), True), \
    T.StructField("net_worth", T.StringType(), True), \
    T.StructField("bday", T.StringType(), True), \
    T.StructField("age", T.IntegerType(), True), \
    T.StructField("nationality", T.StringType(), True)
])

country_schema = T.StructType([ \
    T.StructField("country", T.StringType(), True), \
    T.StructField("num_billionares", T.StringType(), True), \
    T.StructField("billionaire_per_million", T.StringType(), True)
])

spark = SparkSession\
            .builder\
            .appName('spark_basic')\
            .getOrCreate()
            


df_people = spark.read.option('header', 'true').schema(people_schema).csv('path_to/data/top_100_richest.csv')

df_country = spark.read.option('header', 'true').schema(country_schema).csv('path_to/data/wiki_number_of_billionaires.csv')


df_people_filtered = df_people.withColumn('net_worth', regexp_extract(col('net_worth'), '^\$(\\d+).*$', 1).cast('int')).filter(col('net_worth') > 60)

df_people_new = df_people_filtered.withColumn('nationality', when(col('nationality') == 'United States of America',  'United States').\
                                                                            when(col('nationality') == 'French',  'France').\
                                                                            when(col('nationality') == 'England', 'United Kingdom').\
                                                                            otherwise(col('nationality')))
                                                                            

df_prelast = df_people_new.join(df_country, df_people_new['nationality'] == df_country['country'], 'inner')

df_last = df_prelast.filter(col('age').isNotNull()).select(col('rank'), col('name'), col('net_worth'), col('bday'), col('age'), col('nationality'))

df_parquet = spark.read.schema(people_schema).parquet('path_to/3_Spark_Basics/data_parquet')

df_parquet_filtered = df_parquet.filter(col('nationality') == 'Russia')

df_last = df_last.union(df_parquet_filtered)

df_last.write.option("header", 'true').mode('overwrite').csv("path_to/3_Spark_Basics/1.csv")

plans = df_last._jdf.queryExecution().toString()

plans_1 = df_last._sc._jvm.PythonSQLUtils.explainString(df_last._jdf.queryExecution(), 'EXTENDED')

with open('path_to/3_Spark_Basics/plans.txt', 'w') as file:
    file.write(plans)
    
#я оставил оба варианта вывода планов, но второй который plans_1 предпочтительнее. Планы одинаковые

with open('path_to/3_Spark_Basics/plans1.txt', 'w') as file:
    file.write(plans_1)
