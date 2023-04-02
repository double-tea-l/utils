from google.cloud import bigquery
import pandas as pd
import numpy as np

# Instantiating big query
client = bigquery.Client(project='company-gcp-us-ae-ops-prod')

def get_data_from_gbq(query: str, fetch_data=True):
    global query_job
    # Makes a request
    query_job = client.query(query)
    # Get the column names from the first row (each row contains the columns names)
    column_names = list(query_job.result())[0].keys()
    # Convert it to list of tupes
    data = [row.values() for row in query_job]
    # Create a DataFrame
    df_gbq = pd.DataFrame(data, columns=column_names)
    return df_gbq


def load_to_gbq(df, table_name):
    
    client = bigquery.Client(project = 'company-gcp-us-ae-ops-prod')
    # Define table name, in format dataset.table_name & load data to BQ

    # keep job config to replace existing tables when upload, otherwise appending
    job_config = bigquery.job.LoadJobConfig()
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

    job = client.load_table_from_dataframe(df, table_name, job_config = job_config)  
    
    print('The dataframe has been uploaded into GBQ table.')

    return job
