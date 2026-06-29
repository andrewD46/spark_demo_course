<h1 align="center">Data Skew</h1>


## Description

Here, you will learn about a very important issue that affects all distributed systems: data skew.


## Theory about Data Skew

As long as you are running everything on a single machine, you won't encounter this problem (or rather, it might exist, but it won't impact performance that heavily).
Let's look at the core of the problem right away through an example: suppose you have a registration form where the email address is an optional parameter. 
In this case, a large portion of users simply won't enter it. As a result, you will have a data skew in this field (for simplicity's sake, let's say 50% entered an email and 50% did not).
Obviously, there are many different email addresses, so the 50% of entered emails will be more or less evenly distributed. 
However, the absence of emails (the nulls or empty strings) becomes a real issue. 
But what exactly is the problem? Let's say you want to group your data by the email field to calculate some aggregations. 
Under the hood, Spark will perform a shuffle to ensure that data with the same key ends up in the same partition.

Consequently, you will get relatively reasonably sized partitions for the actual emails, but for the missing emails, you will get one incredibly massive partition. 
Two scenarios are possible here:
- Slow execution: Spark manages to fit this huge partition into RAM. It will eventually process it, but it will be very, very slow, creating a bottleneck.
- OOM Error: If the massive partition exceeds the available RAM, your executor will simply crash (Out of Memory).

That is roughly what this problem looks like, and it is a situation you will encounter very frequently in real-world data processing.

## Strategies to solve problem

- The easiest approach is the Broadcast Hash Join (assuming you are actually performing a join, of course). You are already familiar with this join type. The core concept is to create a hash table from the smaller DataFrame, send it to the driver, let the driver assemble the pieces of the hash table from the various workers, and then broadcast the complete hash map back out to all the workers. It is crucial to understand what qualifies as a "small DataFrame" for your specific cluster, as you really don't want to overload the driver with too much data. You already know which parameter controls this threshold, but I will add that AQE (Adaptive Query Execution) can also decide dynamically whether to use this join or not. Alternatively, you can explicitly trigger this join type by using a broadcast hint directly in your code.

- A bit more complicated is **salting**. https://medium.com/@sankalpmohate/solving-the-data-skew-problem-in-pyspark-with-salting-132bda8ef8a8. Actually, you can also use the `explode()` function in Spark for a `join`. Here's an article specifically about `explode` (not about salting itself): https://sparkbyexamples.com/spark/explode-spark-array-and-map-dataframe-column/

- AQE (Adaptive Query Execution). In this case, it only works with a Sort Merge Join. AQE itself collects statistics after the first shuffle stage (shuffle write). At this point, it might notice that one of the partitions is going to be too large and do the following: automatically "salt" (split) it, thereby turning that single partition into several smaller ones. Yes, they will still be on the same worker (since you obviously wouldn't send the corresponding partition of the second dataset to different workers). Nevertheless, the partitions themselves are smaller, and the number of partitions on the workers after the shuffle is distributed evenly. This means you will end up with partitions of more or less the same size everywhere. (Without this, that worker would have multiple partitions with one of them being massive; with this, it holds the exact same data from the large partition, but broken down into smaller ones, keeping the total number of partitions across all workers roughly equal). And yes, AQE isn't a genius, so all the thresholds-like what data size is considered skewed, etc. - must be configured manually via configs.

![image](https://user-images.githubusercontent.com/113685144/194550587-439bbacb-50cc-4357-9623-10380032172c.png)

- Obviously, there are a number of other methods, but they are more tailored to specific situations and are not as common. Basically, salting and broadcast joins
will be more than enough, but if you make a mistake, AQE will clean up your mess (or at least try to - it's not perfect yet).

