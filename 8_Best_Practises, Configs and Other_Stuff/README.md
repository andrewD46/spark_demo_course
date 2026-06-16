<h1 align="center">Best Practises, Configs and Other stuff</h1>


## Description

Well, this is the last lesson before the final assignment. Here, you will get familiar with various recommendations for tuning configurations, which configs are most commonly used, and, of course, with various other best practices.


## Cluster configuration

Well, let's start with a rather interesting topic: how to configure your cluster for a specific job. Right off the bat, I should mention that in Databricks, one executor is launched per worker, which means you cannot manage the number of executors and their resources via configurations - only by choosing the worker itself. Here is an excerpt from an article by Databricks itself:(
Databricks runs one executor per worker node; therefore the terms executor and worker are used interchangeably in the context of the Databricks architecture).

Now, a few additional insights from the Microsoft Azure perspective:

1) Complex Analytics: A single, highly powerful executor is best suited for this. The reasoning is quite simple: in analytics, you will likely perform frequent aggregations across various fields, window functions, and so on. This typically causes heavy data movement (shuffling) from one executor to another. If you use a single large executor, this network overhead disappears entirely. The main risk here is Garbage Collection (GC) errors, so ensure your cluster has significantly more memory resources than the actual volume of data being processed.

2) Standard ETL: Just about any cluster configuration might work well here, ranging from one large executor to a swarm of small ones. You will simply need to benchmark different setups to find the sweet spot.

3) Large-Scale ETL: This follows the same logic as complex analytics. A high volume of joins leads to a massive amount of shuffle data, so using a very large executor is often a great option. Again, to prevent GC bottlenecks, allocate more cluster resources than the total size of the data.

4) Machine Learning: Just about anything goes here, except for a large number of tiny executors. Overall, one large executor or several medium-sized ones will do the trick perfectly. Testing is required.

Bottom Line: Generally speaking, everything must be thoroughly benchmarked. Best practices offer excellent guidelines, but actual validation always comes down to your specific real-world testing.

## Coalesce and repartition

You have already seen these two functions and know what they do. Let's do a quick review and dive deeper into how they actually work under the hood.
ОBoth of these functions are used to manage the number of partitions in your Spark code. However, coalesce can only decrease the number of partitions, whereas repartition can both decrease and increase them. The fundamental difference lies in their execution strategy.

**Coalesce**
coalesce works by merging existing partitions together locally to minimize data movement across the network.

- How it works: Imagine you have 3 executors. The first two executors have 3 partitions each, and the last executor has 5 partitions (11 partitions total). If you call coalesce(9), Spark will shrink the total to 9 by packing the two "extra" partitions on the last executor into its other three existing partitions.
- The Benefit: It achieves the target partition count without a full shuffle, saving massive network overhead.
- The Risk (Data Skew): This strategy can easily lead to data skew. If all your original partitions were evenly sized, you now have two massive partitions sitting on a single executor. Therefore, you must use coalesce with a clear understanding of this side effect.

**Repartition**
repartition, on the other hand, forces a full shuffle across the entire cluster.

- How it works: It completely redistributes the data to create brand new, uniformly distributed partitions.
- Flexibility: You can pass just the desired number of target partitions (which triggers a random round-robin shuffle), or you can specify a partitioning key (ensuring all rows with the same key end up in the same partition), or you can provide both the partition count and the key simultaneously.

Key Takeaway: Use coalesce when you want to reduce partitions quickly without moving data over the network, keeping a close eye on potential data skew. Use repartition when you need an even distribution of data across the cluster or need to group data by a specific key, even though it comes with the performance cost of a full shuffle.

Here is example: https://sparkbyexamples.com/spark/spark-repartition-vs-coalesce/.

Both of these tools are widely used to handle data skew issues. If you notice that certain partitions are significantly larger than others after a join, yet you still need to perform downstream operations like filter, select, or a UDF, you can find a key that distributes the dataset evenly, or calculate the optimal number of partitions to re-balance the load.
They are also heavily utilized when saving files. For instance, if your goal is to merge all data and write it out as a single file, you would use coalesce(1). (We will dive deeper into how they behave during file writing in just a bit).

