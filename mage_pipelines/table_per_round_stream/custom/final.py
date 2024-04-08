if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

import time
import json
import random
from google.cloud import pubsub_v1
from google.cloud import bigquery
from datetime import datetime, timedelta
import pandas as pd

project_id = 'massive-oasis-412719'
dataset_id = 'final_project'
table_id = 'fct_table_per_round'
topic_name = 'all_match_results'
# Create a publisher client
publisher = pubsub_v1.PublisherClient()
# Get the full topic path
topic_path = publisher.topic_path(project_id, topic_name)

@custom
def transform_custom(*args, **kwargs):
    # Connect to BigQuery
    bq_client = bigquery.Client()

    # Query data from BigQuery table
    query = f"""
        SELECT
            team,
            points
        FROM
            `{project_id}.{dataset_id}.{table_id}`
        ORDER BY date
    """
    df = bq_client.query(query).to_dataframe()

    # Generate dummy date with 1 second difference between each timestamp
    current_time = datetime.now()
    df['Date'] = [current_time + timedelta(seconds=i) for i in range(len(df))]

    # Convert all fields to string
    # df = df.astype(str)

    # Construct and publish messages to Pub/Sub
    for index, row in df.iterrows():
        stream_message = {
            'Date': row['Date'].strftime('%Y-%m-%d %H:%M:%S'),
            'team': row['team'],
            'points': row['points']
        }
        publisher.publish(topic_path, data=json.dumps(stream_message).encode('utf-8'))
        print(f"{stream_message}")
        time.sleep(1)  # Simulate streaming by waiting 1 second between messages
    return {}
