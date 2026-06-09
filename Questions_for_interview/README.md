<h1 align="center">Questions for interview</h1>


## Description

Here are some questions you might be asked during interview.

 
## Questions

1) What is Spark
2) Flowing from the first question, what is MapReduce and what is its core concept?
3) What stages are there in MapReduce?
4) The difference between Spark and Hadoop
5) RDD, DF, Dataset - the difference between them (in the context of PySpark, only RDD and DF)
6) What is a DAG and how is it related to Spark?
7) The difference between actions and transformations
8) The difference between narrow and wide transformations
9) What are a job, stage, and task?
10) Types of joins (not left, right, and inner, but specifically join strategies in Spark)
11) When to use which join strategy
11) Why you shouldn't mindlessly write collect() and other things like that
12) The difference between repartition and coalesce (simply answering that coalesce only decreases partitions while repartition can also increase them is not enough; it's not even enough if a person says that repartition always triggers a shuffle). Explain the logic of how it works under the hood. Pros and cons.
13) How partitionBy works
14) partitionBy in combination with repartition or coalesce
15) How to reduce the amount of shuffle
16) Optimizations used by Catalyst
17) How to solve the Data Skew problem, and what it is in general
18) UDFs and why PySpark UDFs are bad. What to replace PySpark UDFs with
19) Delta Lake and why choose it
20) Memory management at the JVM + overhead level
21) Memory management at the full level (if it's PySpark, it involves more than just JVM and overhead)
22) Parquet - what it is (tell everything you know)
23) Nuances when reading JSON
24) Nuances when reading CSV
25) Broadcast variables
