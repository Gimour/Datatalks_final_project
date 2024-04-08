# DataTalks.Club Data Engineering Zoomcamp
# Final Project 2024 Cohort

**Note:** This project was developed as the final step for the completion of the Data Engineering Zoomcamp offered by DataTalksClub.

---

## Premier League

Premier League Data (Season 2021-2022) consist of three data sources (players_data, match_reults, final_table)

The goal of this project is to design and implement a data engineering pipeline tailored for football analytics. This pipeline should efficiently handle both batch and streaming data processing, ensuring data quality. Additionally, it should support the creation of analytics-ready datasets and facilitate insights generation.

Key aspects to address include:

- **Data Processing:** Implement a batch processing pipeline to handle data efficiently and load in a Google BigQuery data lake.
- **Analytics Engineering:** Implement dimensional modelling using dbt to create fact and dimension tables that are optimized for analytics.
- **Real-time Data Streaming:** Build a streaming data pipeline with Google Pub/Sub to handle incoming data streams in real-time.
- **Orchestration:** Orchestrate the pipelines with Mage deployed to Google Cloud Run.
- **Visualization:** Use Grafana to visualize real-time data updates.

## Instructions
---
## 1. Set up Infrastructure using Terraform
Set up a Google Cloud Platform project and service account following the instructions [here](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/01-docker-terraform/1_terraform_gcp/2_gcp_overview.md#initial-setup).

## 2. Deploy Mage to GCP with Terraform
Following the instructions from [Mage docs](https://docs.mage.ai/production/deploying-to-cloud/gcp/setup). Make sure you have installed:
- terraform
- gcloud CLI

1. Clone [mage-ai-terraform-templates github repo](https://github.com/mage-ai/mage-ai-terraform-templates) and edit the /gcp/variables.tf file with your specific project details.

2. Change directory
<pre>
$ cd gcp
</pre>
3. Initialize Terraform
<pre>
$ terraform init
</pre>
4. Deploy
<pre>
$ terraform apply
</pre>
You will see a notification here if you have not enabled any Google Cloud API or resource. To do so, log in to your Cloud Console and use the search bar to find the resource you need to enable. Before retrying steps 3 and 4, make sure you:
<pre>
$ terraform destroy
</pre>
At this stage we can visit [Cloud Run](https://console.cloud.google.com/run?referrer=search&project=massive-oasis-412719) on Google Cloud to view our Mage app. For this project, we have allowed all users to access our service [here](https://mage-4liwb5tgzq-wl.a.run.app/overview), however we can whitelist only specific IPs.

## 3. Mage Pipelines
We can now create our **table_per_round** load pipeline in Mage UI, that will generate synthetic data related to orders an online ecommerce marketplace receives. We name the pipeline <code>table_per_round</code>. [The pipeline](https://github.com/Gimour/Datatalks_final_project/tree/main/mage_pipelines/table_per_round) consists of:
- Data Loaders
- Transformers
- Data Exporters

that essentially are python files that generate synthetic data, then perform some data quality checks and finally load some dataframes to BigQuery.

![](https://github.com/Gimour/Datatalks_final_project/blob/main/screenshots/pipeline.JPG)

We can now schedule this pipeline to run every day, simulating an end-to-end pipeline that loads raw data to our data lake.

## 4. Dimensional Modelling
At this stage of the project we are going to use dbt cloud to create fact and dimension tables based on the raw table we ingested to BigQuery with the batch load pipeline. More on dimensional modelling [here](https://docs.getdbt.com/terms/dimensional-modeling).
In dbt we initially create 2 models:
- [dim_match_data](https://github.com/Gimour/Datatalks_final_project/blob/main/dbt/models/premier_league/dim_match_data.sql) 
- [fct_table_per_round](https://github.com/Gimour/Datatalks_final_project/blob/main/dbt/models/premier_league/fct_table_per_round.sql)

forming a star-schema for our data-warehoue.

![](https://github.com/Gimour/Datatalks_final_project/blob/main/screenshots/dbt_lineage.JPG)

## 5. Real-time Data Streaming

For this part, we used Mage to create a [streamed data](https://github.com/Gimour/Datatalks_final_project/blob/main/mage_pipelines/table_per_round_stream/custom/final.py), based on a python script that creates dummy match streams every 1 second, simulating real-time match data. When triggered the data stream will run indefinitely up until all matches of the year are successfully streamed.

### Google Pub/sub
After setting up the script, we need a service to handle the streaming data and load them to our data lake. For this task, we used [Google Pub/Sub](https://cloud.google.com/pubsub?hl=en) to ingest the orders stream to BigQuery.

Pub/Sub acts as a message broker that reliably stores and delivers messages between publishers (senders) and subscribers (receivers) in real-time or near real-time. It ensures the delivery of messages even in the case of system failures or network disruptions.

The main components of this service are:
- **Topics:** Entities to which messages are published by publishers.
- **Subscriptions:** Subscriptions represent the relationship between a topic and a subscriber. Subscribers receive messages from subscriptions. There are two types of subscriptions: push subscriptions, where Pub/Sub pushes messages to a specified endpoint (e.g., a webhook), and pull subscriptions, where subscribers pull messages from Pub/Sub at their own pace.

We used [Google Cloud Console UI](https://console.cloud.google.com/cloudpubsub/topic/list?tutorial=pubsub_quickstart&_ga=2.120588686.-766652252.1711816423&hl=en&project=massive-oasis-412719) to create a topic in Pub/Sub named: <code>all_match_results</code> and then a subscription for our topic that sends the recieved messages to a BigQuery table:

![](https://github.com/Gimour/Datatalks_final_project/blob/main/screenshots/pubsub_subscription.JPG)

Then we can add the following code to our python producer script, to send the synthetic order streams to our <code>orders-topic</code>:

<pre>
from google.cloud import pubsub_v1
project_id = 'massive-oasis-412719'
topic_name = 'all_match_results'
# Create a publisher client
publisher = pubsub_v1.PublisherClient()
# Get the full topic path
topic_path = publisher.topic_path(project_id, topic_name)
# Publish the message to the topic
publisher.publish(topic_path, data=json.dumps(stream_message).encode('utf-8'))
</pre>

After running our script, we can go back to the BigQuery table we defined in the subcription, to check the order streams that are ingested in real time.

## 6. Visualization
For the visualization part of the project, we needed a tool capable of handling real-time data updates. For this task, we used [Grafana Cloud](https://grafana.com/products/cloud/) which offers a free trial.
[This](https://mouratosg.grafana.net/public-dashboards/e53b21ecfa7941b7bc1b8a717a28f4fe) is a sample dashboard we can build in grafana to monitor the match streams, after triggering our stream producer in Mage:

In the current dashboard we can also monitor some core football KPIs such as: 
- Champion
- Golden Boot Winner
- Best Attacking Team
- Best Defensive Team

among with the Final Table of the 2021-2022 Premier's League Ranking
