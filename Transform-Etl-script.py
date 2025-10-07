

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, length, regexp_replace, when

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Extract: Read from Glue Catalog
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="amazon_db",
    table_name="amazon_csv",
    transformation_ctx="amazonetljob_node1756017061302"
)

# Transform: Convert to DataFrame, clean data
transformed = datasource.toDF()

# Drop rows with null ratings or null discount_percentage
transformed = transformed.na.drop(subset=["rating", "discount_percentage"])

# Clean and cast discount_percentage (remove % and convert to float)
transformed = transformed.withColumn(
    "discount_percentage",
    regexp_replace(col("discount_percentage"), "%", "").cast("float")
)

# Extract the double field from the rating struct and cast to float
transformed = transformed.withColumn(
    "rating",
    when(col("rating.double").isNotNull(), col("rating.double").cast("float")).otherwise(None)
)

# Add a new column for discount tier
transformed = transformed.withColumn(
    "discount_tier",
    when(col("discount_percentage") >= 50, "High")
    .when(col("discount_percentage") >= 25, "Medium")
    .otherwise("Low")
)

# Optional: Filter for high-rated products (uncomment to enable)
# transformed = transformed.filter(col("rating") > 4)

# Load: Write to S3 as Parquet, partitioned by category and discount_tier
transformed.write.mode("overwrite").partitionBy("category", "discount_tier").parquet(
    "s3://analysis-data-lake-bucket/refined/amazon-parquet/"
)

job.commit()