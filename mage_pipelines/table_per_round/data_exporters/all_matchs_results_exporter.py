from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from pandas import DataFrame
import os
import json
from google.oauth2 import service_account


if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_big_query(df: DataFrame, **kwargs) -> None:
    
    project_id = 'massive-oasis-412719'
    dataset_id = 'final_project'
    client = bigquery.Client(project=project_id)

    # Construct a full Dataset object to send to the API
    dataset = bigquery.Dataset(f"{client.project}.{dataset_id}")
    dataset = client.create_dataset(dataset, exists_ok=True)


    schema = [
    bigquery.SchemaField('Date', 'STRING'),
    bigquery.SchemaField('HomeTeam', 'STRING'),
    bigquery.SchemaField('HomeTeam_goals', 'STRING'),
    bigquery.SchemaField('AwayTeam_goals', 'STRING'),
    bigquery.SchemaField('AwayTeam', 'STRING')
    ]

    table_name = 'all_match_results'
    table_ref = client.dataset(dataset_id).table(table_name)
    table = bigquery.Table(table_ref, schema=schema)

    # If the table exists, delete it
    try:
        table = client.get_table(table_ref)
        print("Table {} already exists.".format(dataset_id + '.' + table_name))
        client.delete_table(table_ref)
        print("Table {} deleted.".format(dataset_id + '.' + table_name))
    except Exception as e:
        if isinstance(e, NotFound):
            print("Table {} does not exist. Creating now ...".format(dataset_id + '.' + table_name))
        else:
            print(f"An error occurred: {e}")

    # Create the table
    table = client.create_table(table)

    # Load the DataFrame into the BigQuery table
    job = client.load_table_from_dataframe(
        df, table_ref, job_config=bigquery.LoadJobConfig()
    )
    job.result()  # Wait for the job to complete
    print("Table {} created".format(dataset_id + '.' + table_name))