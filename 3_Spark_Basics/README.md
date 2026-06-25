<h1 align="center">Spark Basics</h1>


## Description

In this lesson we will describe how Spark work. We will build our own distributed system.

## Pre-requirements

Spark, Hadoop, Java JDK.

## Cluster Theory

Before we can dive into optimizations and the internal workings of Spark itself, we first need to get familiar with the concepts of a distributed computing system - which is exactly what Spark is.
Essentially, the system's architecture rests on 6 core concepts:

- Executor
- Worker
- Driver
- Master
- Cluster Manager
- Cluster 

Here is an example of the entire system in the image below.

<p align="center">
<img src="https://miro.medium.com/max/3334/1*9rdJjMwXXaBXDddxRLPFlw.jpeg" width="80%"></p>

Let's take it one step at a time.

### Cluster

A cluster refers to all computing resources (whether they are servers or simply standalone computers) that make up the system. 
A cluster is a set of tightly or loosely coupled computers connected through a LAN (Local Area Network). 
The computers in the cluster are usually called nodes. Each node in the cluster can have separate hardware and its own Operating System, or can share them. 
Resource (node) management and task execution across the nodes are controlled by a software called a Cluster Manager.

### Worker

A computer (or server) whose resources will be utilized to run Spark. 
For example, in Databricks, when creating a cluster, you see an option to select a worker node, and after selecting it, you can specify their quantity. 
Essentially, these are machines connected over a network to work collaboratively.

### Executor

An executor is nothing more than a process running within a JVM (Java Virtual Machine). 
There can be multiple executors on each worker; how to choose the right number will be discussed below. 
The worker itself, as you understand, does not actually execute tasks; all the work is done by the executors, which utilize the worker's resources.

P.S. Essentially, a worker is a piece of hardware equipped with software, while an executor is a process that performs the work using that hardware's resources.

### Master

The machine from which the code is submitted for execution. Essentially, it is the place where you write the code, nothing more.

### Driver

The Driver is also a process, which, depending on the deployment mode, can run either on the Master machine (client mode) or on one of the worker nodes (cluster mode).
Obviously, cluster mode is used for production, because the driver constantly communicates with the executors, and if you are sitting in Minsk while the server is in Moscow, the network latency will be greater than the execution time itself.

The main() method resides in the driver, which creates the SparkContext (SparkSession starting with the DataFrame API), acting as the logical center of Spark. Its responsibilities include:

- Slicing the code into jobs, stages, and tasks (more on what these are below).
- Creating the Logical Plan, Physical Plan, etc. (explanation also below).
- Coordinating with the cluster manager to dispatch tasks to the executors for execution.
- Tracking execution progress (monitoring what is running, where, and at what stage).

### Cluster manager

There are several types of Cluster Managers:

- Spark Standalone Cluster Manager: The most basic option, which comes bundled with Spark itself. It requires essentially no setup))
- Apache Mesos: A bit more complex and powerful, but while the Standalone manager is used for testing purposes, I have honestly never seen Mesos used in practice.
- Hadoop YARN: Before Kubernetes (k8s) entered the market, this was one of the best solutions. However, due to its architectural specifics, it is used less frequently nowadays - for example, mostly in managed cloud solutions (like AWS EMR).
- Kubernetes (k8s): The best option, and the one you will encounter most often. You can read up on how k8s works online; I will just mention that in the context of Spark, one executor = one pod. This adds an extra layer of flexibility.

In general, the Cluster Manager is responsible for allocating resources. If we run a task in cluster mode, this software (remember, the cluster manager is a piece of software) first spins up the driver. 
The driver then says, "I need this many executors with these specific resources," and sends a request to the cluster manager. The cluster manager then goes and spins up everything requested.
In client mode, the driver is spun up locally on your machine, but provisioning the executors still falls entirely on the shoulders of the cluster manager.

Here's a great example of how it all works:

Working Process

