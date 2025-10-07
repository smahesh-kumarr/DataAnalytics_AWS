🎉 AWS Data Lake Pipeline Project - Amazon Dataset 🎉
Welcome to the AWS Data Lake Pipeline Project! 🚀 This repository documents the end-to-end implementation of a data lake to ingest, catalog, transform, query, and secure an amazon.csv dataset using AWS services. Built from scratch on August 25, 2025, this project showcases a scalable solution for managing product data (e.g., category, rating). Let’s explore the journey! 🌟


![AWS Data Lake Architecture](images/Architecture.png)

🌟 Overview of the Project
This project constructs a data pipeline to process and analyze an amazon.csv dataset containing product details. We utilized AWS services to:

📥 Ingest and Store: Load raw data into Amazon S3.
📚 Catalog: Generate metadata with AWS Glue.
🔧 Transform (ETL): Optimize data with Glue Jobs.
📊 Query: Perform SQL queries using Amazon Athena.
🔒 Secure: Enforce access control with AWS Lake Formation.
👀 Monitor: Track operations with CloudWatch.

The pipeline is anchored around the S3 bucket analysis-data-lake-bucket-20250825, Glue database amazon_db, table amazon_csv, and the IAM role glue-etl-role (ARN: arn:aws:iam::747757438809:role/glue-etl-role). 🎯

🚀 Step-by-Step Implementation
Here’s a detailed log of the steps we executed to build this project:
1. 📥 Preparation and Setup (Infrastructure Foundation)

Actions:
Signed into the AWS Console (console.aws.amazon.com) and selected region us-east-1. 🌍
Created S3 bucket analysis-data-lake-bucket-20250825 with:
Block public access enabled. 🔒
Server-side encryption (SSE-S3) activated. 🔐
Versioning enabled for data recovery. 🔄
(Optional) Lifecycle rule planned for future optimization. ⏳
![S3-Buckets](images/S3-Buckets.png)



Created IAM role glue-etl-role with policies:
AWSGlueServiceRole for Glue access. 🛠️
Custom S3 policy for analysis-data-lake-bucket-20250825. 📦
AmazonAthenaFullAccess for querying. 📊
Trust policy updated for glue.amazonaws.com and lakeformation.amazonaws.com. 🔑



(Optional) Set up VPC endpoints for S3 and Glue for private traffic. 🌐


Outcome: Secure infrastructure foundation established. ✅
![Glue-Role](images/Glue-Role.png)

2. 📥 Data Ingestion (Getting Data into the Lake)

Actions:
Prepared amazon.csv with product data (e.g., category, rating). 📋
Uploaded amazon.csv to s3://analysis-data-lake-bucket-20250825/raw/amazon/ via S3 console. 📤
Organized S3 structure with raw/, refined/, and athena-results/ folders. 📂

Outcome: Raw data ingested and stored durably in S3. ✅
![Analyis Data Set and S3 Structure](images/Analysis-Report.png)

3. 📚 Cataloging Data (Metadata Management)

Actions:
Created Glue database amazon_db in the Glue console. 📖
Configured crawler amazon-crawler to scan s3://analysis-data-lake-bucket-20250825/raw/amazon/:
IAM role: glue-etl-role. 🔑
Target database: amazon_db. 📚
Ran crawler to generate amazon_csv table with inferred schema. 🕵️‍♂️


Troubleshot TABLE_NOT_FOUND by re-verifying S3 data and re-running the crawler. 🛠️


Outcome: Metadata cataloged, enabling queryability. ✅
![Crawler](images/Crawler.png)

![DataCatalog Database and Table View](images/Table.png)



4. 🔧 ETL (Extract, Transform, Load)

Actions:
Created Glue job amazon-etl-job with:
IAM role: glue-etl-role. 🔧
Type: Spark (PySpark). ⚡
Workers: 2 DPUs. 💻
Output path: s3://analysis-data-lake-bucket-20250825/refined/amazon-parquet/. 📦


Wrote and executed PySpark script:import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

datasource = glueContext.create_dynamic_frame.from_catalog(database="amazon_db", table_name="amazon_csv")
transformed = datasource.toDF().na.drop(subset=["rating"]).withColumn("discount_percentage", col("discount_percentage").cast("float"))
aggregated = transformed.groupBy("category").agg({"rating": "avg"}).withColumnRenamed("avg(rating)", "avg_rating")
aggregated.write.mode("overwrite").partitionBy("category").parquet("s3://analysis-data-lake-bucket-20250825/refined/amazon-parquet/")

