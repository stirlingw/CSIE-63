from pyspark import SparkConf, SparkContext, SQLContext
from pyspark.sql import SQLContext, SparkSession, Row
from pyspark.sql.types import *
import pyspark.sql.functions as psf
import re

conf = (
            SparkConf()
            .setAppName("assignment-4")
            .set("spark.executor.instances", 1)
            .set("spark.executor.cores", 1)
            .set("spark.shuffle.compress", "true")
            .set("spark.io.compression.codec", "snappy")
            .set("spark.executor.memory", "4g")
)

sc = SparkContext().getOrCreate(conf = conf)
sc.setLogLevel("ERROR")
sqlContext = SQLContext(sc)
spark = SparkSession.builder.appName("spark play").getOrCreate()


### Stop Words
# Obtained a list of stop words from the following URL
# http://www.lextek.com/manuals/onix/stopwords1.html
stop_words_rdd = sc.textFile("file:////Users/swaite/Stirling/CSIE-63/assignment-4/data/inputs/stop-words.csv")
print(stop_words_rdd.take(10))

# Use Spark transformation and action functions present in RDD API to transform those texts into RDD-s
# that contain words and numbers of occurrence of those words in respective text.
### King James Bible
# 1.  Splits on each word
# 2.  Gets rid of un-needed non-alpha characters
# 3.  Filters out any words that are Null or Empty
# 4.  Converts each word to lower case and encodes word into UTF-8 format
# 5.  Removes words that are stop words
# 6.  Group By word, and does frequency count for each word
# 7.  Sorts by frequency count
bible_rdd = sc.textFile("file:////Users/swaite/Stirling/CSIE-63/assignment-4/data/inputs/clean_bible.txt")\
              .flatMap(lambda x: x.split()) \
              .map(lambda x: re.sub("[^a-zA-Z]+", "", x.lower().encode("utf-8", "ignore"))) \
              .filter(lambda x: x != "") \
              .subtract(stop_words_rdd) \
              .map(lambda word: (word, 1)) \
              .reduceByKey(lambda x, y: x + y)\
              .sortBy(lambda x: x[1], ascending=False)

# List for us 30 most frequent words in each RDD (text). Print or store the words and the numbers of occurrences.
print "30 most frequent words in King James Bible"
print(bible_rdd.take(30))
print(bible_rdd.count())


### Ulysses by James Joyce
# 1.  Splits on each word
# 2.  Gets rid of un-needed non-alpha characters
# 3.  Filters out any words that are Null or Empty
# 4.  Converts each word to lower case and encodes word into UTF-8 format
# 5.  Removes words that are stop words
# 6.  Group By word, and does frequency count for each word
# 7.  Sorts by frequency count

ulysses_rdd = sc.textFile("file:////Users/swaite/Stirling/CSIE-63/assignment-4/data/inputs/4300-2.txt") \
                .flatMap(lambda x: x.split()) \
                .map(lambda x: re.sub("[^a-zA-Z]+", "", x.lower().encode("utf-8", "ignore"))) \
                .filter(lambda x: x != "") \
                .subtract(stop_words_rdd) \
                .map(lambda word: (word, 1)) \
                .reduceByKey(lambda x, y: x + y) \
                .sortBy(lambda x: x[1], ascending=False)

# List for us 30 most frequent words in each RDD (text). Print or store the words and the numbers of occurrences.
print "30 most frequent words in Ulysses"
print(ulysses_rdd.take(30))
print(ulysses_rdd.count())

# Create for us the list of 20 most frequently used words common to both texts.
print "Create for us the list of 20 most frequently used words common to both texts."
combined_rdd = bible_rdd.join(ulysses_rdd)

# In your report, print (store) the words, followed by the number of occurrences in Ulysses and then the Bible.
print "In your report, print (store) the words, followed by the number of occurrences in Ulysses and then the Bible."
print(combined_rdd.take(10))
print(combined_rdd.count())

# Order your report in descending order starting by the number of occurrences in Ulysses.
print "Order your report in descending order starting by the number of occurrences in Ulysses."
combined_bible_rdd = combined_rdd.map(lambda (x, y): (x, y[0]))\
                                 .sortBy(lambda x: x[1], ascending=False)
print(combined_bible_rdd.take(100))
print(combined_bible_rdd.count())

# Present the same data this time ordered by the number of occurrences in the Bible.
print "Present the same data this time ordered by the number of occurrences in the Bible."
combined_ulysses_rdd = combined_rdd.map(lambda (x, y): (x, y[1])) \
                                   .sortBy(lambda x: x[1], ascending=False)
print(combined_ulysses_rdd.take(100))
print(combined_ulysses_rdd.count())

# List for us a random samples containing 5% of words in the final RDD.
print "List for us a random samples containing 5% of words in the final RDD."
five_perc = int(combined_rdd.count() * 0.05)
print "Sample of 5 percent common words to both books: {0}".format(combined_rdd.takeSample(False, five_perc, seed=13))