spark-submit –master <Spark master URL> –executor-memory 2g –executor-cores 4 WordCount-assembly-1.0.jar

 
1) Let’s say a user submits a job using “spark-submit”.
2) “spark-submit” will in-turn launch the Driver which will execute the main() method of our code.
3) Driver contacts the cluster manager and requests for resources to launch the Executors.
4) The cluster manager launches the Executors on behalf of the Driver.
5) Once the Executors are launched, they establish a direct connection with the Driver.
6) The driver determines the total number of Tasks by checking the Lineage.
7) The driver creates the Logical and Physical Plan.
8) Once the Physical Plan is generated, Spark allocates the Tasks to the Executors.
9) Task runs on Executor and each Task upon completion returns the result to the Driver.
10) Finally, when all Task is completed, the main() method running in the Driver exits, i.e. main() method invokes sparkContext.stop().
11) Finally, Spark releases all the resources from the Cluster Manager.

## Cluster practice (and theory)

Now we're going to set up our own cluster on our machine.

Open the cmd (assuming you've set up Spark as described in my guide) and type the following right there 
```
spark-class org.apache.spark.deploy.master.Master
```
This is nothing more than declaring the master for your cluster. In general, Spark provides a wide range of scripts to automatically spin up all this stuff, but unfortunately, they don't work on Windows (Linux only). Therefore, we will be doing everything by hand.
After executing the code above, you should see the following output:

![image](https://user-images.githubusercontent.com/113685144/192796311-57f796a6-c35e-4aac-9ee3-d9467c5a2da0.png)

Now you can take the MasterUI URL and open it in your web browser. This is nothing more than a UI where you can find everything about your cluster: what it consists of, what tasks it is running, and so on. It is used to monitor your cluster's operations in real-time. As for the master itself, it is spun up at the address specified in this line: Starting Spark master at spark://...

Next, we need to spin up, for example, two workers.
Open a new CMD window and enter the following:
```
spark-class org.apache.spark.deploy.worker.Worker spark://<master address> --cores 2 --memory 3g
```
This will create a worker on your computer with 2 cores and 3GB of RAM. Spark counts logical cores; for example, I have 6 cores with 2 threads each, which means 12 cores as far as Spark is concerned.
To verify that it was successfully created, check the UI and you will see Workers (1).
Note: Do not switch networks while setting all of this up, because the addresses will obviously change.
Let's create another worker, but this time with 3 cores and 4GB of memory.

```
spark-class org.apache.spark.deploy.worker.Worker spark://<master address> --cores 3 --memory 4g
```
A second Worker should appear in Spark UI.
Your cluster is now ready for action.

##  A little (actually, a lot) of theory about jobs, stages, tasks, the optimizer, tables, and types of optimizations in the optimizer

Before you start running the code, you first need to understand how everything works on this cluster.
In this article, you’ll learn about the aforementioned jobs, stages, and tasks.

- https://blog.dataengineerthings.org/deep-dive-into-spark-jobs-and-stages-481ecf1c9b62

An article about the optimizer in Spark: https://g1thubhub.github.io/catalyst.html

We have already mentioned the logical optimizations applied by the optimizer when converting a logical plan into an optimized logical plan several times. 
All of these optimizations are known as rule-based optimizations. Now, it's time to find out exactly what they are:

- Predicate pushdown — rows. In other words, if you write code where the first line reads the data and then somewhere near the end you filter by a key (for example, keeping only a True flag), Spark will perform this filtering as close to the data source file as possible (if feasible, of course) to reduce the number of rows as early as possible. On top of that, this row filtering can happen right at the file-reading stage (meaning that as it reads the data, rows are already being filtered out).
- Projection pushdown — columns. The exact same thing, but with fields. For example, recall Parquet, which allows reading only the specific columns that we actually use.
- Partition pruning — generally speaking, this applies when Spark uses a Hive Metastore DB to store all kinds of metadata about tables. If we are talking about Databricks, Spark uses this DB, but if it's regular local Spark, it uses a default embedded DB (if you want a Hive Metastore, you need to configure it additionally). This feature is only used on tables via Spark SQL, meaning it is not applicable to regular DataFrames (unless I'm missing something).
Here is an article that begins with an explanation of the concept of partitioning pruning: http://www.openkb.info/2021/03/spark-tuning-dynamic-partition-pruning.html.

In short, the core idea is that when performing a conditional join, instead of joining both tables immediately, you can first run a subquery that filters one table, then broadcast the resulting values to all executors to filter the second table there, and only after that perform the join on the already filtered tables. It works great and all, but it immediately makes you wonder why this only works with tables: because how would you write something like that using the DataFrame API syntax? You can't; you would manually filter one table first and then join them both.
Tables in this case refer to actual tables. What follows is a long and rather heavy section, so pay close attention.

Tables in Spark are not like tables in a traditional database because they are stored as files. Therefore, ACID principles do not apply to them. 
Even worse, since these are just files, you cannot perform UPDATE, DELETE, or - most importantly - MERGE operations on them. Yes, you can run SQL queries against them just like in a regular database, thanks to the Hive Metastore DB or Spark's default metastore, but for better or worse, they are still just files.

And this is where the well-known Delta Lake comes into play with its Delta tables. Essentially, they are the same files, but way cooler and more powerful, because they are now fully ACID-compliant. Plus, using the Delta API, you can perform DELETE, UPDATE, and MERGE operations, as well as maintain a version history (you will learn about Delta Lake in much greater detail later).
Now, another thing you need to know about tables is that they can be either managed or external. The point is that Spark also includes a Spark Warehouse (Hive Warehouse). This is the storage location where Spark keeps its managed tables.

The difference is as follows:

Managed table - a table that is fully managed by Spark. Specifically, Spark stores not only the metadata in the Hive Metastore, but also the actual data files of this table within the Spark Warehouse. If you delete the table, you delete both the metadata and the actual data itself. It is created like this:

spark.sql("CREATE TABLE employee (name STRING, emp_id INT,salary INT, joining_date STRING)")

or like this 

df= spark.read.format("csv").option("inferSchema","true").load("/FileStore/tables/Order.csv")

df.write.saveAsTable("OrderTable").

External table - a table whose data (files) is stored outside the Spark Warehouse. Spark only knows that it is stored at a specific location and maintains its metadata. If you delete such a table, Spark will only remove the metadata, while the actual data files will remain intact. It is created like this:

spark.sql("""CREATE TABLE OrderTable(name STRING, address STRING, salary INT) USING csv OPTIONS (PATH '/FileStore/tables/Order.csv')""").

For the most part, tables are only used with Databricks, which has Hive and its own HDFS storage under the hood, but which specific table type to use is up to the project architect's preference.

Unfortunately, that's not all the theory. Next up are the optimizations that the optimizer uses when choosing a physical plan. These are called cost-based optimizations. We could really go down a rabbit hole here, but since this is best shown alongside practical examples, let me just give you one example: you have a join. Spark has 5 types of joins (we will definitely cover them, just not today), and depending on the settings you configured (like spark.sql.autoBroadcastJoinThreshold, for instance), Spark will look at the input data statistics and decide which of the 5 joins to use.

You will learn exactly what optimizations Spark performs at this stage in future topics. For now, I'll just mention that there is also something called AQE (Adaptive Query Execution), which doesn't just rely on initial input data; instead, it looks at runtime statistics to decide what's best. In other words, the initial plan might look one way, but later at runtime - after you've already filtered and transformed something - the statistics might change, making the old plan suboptimal. This is where AQE comes to the rescue: it collects statistics after each shuffle and checks whether it needs to dynamically adjust the execution plan. This amazing feature arrived with Spark 3.0 and is actively used.

The choice of a physical plan is also influenced by CBO (Cost-Based Optimization). It only works on tables (meaning Spark SQL); it's obviously useless for raw DataFrames or RDDs, but it helps tremendously with tables. You have to enable it and manually write code to trigger Spark to compute table statistics; only then will CBO kick in. You will learn more about AQE and CBO, as well as the specific optimizations they perform, a bit later—once you understand what can actually be optimized in Spark and why it matters in the first place.


## DAG, narrow wide transformations

Narrow and Wide Transformations (yes, they already appeared in a previous article, but we need to reinforce this concept): https://sauravomar01.medium.com/wide-vs-narrow-dependencies-in-apache-spark-2cd33bf7ed7d

DAG — remember the image from the previous article on RDD Lineage? Well, this is exactly what it is. A Directed Acyclic Graph shows the journey of your RDDs from start to finish, specifically detailing which operations are performed on them, etc. Article: https://www.tutorialkart.com/apache-spark/dag-and-physical-execution-plan/.

And lastly, how to read a query plan: https://blog.rockthejvm.com/reading-query-plans/.


## Running code on a cluster

Before you take a look at your cluster in action and check out the various metrics in the Spark UI, here’s an article about what you can actually find in the Spark UI: 
https://spark.apache.org/docs/latest/web-ui.html

Here's a brief explanation of cache and persist: https://stackoverflow.com/questions/26870537/what-is-the-difference-between-cache-and-persist. 
You should also check how the Spark application is launched: https://sparkbyexamples.com/spark/spark-submit-command/.

Since analytics in the Spark UI are only available in real-time, you need to configure a folder to store the history of these analytics so you can view them later. 
To do this, you need to create a folder named for_history inside this directory (3_Spark_Basics). 
To ensure the history is saved there and you can view all the statistics in the History Server later, you need to add these lines:

```
spark.eventLog.enabled true
spark.eventLog.dir file:///C:/Users/stepa/Desktop/spark_demo/3_Spark_Basics/for_history
spark.history.fs.logDirectory file:///C:/Users/stepa/Desktop/spark_demo/3_Spark_Basics/for_history
```

using your own specific path to the folder, of course. You need to enter these lines into the spark-defaults.conf file, which is located at this path: ...\spark-3.1.3-bin-hadoop2.7\conf
Note: You will first need to remove the .template extension from the filename spark-defaults.conf.template. If you cannot see the extension, make sure to enable View -> File name extensions in your Windows File Explorer.
Once the configuration is saved, you need to start the History Server. To do this, open a new CMD window and run:

```
spark-class org.apache.spark.deploy.history.HistoryServer
```

This command will start the server that reads the history of completed applications. The server address will be displayed after the command executes (just like it was with the master address). Therefore, once your application finishes running, you need to go to the address specified during the history server startup to inspect your application.

To ensure Spark detects Python 100% of the time, rename the file spark-env.sh.template to spark-env.cmd and add the lines below (the file is located at this path: ...\spark-3.1.3-bin-hadoop2.7\conf). 
Naturally, you need to specify your own paths, which will look almost exactly the same.

```
set PYSPARK_PYTHON=C:\users\stepa\appdata\local\programs\python\python39\python.exe
set PYSPARK_DRIVER_PYTHON=C:\users\stepa\appdata\local\programs\python\python39\python.exe
```

The code file is already prepared and named spark_basics.py. In it, you need to change the paths for reading df_people, df_country, and df_parquet, as well as for writing df_last, plans1.txt, and plans.txt.

After that, you need to run it and look at the various metrics in the Spark UI (if you don't make it in time while the application is running, hurry over to the History Server), as well as the query plans that will be saved to a separate file named plans.txt or plans1.txt. Compare the execution plan with the code in spark_basics.py, and compare the different plans (logical vs. physical, or any others).

Also, make sure to go to the SQL tab in the History Server (at the top where Jobs, Stages, etc., are located) and explore everything interactively. 
The more advanced article on reading plans explains quite well how to interpret everything there.

After your self-review, make sure to take a look at "Explanation of Query Plans.docx" to check out the nuances that you absolutely need to see.

Note: Yes, the physical plan can be found in the Spark UI (History Server) under the DAG in the SQL tab. However, only the physical plan is shown there, whereas the .txt file will contain all of them.
Note 2: The History Server is the exact same thing as the Spark UI, except it stores completed runs, while the active Spark UI shows what is happening in real time.
