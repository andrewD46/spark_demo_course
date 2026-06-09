<h1 align="center">Memory management</h1>


## Description

Here you'll learn how to manage memory in Spark, as well as how it works in general.


## Spark Memory

To be honest, the Spark developers are really great at what they do, and the default memory management configs they provide are quite solid - most of the time, you don't even need to touch them.
However, every situation is different. You can even find a few articles on Habr where people talk about squeezing unbelievable performance out of their clusters, partly by tuning memory management. 
So, let's put it this way: it might seem useless to the average user, but they can definitely ask you about it in an interview. So, let's dive in.

Article about Spark Memory Management and its types - https://medium.com/@vtrkayalrajan/spark-memory-management-and-its-types-425af52d7c15

Here's another article that focuses solely on memory in the JVM (it goes into a bit more detail about what exactly is stored in the JVM's memory segments):
https://medium.com/analytics-vidhya/apache-spark-memory-management-49682ded3d42.