**Pro-Tip: The coalesce(1) Downstream Trap**
There is a fascinating and dangerous optimization quirk you should know about.

Imagine you write a pipeline that does a heavy join, followed by a filter and a select, and finally saves everything into a single file using coalesce(1).
Because of how Spark's optimizer evaluates the execution plan, it looks at coalesce(1) at the very end and might decide to push it upstream, right after the join. Spark thinks: "Why keep data across multiple partitions if it's going to end up in one anyway? Let's just collapse it to 1 partition immediately."
This is exactly where your application will likely crash with an OOM (Out of Memory) error. Because Spark collapsed the partitions prematurely, your intermediate filter and select operations will be forced to process a single, massive partition using just one CPU core, completely killing parallelism.

**The Fix: Forcing Stage Boundaries**

To prevent Spark from pushing the consolidation upstream, you can use repartition(1) instead of coalesce(1) before saving.
- Why it works: repartition forces a full shuffle, which creates a strict stage boundary that the optimizer cannot bypass.
- The Result: The intermediate step (your select and filter) will run beautifully in parallel using the number of tasks specified in spark.sql.shuffle.partitions. Only after that stage completes will Spark shuffle the data into a single partition for the final write.

Ultimately, deciding whether to stick with coalesce or force a shuffle with repartition depends entirely on your specific data and pipeline structure. 
Different cases yield different results, so always benchmark and test!

## spark.sql.shuffle.partitions

This is easily the configuration you will interact with and fine-tune the most. It dictates the number of output partitions generated after wide transformations (such as joins or aggregations).
- The Default: It defaults to 200.
- The Reality: There is no one-size-fits-all number. For tiny datasets, 200 partitions is complete overkill and leads to massive scheduling overhead with lots of empty partitions. For terabytes of data, 200 is drastically insufficient and will easily crash your executors with Out-of-Memory (OOM) errors. You must treat this config as a dynamic dial that you adjust based on the scale of your specific data.

## Broadcast variables and Accumulators

If broadcast variables are the top 1 interview question (they really come up often) and you might actually encounter them in practice too, accumulators are a very rare question, since in practice you'll meet them with a 0.1% probability.

Accumulators: https://sparkbyexamples.com/pyspark/pyspark-accumulator-with-example/.
Broadcast variables: https://sparkbyexamples.com/spark/spark-broadcast-variables/.

If anyone wasn't paying attention, I'll explain broadcast here: the gist is that when you use a certain variable, for example during a filter, this variable is sent along with the task for execution. As you remember, one task equals one partition, meaning if you are filtering a dataframe with 500 partitions, this variable will be sent 500 times. Sounds terrible, but it's not critical with primitives like Int or String. However, when it comes to, say, dictionaries of N elements, it's not so cool anymore. Therefore, you can make the variable a broadcast variable, thereby sending it at the beginning of the stage (I think) into the storage memory, where it will be kept. So it will be sent not 500 times, but only m times (where m is the number of executors). Profit? Profit. 
Accumulators are very rare, so the main thing is to know what they are for, the details are no longer important.

## PySpark serializator

