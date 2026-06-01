<h1 align="center">Types of files</h1>


## Description

In this task you will see more information about different types of files.

## Parquet

Parquet is a fairly complex format compared to, say, a standard text file containing JSON. 
Notably, the roots of this format can be traced back to Google's developments, specifically to their project called Dremel. 
This has already been mentioned on Habr, but we won't delve into the details of Dremel here; those interested can read more about it at: research.google.com/pubs/pub36632.html.

In short, Parquet uses an architecture based on "definition levels" and "repetition levels," which allows for highly efficient data encoding, 
while the schema information is extracted into separate metadata. At the same time, empty (null) values are stored optimally.

The structure of a Parquet file is well illustrated in the documentation:

<p align="center">
<img src="https://habrastorage.org/files/00c/814/4e6/00c8144e68f14eb388f8636717a7667a.gif" width="80%"></p>

Files have multiple levels of partitioning, which enables highly efficient parallel execution of operations over them:

Row group: A partitioning level that allows for parallel data processing at the MapReduce level.

Column chunk: Partitioning at the column level, which allows for the distribution of I/O operations.

Page: The division of columns into pages, allowing for the distribution of encoding and compression workloads.

If you save data to a Parquet file on disk using a conventional file system, you will find that instead of a single file, a directory is created containing an entire collection of files.
Some of these are metadata files containing the schema and various auxiliary information, including a partial index that allows reading only the required data blocks during a query.
The remaining parts, or partitions, are precisely our Row groups.

For an intuitive understanding, let's consider Row groups as a set of files united by common information. By the way, this partitioning is used by HDFS to achieve data locality, 
where each node in the cluster can read the data located directly on its own disk. Furthermore, a row group acts as a single MapReduce unit, and each map-reduce task in Spark works with its own row group. 
Because of this, a worker is required to load the row group into memory. When configuring the row group size, you must consider the minimum amount of memory allocated per task on the weakest node in the cluster; otherwise, you might run into an OOM (Out of Memory) error.

Column chunk (partitioning at the column level) optimizes disk I/O. If you visualize the data as a table, it is written not row by row, but column by column.

Here is a table:

<p align="center">
<img src="https://habrastorage.org/r/w1560/files/469/897/dae/469897dae11f4b159afd1f2bef6d5d6d.png" width="50%"></p>

In that case, in a text file, for example CSV, file we would store the data on disk something like this:

<p align="center">
<img src="https://habrastorage.org/files/b4f/916/6d3/b4f9166d324a41f395406d52feec5d7b.png" width="80%"></p>

In the case of Parquet:

<p align="center">
<img src="https://habrastorage.org/files/b45/9aa/ce8/b459aace83f5497aa7dbd37a9e50b493.png" width="80%"></p>

Thanks to this, we can read only the columns we actually need.

Out of the vast variety of columns, an analyst usually only needs a few at any given moment; moreover, the majority of the columns often remain empty. 
Parquet speeds up data processing significantly. Furthermore, this way of structuring information simplifies data compression and encoding due to the homogeneity and similarity of the data.
Each column is divided into pages (Pages), which, in turn, contain metadata and data encoded based on the architectural principles of the Dremel project. 
This achieves highly efficient and fast encoding. In addition, compression is performed at this level (if configured). Currently, available codecs include Snappy, GZIP, and LZO.

Are there any pitfalls?

Due to the specific organization of Parquet data, it is difficult to set up streaming for it - if you transfer data, you have to transfer the entire group. Also, if you lose the metadata or alter the checksum for a data page, the entire page will be lost (if this happens to a column chunk, the chunk is lost, and similarly for a row group). Checksums are generated at each partitioning level, so you can disable their calculation at the file system level to improve performance.

Conclusion:

Advantages of storing data in Parquet:

- Even though it was created for HDFS, the data can also be stored in other file systems, such as GlusterFS or over NFS.
- Essentially, these are just files, which means they are easy to work with, move, back up, and replicate.
- The columnar format significantly speeds up an analyst's workflow if they don't need all the columns at once.
- Native, out-of-the-box support in Spark allows you to easily take a file and save it to your preferred storage.
- It provides highly efficient storage in terms of space consumption.
- As practice shows, this particular format provides the fastest read performance compared to other file formats.


Disadvantages:

- The columnar nature forces you to think carefully about the schema and data types upfront.
- Outside of Spark, Parquet does not always have native support in other products.
- It does not support data modification and schema evolution. Of course, Spark can merge schemas if yours changes over time (this requires specifying a special option when reading), but to change something in an already existing file, you cannot avoid rewriting it entirely, though it is possible to add a new column.
- Transactions are not supported, as these are regular files and not a database.

Note: an article that explains it in other words (https://www.bigdataschool.ru/wiki/parquet?ysclid=l87biclda9504593918) - **rus**

Here's a brief summary from me (if I'm asked about this in the interview, I'll mention something along these lines): 

- First, Parquet is highly optimized for working with Spark.
- Parquet compresses data exceptionally well (slightly worse than ORC, but a solid second place), and I will demonstrate this a bit later in this lesson.
- There is a really cool technology called Delta Lake. I will cover this topic in more detail in later lessons, but for now, you just need to know that Delta Lake works closely with Parquet files.
- Parquet stores data by columns. This means that if you only need x columns, you will only read those x columns—unlike CSV, for example, where you have to read every single column.
- From the PySpark_Basics topic, you should already know that Parquet stores metadata. Because of this, Spark doesn't need to scan all the rows to infer column types and other details like it does with CSV; it simply retrieves that information from the metadata.
- Even though some official documentation might suggest that Snappy compression means a file can only be read as a whole (i.e., it is not splittable), the compression in Parquet is actually performed at the page level. Therefore, you can still read exactly what you need from the Parquet file itself without scanning the entire file.

## ORC

I found only one reliable source that focuses exclusively on this format, so here's the link (https://www.bigdataschool.ru/wiki/orc?ysclid=l87d66i1a4726280864). - **rus**

A quick summary from my side:

- It compresses data better than Parquet, and quite significantly at that.
- It stores data by columns, which again means we only read exactly what we need
- It stores metadata, meaning all necessary information is retrieved from it without having to scan the entire file.

This raises the question: why use Parquet at all if ORC is essentially the same but offers better compression? The answer can be found in this article: (https://medium.com/@dhareshwarganesh/benchmarking-parquet-vs-orc-d52c39849aef).

From my own experience, I can add that Parquet was originally designed for Spark, whereas ORC was built for Hive (Spark used to read vectors natively from Parquet, while Hive read them from ORC). 
Today, both engines can read vectors from either format, so the differences boil down to the following:

- Nested vs. Flat: Choose Parquet if your data is highly nested; choose ORC for flat data structures.
- Compression vs. Speed: Need maximum compression? Go with ORC. Need speed (which is often the main priority)? Then Parquet is your choice.
- ACID Transactions: It's true that Parquet does not natively support ACID transactions unlike ORC, but this is exactly where Delta Lake steps in—it provides ACID support and works specifically with Parquet files.
- Industry Standard: In 99% of cases, you'll end up using Parquet simply because it's faster and more efficient to work with in the Spark ecosystem.

## CSV

Facts:

- Stores data by rows (which means that all columns are always read)
- No compression (p.s. You can compress it using an archiver, such as gz)
- No meta-data

## JSON

Up to this point, all the files we've discussed have been splittable: meaning that within Spark, we have multiple threads ready to read data in parallel. 
If a file is splittable, it will be read by several threads simultaneously.
JSON, however, is not splittable, which means it must always be read in its entirety. 
This can become a massive problem (for example, a 1GB JSON file will be loaded into a single partition because it cannot be divided, 
which can lead to a spill effect or, even worse, an OOM error. We will cover this in more detail in upcoming lessons). Fundamentally, JSON is essentially a key-value structure.
P.S. There actually is a developed extension for JSON (I don't remember by whom) that makes it splittable, but I doubt you will ever encounter it in practice.

## Avro

Article - (https://www.bigdataschool.ru/blog/kafka-big-data-apache-avro.html?ysclid=l87f4mn9lc361070957). - **rus**

I'm not really sure what to say, except that it requires a special Avro schema that it absolutely can't do without. It's better than JSON. I haven't worked with it myself, so I'll move right on to the next one.

## Difference between Avro, Parquet and ORC

I'll attach an article to go over the main types of Big Data files again; it also includes a comparison at the end (https://habr.com/ru/company/vk/blog/504952/?ysclid=l87ddj9j44827638583). - **rus**
 
