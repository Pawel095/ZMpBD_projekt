from pyspark.conf import SparkConf
from pyspark.ml.pipeline import Pipeline
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.window import Window
from pyspark.streaming import StreamingContext
from pyspark.sql import functions as f
from decouple import config
from pyspark.ml import PipelineModel
from pyspark.sql import Row
from pyspark.sql.types import (
    DoubleType,
    StructField,
    StructType,
    StringType
)

KAFKA_URL = "{ip}:{port}".format(
    ip=config("KAFKA_SERVER_IP"),
    port=config("KAFKA_SERVER_PORT", cast=int),
)
IN_TOPIC = config("KAFKA_INPUT_TOPIC")
OUT_TOPIC = config("KAFKA_OUTPUT_TOPIC")

schema = StructType(
    [
        StructField("ph", DoubleType(), True),
        StructField("hardness", DoubleType(), True),
        StructField("solids", DoubleType(), True),
        StructField("chloramines", DoubleType(), True),
        StructField("sulfate", DoubleType(), True),
        StructField("conductivity", DoubleType(), True),
        StructField("organic_carbon", DoubleType(), True),
        StructField("trihalomethanes", DoubleType(), True),
        StructField("turbidity", DoubleType(), True),
        StructField("job_id", StringType(), True),
    ]
)
ccols = [
    "ph",
    "hardness",
    "solids",
    "chloramines",
    "sulfate",
    "conductivity",
    "organic_carbon",
    "trihalomethanes",
    "turbidity",
    "potability",
]

conf = SparkConf()
conf.set("spark.logConf", "true")


def start():
    spark = (
        SparkSession.builder.appName("ml")
        .config(
            "spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0"
        )
        .getOrCreate()
    )
    # spark.sparkContext.setLogLevel("ERROR")
    print("Python started")

    fit_pipe = PipelineModel.load("./model")

    stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_URL)
        .option("failOnDataLoss", "false")
        .option("subscribe", IN_TOPIC)
        .option("includeHeaders", "true")
        .load()
    )

    parsed = stream.select(
        f.from_json(stream.value.cast("string"), schema).alias("json")
    ).select("json.*")

    temp1 = (
        fit_pipe.transform(parsed)
        .select(["prediction","job_id"])
        .withColumnRenamed("job_id", "key")
        .withColumnRenamed("prediction", "value")
        .selectExpr("CAST(value as STRING)","CAST(key as STRING)")
    )

    out = (
        temp1.writeStream.outputMode("append")
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_URL)
        .option("topic", OUT_TOPIC)
        .option("checkpointLocation", "checkpoint")
        .start()
    )

    console = (
        temp1.writeStream.outputMode("append")
        .option("truncate", "false")
        .format("console")
        .start()
    )
    out.awaitTermination()
    console.awaitTermination()


if __name__ == "__main__":
    start()