Generally, you've already read about Spark serializers. Well, that was Scala, and most people even think that PySpark has the exact same ones. But that's not true. If you try to catch a serializer error (believe me, you'll catch one eventually), the error will say something about pickle, the very same Python serializer. Python has another one, marshal, which guides claim is faster than pickle. By the way, exactly because of the quirks of PySpark and how its serializers work, there are some limitations that don't exist in Scala. For example, with foreach, where in Scala you can pass objects created outside of foreach, but Python's pickle will yell that the thread is locked (I ran into this myself).

Actually, it's probably worth saying here that for more serious development, Scala is still miles better, but readability and simplicity still go to PySpark. There are a ton of nuances that cause certain things to not work in Python. I won't go too deep into it because I don't fully understand it myself, but I've noticed more than once how theoretically identical code written in Scala and Python yields different query plans (with Scala's obviously being better).

## AQE

You've heard about this amazing machine many times before. 
Article: https://sparkbyexamples.com/spark/spark-adaptive-query-execution/.
Of course, it's a cool and useful thing, but it cannot solve all problems on its own (otherwise, why would they need us?)))), so this thing serves to ensure that if you happen to miss something or, for example, different data arrives one time, your process won't crash but will work as intended. But in general, things like balancing data after a Shuffle it handles even better than a human (since, after all, it knows all the metrics at runtime).

## Why Dataframe and Dataset, but not RDD

Generally, everything is obvious, the optimizer doesn't optimize RDDs, and writing on the RDD API is 1000 times harder. Therefore, wherever possible, dataframe is used, while dataset doesn't exist in pyspark because it is only for compiled languages, that is, for Scala. RDD is used only in one case: if the file is txt or another completely unstructured one.

## How to read files

First, in your own words.
spark.default.parallelism (default: Total No. of CPU cores) — for RDDs, the amount of partitions after a shuffle, and as we'll see, used to calculate the size.
spark.sql.files.maxPartitionBytes (128 mb default) — the maximum data size of a partition when reading from a file.
spark.sql.files.openCostInBytes (default: 4 MB) — the estimated size of additional overhead data when reading from a file (this is only accounted for after we pack a portion of the file. Example: the partition size limit is 128 MB, the open cost is 4 MB. A 40 MB file is taken, placed into the partition, and 4 MB of overhead is added. Then another 40 MB file is taken; it fits, so we place it and add another 4 MB on top. Then one more 40 MB file is taken; it fits, so we place it too. Total: 3 files packed into one partition).
maxSplitBytes = Minimum(maxPartitionBytes, bytesPerCore)
bytesPerCore = (Sum of sizes of all data files + No. of files * openCostInBytes) / default.parallelism

Now, a bit more detail. Basically, you have various files. After calculating the parameters, you get the target size of a single partition.
After that, Spark will look at the files. If they are larger than the calculated partition size and are splittable, it will divide the file into chunks equal to the partition size, until the last chunk is less than or equal to the partition size. If the files are smaller than the partition or are non-splittable, it will leave them exactly as they are.
And so, from these resulting files (or chunks), it will start forming the partitions. At the same time, every time it adds a file chunk or a whole file into a partition, it adds that spark.sql.files.openCostInBytes overhead.
And here I actually have a question myself: what if it's a Parquet file? Once it reads the data, it will get a much larger volume of data (since Parquet is compressed). Here I'm honestly powerless because I don't know myself, so I'll leave this question open.
You might ask, why is all this necessary? So you know exactly how many partitions you will have after reading the files. In reality, you almost always need to manage this number, at least approximately.

Here is an article: https://dzone.com/articles/guide-to-partitions-calculation-for-processing-dat.

## How to save files

Here will be an article in which everything is explained brilliantly.
Article: https://mungingdata.com/apache-spark/partitionby/.

## UDF

When built-in functionality isn't enough, UDFs (User Defined Functions) come to the rescue. Essentially, it's just a regular function, but designed for working with columns. There are three types:
- Scala UDF: Obviously the fastest option.
- Pandas UDF: Takes second place because it works with vectors (vectorized operations).
- PySpark UDF: The slowest option, as it processes data element by element.
  
In Scala, you will obviously only use Scala UDFs, but in PySpark, regular PySpark UDFs are the most commonly used. 
However, if the execution of a UDF becomes a performance bottleneck, it is highly recommended to replace it with a Pandas UDF.
Best Practice: Overall, it is better to avoid using them altogether. The Spark optimizer cannot optimize UDFs (since it has no idea what you wrote inside that black box), and PySpark UDFs, in particular, are genuinely sluggish.
