# -*- coding: utf-8 -*-
"""
Created on Sun May  7 15:14:54 2023

@author: SANTI
"""
import openai
#import json
#import pandas as pd
#import pdb
#import os
import logging
from docxtpl import DocxTemplate
from query_db import crud
#from conection_big_query import BigQueryHandler
#from datetime import datetime, timedelta
#import websockets

def generate_system_messages(context,cutoff):
    
    initial_text_prompt = context + ' cutoff:{'+cutoff+'}'
    
    return initial_text_prompt

def call_chatgpt(messages):

    openai.api_key = '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'
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature = 0.7,
        messages=messages
        )
    except Exception as e:
        logging.info("chatGPT error:  " + str(e))
        print("chatGPT error: ")
        return ''
        
    output = response["choices"][0]["message"]["content"]
    output_bq = output.replace("\n", " ")
    logging.info("respondio " + output_bq)
    return output

def generate_text(entrada,cutoff):
    
    cutoff = cutoff
    
    if entrada==1:    
        contexto = 'tu como abogado ayudame a redactar mejor el siguiente texto:'
    elif entrada == 2:
        contexto = 'tu como abogado Colombiano, dado estos hechos, dame una lista de derechos que se estan vulnerando en Colombia:'
    elif entrada == 3:
        contexto = 'tu como abogado Colombiano, estos derechos en que leyes se basan en Colombia, dame un lista de ellos'
    elif entrada == 4:
        contexto = 'resume el siguiente texto, en primera persona:'
    elif entrada == 5:
        contexto = 'dato estos textos construye unos hechos para una tutela y dividelos segun cosideres enb PRIMERO, SEGUNDO Y TERCERO:'
    elif entrada == 6:
        contexto = 'Hazme una lista de peticiones que puedo hacer dados estos hechos:'
    elif entrada == 7:
        contexto = 'de la situación contada a continuación hazme un resumen bien redactado serio y corto'
    general_prompt = generate_system_messages(contexto,cutoff)
    #print (general_prompt)
    system_message = {"role": "system", "content": general_prompt}
    messages = []
    messages.insert(0, system_message)  
    text = call_chatgpt(messages)
    return text

def generate_doc(Accionante, Accionado, Asunto,  Hechos, Derechos, Pretensiones, Fundamentos, Anexos,  TipoDoc, NumeroDoc, id_proceso):
    doc = DocxTemplate("Plantilla.docx")
    context = { 'Accionante' : Accionante, 'Accionado' : Accionado, 'Asunto': Asunto, 
               'Hechos':Hechos, 'Derechos':Derechos, 'Pretensiones':Pretensiones, 'Fundamentos':Fundamentos,  
               'Anexos':Anexos,  'TipoDoc':TipoDoc, 'NumeroDoc':NumeroDoc}
    doc.render(context)
    print(id_proceso)
    destination_directory = "documentos"
    custom_filename = f"{id_proceso}_tutela.docx"
    file_location = f"{destination_directory}/{custom_filename}"
    doc.save(file_location)
    
def create_tutela_salud_sin_apoderado(row):
    list_respuestas = row['respuestas'].split("<EOS>")
    Accionante = list_respuestas[1]
    Accionado = list_respuestas[7]
    NumeroDoc = list_respuestas[4]
    hechos_concat = list_respuestas[11]+"\n" + list_respuestas[11]+"\n" + list_respuestas[15]
    Hechos = generate_text(5,hechos_concat)
    Derechos = generate_text(2,Hechos)
    Pretensiones =generate_text(6,Hechos)
    Fundamentos =generate_text(3,Hechos)
    Asunto =generate_text(7,Hechos)
    df=crud('documentos_p',{"id_proceso":row['id_proceso']}).read_documents_by_user_id()
    Anexos = ""
    for i in range(0,len(df)):
        Anexos = Anexos + "\n" + df['tipo_doc'][i]
    TipoDoc = list_respuestas[3]
    print(row['id_proceso'])
    generate_doc(Accionante, Accionado, Asunto,  Hechos, Derechos, Pretensiones, Fundamentos, Anexos,  TipoDoc, NumeroDoc, row['id_proceso'])

    
    return df


#generate_doc(Accionante, Accionado, Asunto, Presentacion, Hechos, Derechos, Pretenciones, Fundamentos, Anexos, Notificacion, TipoDoc, NumeroDoc)

df=crud('proceso_p','').read_all_tutela()
lista = df.apply(create_tutela_salud_sin_apoderado, axis=1)[0]
