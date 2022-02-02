from pyspark.conf import SparkConf
from pyspark.ml import Pipeline, classification, evaluation, feature
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, IntegerType, StructField, StructType

conf = SparkConf()
conf.set("spark.logConf", "true")
spark = (
    SparkSession.builder.appName("ml")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")


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
        StructField("potability", IntegerType(), True),
    ]
)


def run():
    build_model()


def build_model():
    df = spark.read.csv("./water_potability.csv", header=False, schema=schema)
    df = df.na.drop(how="any")
    df.createOrReplaceTempView("df")
    df_train, df_eval = df.randomSplit([0.8, 0.2], 42)

    vectorizer = feature.VectorAssembler(
        inputCols=df.columns[:-1], outputCol="features_raw"
    )
    scaler = feature.StandardScaler(
        inputCol="features_raw",
        outputCol="features",
    )
    forest = classification.RandomForestClassifier(
        featuresCol="features",
        labelCol="potability",
        maxDepth=12,
        minInstancesPerNode=2,
        seed=42,
    )

    pipe = Pipeline(stages=[vectorizer, scaler, forest])
    model = pipe.fit(df_train)

    binaryevaluator = evaluation.BinaryClassificationEvaluator(labelCol="potability")
    multievaluator = evaluation.MulticlassClassificationEvaluator(
        labelCol="potability", metricName="accuracy"
    )
    transformed = model.transform(df_eval)
    bineval = binaryevaluator.evaluate(transformed)
    muleval = multievaluator.evaluate(transformed)
    print(f"bineval: {bineval}\n muleval: {muleval}")

    model.save("./model")