job.commit()


Ran the job and created a new crawler for refined/amazon-parquet/ to generate amazon_refined. 🔄


Outcome: Transformed data optimized as Parquet with aggregated insights. ✅

![ETL-JOB](images/etl-job.png)


5. 📊 Querying Data (Ad-Hoc Analysis)

Actions:
Created Athena workgroup amazon-workgroup via AWS CLI:aws athena create-work-group --name amazon-workgroup --configuration '{"ResultConfiguration": {"OutputLocation": "s3://analysis-data-lake-bucket-20250825/athena-results/"}, "ExecutionRole": "arn:aws:iam::747757438809:role/glue-etl-role", "EnforceWorkGroupConfiguration": true, "PublishCloudWatchMetricsEnabled": false}'


Set query result location to s3://analysis-data-lake-bucket-20250825/athena-results/. 📍
Ran queries:
Raw: SELECT category, rating FROM amazon_csv WHERE rating > 4 ORDER BY rating DESC LIMIT 10;
Refined: SELECT category, avg_rating FROM amazon_refined ORDER BY avg_rating DESC;


Resolved TABLE_NOT_FOUND by re-running the crawler. 🕒


Outcome: Successfully queried raw and refined data. ✅
![Athena Query](images/AthenaQuery.png)


6. 🔒 Security and Governance (Access Control)

Actions:
Set up Lake Formation:
Granted admin permissions to admin-analysis-team. 👤
Registered s3://analysis-data-lake-bucket-20250825/ with glue-etl-role. 🌐
Enabled Lake Formation Mode. ⚙️


Applied permissions:
glue-etl-role: Describe, Alter on amazon_db, Select, Describe on amazon_csv (columns category, rating), and Data access on S3. 🔐
Revoked default IAMAllowedPrincipals permissions. 🚫




Outcome: Data lake secured with fine-grained access. ✅
![LakeFormation](images/LakeFormation.png)
![AdminUser](images/AnalysisTeamUser.png)
![Adminstrative Roles and Tasks](images/AdminRolesAndTask.png)
![Colum-Based-Access](images/Column-Based-Access.png)
![Trust-Relationship-Glue-Role](images/Trust-Relationship-Glue-Role.png)


7. 👀 Visualization and Insights (Reporting)

Actions:
Set up Amazon QuickSight:
Signed up for a free trial. 📊
Granted access to S3 and Athena. 🔑


Created dataset and dashboard:
Source: amazon_db.amazon_refined.
Visual: Bar chart of category vs. avg_rating for top-rated products. 📈
Published and shared the dashboard. 🌐




Outcome: Visual insights generated (e.g., top-rated categories). ✅
![QuickSight DashBoard - 1](images/QuickSight-1.png)
![QuickSight DashBoard - 2 ](images/QuickSight-2.png)

8. 🔍 Testing, Monitoring, and Optimization

Actions:
Tested: Deleted a file in raw/, restored via versioning, and re-ran crawler/ETL/query. ✅
Monitored: Set up CloudWatch metrics for Glue job duration and Athena data scanned. 📡
Optimized: Used Parquet partitioning to reduce query costs. 💡
Cleaned Up: Emptied/deleted S3 bucket, stopped Glue jobs, and deleted QuickSight resources. 🧹


Outcome: Reliable, optimized, and cost-effective pipeline. ✅
![CloudWatch Monitoring](images/CloudWatch.png)


🌈 Architecture Diagram
[External Data Source] --> [Amazon S3] --> [AWS Glue] --> [AWS Glue Jobs] --> [Amazon Athena] --> [AWS Lake Formation & CloudWatch]
    |                        |                |                    |                     |                        |
    +---- Raw Data --------->|------ Catalog -->|----- Transform ---->|------- Query ------->|----- Secure & Monitor -+
                             (amazon_db, amazon_csv)          (amazon_refined)           (category, rating)       (Permissions, Logs)


S3: Stores analysis-data-lake-bucket-20250825 with raw/, refined/, and athena-results/.
Glue: Manages amazon_db, amazon_csv, and amazon_refined via amazon-crawler and amazon-etl-job.
Athena: Queries with amazon-workgroup.
Lake Formation: Secures with admin-analysis-team and glue-etl-role.
CloudWatch: Monitors logs and metrics.


🎯 Project Outcomes

📈 Built a fully functional data lake pipeline from scratch.
🔒 Implemented robust security with Lake Formation.
📊 Enabled querying and visualization of key metrics.
🚀 Optimized for scalability and cost efficiency.




