# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 12:38:40 2023

@author: JUAN DAVID
"""
# This is an example to get data from BigQuery and return it as a pandas dataframe
# Step 1 - Import the required libraries
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account   
#from aws_handler import get_secret
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas_gbq
# Some constants (you can move them to a config file - ENV variables)



# Step 2  - Create a class to handle the BigQuery connection
class BigQueryHandler:
    
    def __init__(self):
        
        # Step 3 - Get credentials from the service account stored in AWS Secrets 
        credential_file = "credentials_bq.json"
        CREDENTIALS = Credentials.from_service_account_file(credential_file)

        # Now we can connect to BigQuery and create a client
        self.client = bigquery.Client(credentials=CREDENTIALS, project="bittfy-gcp-server")

        # Set the query job in dry_run mode to get the number of rows (Cost of the query before running it)
        self.dry_run_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)


    def execute_query(self, query) -> pd.DataFrame:
        """
        Function: execute query

        Description: This function executes a query and returns the results as a pandas dataframe

        Parameters:
            query: The query to be executed as a string
        
        Returns:
            df: The results of the query as a pandas dataframe
        """

        query_job = self.client.query(query, job_config=self.dry_run_config)
        print(f"Query cost: {query_job.total_bytes_processed / 1000000} MB")

        # Here you can add some logic to check if the query is too expensive and stop it
        
        # Now we can run the query for real
        query_job = self.client.query(query)
        results = query_job.result()

        # Convert the results to a pandas dataframe
        df = results.to_dataframe()

        return df
    
    def save_dataframe(self, df, project_id, table_id, if_exist_var = "replace"):
        credential_file = "credentials_bq.json"
        CREDENTIALS = Credentials.from_service_account_file(credential_file)
        
        pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists=if_exist_var, credentials=CREDENTIALS)
        
        
        




"""
query = f'''SELECT id_conversacion FROM `loklbot-contextos.lokl1.registros`
where  id_user= '+573214808764' order by date DESC LIMIT 1;'''
create_query = BigQueryHandler().execute_query(query)
if len(create_query) > 0:
    id_conv = int(create_query['id_conversacion'][0])
    id_conv += 1
else:
    id_conv = 1
"""
    


