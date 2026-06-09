<h1 align="center">Different underhood stuff</h1>


## Description

Here you'll learn about various topics that aren't all that important (though they actually have a huge impact on performance, they're much harder to manage), 
but I simply can't leave them out, because they might come up in job interviews (especially in very tough ones).

## Spill effect

Article: https://selectfrom.dev/spark-performance-tuning-spill-7318363e18cb.

## Garbage collection and Serialization

You'll need two sections from the following article ("Data Serialization" and "Garbage Collection Tuning"): https://spark.apache.org/docs/latest/tuning.html.

## Tungsten

Long story short, nobody really knows exactly what this thing fully does under the hood (except the developers themselves, of course). Just for context, those are the words of a Data Engineer with over 10 years of experience, who started working with Hadoop and its ecosystem the very moment it hit the market. Anyway, the developers behind this engine are geniuses, and you are about to understand why.
Let's start with a simple fact: Java objects are huge. The string "abcd" takes up just 4 bytes using standard UTF-8 encoding, but a Java object holding this exact same data will weigh in at 48 bytes! 
This includes the object header, hash code, metadata, and the characters themselves. Crazy, right? Virtual function calls (or whatever they're called in Java) are also really heavy.
This is exactly where Tungsten comes to the rescue. Its developers really understand hardware, so Tungsten works directly with binary data. Simply put, if you need to calculate A + B, in standard Java this means taking object A, then object B, calling a virtual function, performing the calculations inside of it, and only then returning the answer.
Tungsten, on the other hand, says that A + B is just A + B and you don't need to call anything at all (assuming we are dealing with primitive types, like an int). It basically says: take the binary for A, take the binary for B, and execute the operation, using algorithms that take full advantage of the CPU cache (meaning, algorithms that sit very close to bare-metal hardware).
Because of this, at the end of the optimizer's physical plan, you will sometimes see Tungsten listed as its own separate block (Whole-Stage Code Generation) - because that is exactly what it's doing. Tungsten translates all the code into machine code, picking the fastest and most efficient algorithms available.
I think you remember off-heap memory. If you save a DataFrame in standard memory (using the cache function), it's going to weigh a ton. Tungsten helps bypass that object bloat.
Save it in off-heap memory, and it will take up a fraction of the space. In fact, as you may have read, String objects are actively stored and processed in off-heap memory.
Also, the Tungsten shuffle leaves other shuffle strategies in the dust (which you have read all about). This is precisely because, if you remember, when a buffer (whether it's a read buffer or a write buffer) runs out of memory, it spills data to the disk. At this point, as you understand, the data gets serialized so it can be written to the disk. Normally, it would then have to be deserialized, sorted, merged, serialized again, and written back to the disk once more before being sent out.
Well, Tungsten actually knows how to sort binary data. This means there is zero deserialization involved - it simply takes all the files on the disk, sorts them together, and leaves them exactly as they are in their serialized form. Think this isn't a big deal? It is hugely important because the serialization and deserialization process is incredibly heavy and resource-intensive.
To summarize:
- It transforms the physical plan into a set of machine instructions.
- It can work directly with binary data, which saves a massive amount of overhead on serialization and deserialization cycles.
- Tungsten objects weigh significantly less than standard Java objects.

Here is an article about Project Tungsten, which hopefully shouldn't be too hard to understand now after my introduction:
https://www.databricks.com/blog/2015/04/28/project-tungsten-bringing-spark-closer-to-bare-metal.html.

