from pyspark.conf import SparkConf
from pyspark.ml import Pipeline, classification, evaluation, feature
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, IntegerType, StructField, StructType


def predownload():
    conf = SparkConf()
    conf.set("spark.logConf", "true")
    spark = (
        SparkSession.builder.appName("ml")
        .config(
            "spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0"
        )
        .getOrCreate()
    )
