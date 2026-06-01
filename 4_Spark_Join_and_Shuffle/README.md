<h1 align="center">Spark Join</h1>


## Description

Here you will learn about join strategies in Spark and shuffle strategies in Spark.


## Theory about shuffle 

In reality, shuffle strategies in Spark are rarely touched, as the default configs are set up so that you won't run into any problems. More often than not, you'll never even have to think about them. Nevertheless, to understand the concept of a join, you need to have an understanding of shuffles as well. Plus, there is one particular guest - the Tungsten shuffle - that can act as quite a lifesaver when dealing with very large volumes of data. So, let's get started.

Article about shuffle: https://0x0fff.com/spark-architecture-shuffle/.

There is a nuance in the article that some might overlook: when spark.sql.shuffle.partitions < 200, the default strategy is the Hash Shuffle. 
If spark.sql.shuffle.partitions > 200, it becomes the Sort-based Shuffle. The Tungsten shuffle isn't part of the default settings at all; 
however, in certain situations, it can truly be the key to solving a problem.


## Join strategies

Article: https://medium.com/@ongchengjie/different-types-of-spark-join-strategies-997671fbf6b0

