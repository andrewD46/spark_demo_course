<h1 align="center">Delta lake</h1>


## Description

Here you'll discover the already famous Delta Lake.


## Delta Lake concept

The core idea is actually quite simple: regular files in a data lake are just sitting there in storage. You cannot perform MERGE, UPDATE, or DELETE operations on them because they are simply files and lack ACID transaction support. But in reality, having that capability is incredibly desirable. Enter Delta Lake.
Its underlying concept is straightforward: we store Parquet files, but we accompany them with a JSON file (transaction log) that records all information about data loads, which data is currently valid, and so on.
Thanks to this, our data is now compliant with ACID properties. Using the Delta API, we can now execute operations like UPDATE, DELETE, and MERGE. We also get the ability to time travel (yes, Delta Lake allows you to look at the data you loaded yesterday, even if it has been updated since). This works because Delta Lake doesn't just delete files outright; it simply marks them as obsolete. The JSON log still retains the knowledge that those files belonged to a previous version. To physically remove the old files, you have to explicitly use the VACUUM command.

Two major architectural concepts are built on top of this technology:
- The Medallion Architecture (by Databricks): Organizing data logically into Bronze, Silver, and Gold layers.
- The Data Lakehouse: Combining the best elements of data lakes and data warehouses.

## Delta Lake API

Link: https://docs.databricks.com/delta/index.html. Read everything in tab Delta Lake.
