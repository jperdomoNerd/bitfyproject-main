# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 13:46:52 2023

@author: JUAN DAVID

"""


import requests
import pandas as pd
from query_db import crud
from conection_big_query import BigQueryHandler
import os


def expandir_diccionario(row):
    billing_dict = row["billing"]
    row["first_name"] = billing_dict["first_name"]
    row["last_name"] = billing_dict["last_name"]
    row["email"] = billing_dict["email"]
    row["phone"] = billing_dict["phone"]    
    return row


def load_procesos():
    
    df = crud("proceso_p","").read_all()
    df = pd.DataFrame(df)
    return df

def load_users():
    
    df = crud("user_p","").read_all()
    df = pd.DataFrame(df)
    return df

def load_orders():
    
    
    username = "ck_5c8460c6e6779c116bbbe427caef0f6aa2de9515"
    password = "cs_67ff0f69f36e449123eead891f93b5c400290f06"
    url = 'https://derechoalderecho.co/wp-json/wc/v3/orders'
    response = requests.get(url, auth=(username, password))
    data = response.json()
    df = pd.DataFrame(data)
    df = df.apply(expandir_diccionario, axis=1)
    df = df.drop("billing", axis=1)
    df_expanded = pd.json_normalize(df["line_items"].explode())
    df_expanded = df_expanded.drop(df_expanded.columns[0], axis=1)
    df_expanded = df_expanded.drop(df_expanded.columns[7], axis=1)
    df = pd.concat([df.drop("line_items", axis=1), df_expanded], axis=1)

    columns = ['id','status','currency','date_created','total','first_name','last_name','email','phone','name','product_id','quantity','date_modified']
    df = df[columns]
    df['date_modified_datetime'] = pd.to_datetime(df['date_modified'])
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(days=2)
    df = df[(df['date_modified_datetime'] > start_date)]
    df = df.drop(columns=['date_modified_datetime'])
    try:
        df_orders_bq = crud("orders_p","").read_all()
        df_orders_bq = pd.DataFrame(df_orders_bq)
        
    except:
        df['assigned'] = False
        BigQueryHandler().save_dataframe(df, "bittfy-gcp-server", "bifylegal.orders_p")
        df_orders_bq = crud("orders_p","").read_all()
        df_orders_bq = pd.DataFrame(df_orders_bq)

    ids_orders_bq = df_orders_bq['id'].unique()
    missing_rows = df[~df['id'].isin(ids_orders_bq)].copy()  # .copy() para evitar SettingWithCopyWarning

    # Agregar la columna 'assigned' en False para estas filas
    missing_rows['assigned'] = False

    # Agregar las filas al df_orders_bq
    df_orders_bq = pd.concat([df_orders_bq, missing_rows], ignore_index=True)   
    df['assigned'] = False
    merged_df = df_orders_bq.merge(df, on='id', suffixes=('_bq', '_df'))

    # 2. Identificar donde los 'status' son diferentes
    mask = merged_df['status_bq'] != merged_df['status_df']

    # 3. Actualizar 'status' en df_orders_bq
    df_orders_bq.loc[df_orders_bq['id'].isin(merged_df[mask]['id']), 'status'] = merged_df[mask]['status_df'].values
    df_orders_bq.loc[df_orders_bq['id'].isin(merged_df[mask]['id']), 'status'] = merged_df[mask]['date_modified_df'].values

        
    #BigQueryHandler().save_dataframe(df_orders_bq, "bittfy-gcp-server", "bifylegal.orders_p")        
    #   
    
    return df_orders_bq

    

os.chdir('/home/ubuntu/project/bitfyproject/bitfyplatform/') # server
df_procesos = load_procesos()
df_procesos = df_procesos[df_procesos['status'] == 'creada']
df_usuarios = load_users()
df_orders_original = load_orders()
df_orders = df_orders_original[df_orders_original['assigned'] == False]


# colocar el pago como asignado
resultados = df_procesos.merge(df_usuarios[['id_user', 'email']], on='id_user', how='inner')
filtro_correos = df_orders['email'].isin(resultados['email'])
filtro_cancelled = df_orders['status'] == 'cancelled'
#df_orders.loc[filtro_correos & filtro_cancelled, 'assigned'] = True


# colocar el proceso como asignado
df_orders.sort_values(by='email', inplace=True)
resultados.sort_values(by='email', inplace=True)
merged = pd.merge(resultados, df_orders[filtro_correos & filtro_cancelled][['email', 'id']], on='email', how='left')
merged =  merged.dropna(subset=['id'])
if len(df_orders[filtro_correos & filtro_cancelled]):

    merged.drop_duplicates(subset=['id_proceso'], inplace=True)
    merged.drop_duplicates(subset=['id'], inplace=True)
    if 'pago' in merged.columns:
        merged['pago'].update(merged['id'])
    else:
        merged.rename(columns={'id': 'pago'}, inplace=True)
    merged.drop(columns=['id'], inplace=True)
    resultados = merged
    #df_orders = df_orders[df_orders['assigned'] == False]
    
    merged = pd.merge(df_procesos, resultados[['id_proceso', 'pago']], on='id_proceso', how='left', suffixes=('', '_from_resultados'))
    if 'pago' in merged.columns and 'pago_from_resultados' in merged.columns:
        mask = merged['pago_from_resultados'].notna()
        merged.loc[mask, 'status'] = 'pagada'
        
        merged['pago'].update(merged['pago_from_resultados'])
        merged.drop(columns=['pago_from_resultados'], inplace=True)
    elif 'pago_from_resultados' in merged.columns:
        merged.rename(columns={'pago_from_resultados': 'pago'}, inplace=True)
    df_procesos_2 = merged
    
    merged = df_procesos.merge(df_procesos_2, on='id_proceso', how='inner', suffixes=('_original', '_nuevo'))
    columns_to_compare = set(merged.columns) - {'id_proceso'}
    mask_diff = (merged.loc[:, [col for col in columns_to_compare if col.endswith("_original")]] !=
                 merged.loc[:, [col.replace('_original', '_nuevo') for col in columns_to_compare if col.endswith("_original")]].values).any(axis=1)
    diff_rows = merged.loc[mask_diff, ['id_proceso'] + [col for col in merged.columns if col.endswith('_nuevo')]]
    diff_rows = diff_rows.reset_index(drop=True)
    #diff_rows.columns = diff_rows.columns.str.replace('_nuevo$', '') 
    # Actualizar solo las filas que coinciden, sin cambiar las que ya estaban establecidas a True
    mask = df_orders_original['id'].isin(diff_rows['pago_nuevo']) & ~df_orders_original['assigned']
    df_orders_original.loc[mask, 'assigned'] = True

    for i in range(0,len(diff_rows)):
        values = {"id_proceso":diff_rows['id_proceso'][i],
                  "id_user":diff_rows['id_user_nuevo'][i],
                  "id_ciudad":diff_rows['id_ciudad_nuevo'][i],
                  "status":diff_rows['status_nuevo'][i],
                  "resumen":diff_rows['resumen_nuevo'][i],
                  "pago":diff_rows['pago_nuevo'][i],
                  "respuestas":diff_rows['respuestas_nuevo'][i],
                  "tipo_proceso":diff_rows['tipo_proceso_nuevo'][i],
                  "last_update":diff_rows['last_update_nuevo'][i],
                  "num_radicado":diff_rows['num_radicado_nuevo'][i],
                  "juzgado": diff_rows['juzgado_nuevo'][i]
                  }    
        crud('proceso_p', values).update()
    
BigQueryHandler().save_dataframe(df_orders_original, "bittfy-gcp-server", "bifylegal.orders_p")



