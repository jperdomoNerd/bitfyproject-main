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
import uuid
from docxtpl import DocxTemplate
from query_db import crud
import os
#from conection_big_query import BigQueryHandler
from datetime import datetime
from email_procesos import gmail
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
        print("chatGPT error: " + str(e))
        return ''
        
    output = response["choices"][0]["message"]["content"]
    output_bq = output.replace("\n", " ")
    logging.info("respondio " + output_bq)
    return output

def generate_text(entrada,cutoff):
    
    nombre_archivo = 'contextoTutSalud.txt'
    contexto_derecho_file = 'contextoDerechos.txt'
    contexto_fundamentos_file = 'contextoFundamentos.txt'

    try:
        with open(nombre_archivo, 'r') as archivo:
            contexto = archivo.read()
            #print(cntexto)
    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no fue encontrado.")
        
    try:
        with open(contexto_derecho_file, 'r') as archivo:
            contexto_derecho = archivo.read()
            #print(cntexto)
    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no fue encontrado.")
        
    try:
        with open(contexto_fundamentos_file, 'r') as archivo:
            contexto_fundamentos = archivo.read()
            #print(cntexto)
    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no fue encontrado.")
    
    if entrada==1:    
        contexto = 'tu como abogado ayudame a redactar mejor el siguiente texto:'
    elif entrada == 2: #derechos
        contexto = contexto_derecho +"\n"+ 'tu como abogado Colombiano, dado esta lista de derechos y la siguiente lista de hechos dime que derechos se vulneraron, responde solo la lista de derechos, sin resumen al final. '
    elif entrada == 3: #fundamentos
        contexto = contexto_fundamentos + 'tu como abogado Colombiano, dime cual de las anteriosres sentencias aplican para los hechos nombrados a continuación'
    elif entrada == 4:
        contexto = 'resume el siguiente texto, en primera persona:'
    elif entrada == 5:
        contexto = 'dado estos textos construye unos hechos para una tutela y dividelos segun cosideres enb PRIMERO, SEGUNDO Y TERCERO:'
    elif entrada == 6: #pretensiones
        contexto =' Haz una lista numerada de maximo 4 peticiones que le puedo hacer a un juez dados estos hechos'
    elif entrada == 7:
        contexto = 'de la situación contada a continuación hazme un resumen bien redactado serio y corto, de maximo 130 caracteres'
    general_prompt = generate_system_messages(contexto,cutoff)
    system_message = {"role": "system", "content": general_prompt}
    messages = []
    messages.insert(0, system_message)  
    text = call_chatgpt(messages)
    
    
    if entrada == 2: #derechos
        messages.append({"role": "assistant", "content": text})
        contexto = "agrega a cada derecho el por que se esta vulnearando para este caso"
        messages.append({"role": "user", "content": contexto})
        text = call_chatgpt(messages)
    elif entrada ==3:
        messages.append({"role": "assistant", "content": text})
        contexto = "deja solmanete la lista de las sentencias que aplican"
        messages.append({"role": "user", "content": contexto})
        text = call_chatgpt(messages)
    elif entrada == 6:
        messages.append({"role": "assistant", "content": text})
        contexto = "deja el mismo texto pero hablando en primera persona"
        messages.append({"role": "user", "content": contexto})
        text = call_chatgpt(messages)
       
    return text

def generate_doc(Accionante, Accionado, Asunto,  Hechos, Derechos, Pretensiones, Fundamentos, Anexos,  TipoDoc, NumeroDoc, id_proceso, tutela, tipoProceso, conciente, NumeroDocRepresentante, Representante):
    if (tipoProceso == 'tutela-salud'):
        if (conciente == 'si'):
            doc = DocxTemplate("Plantilla_tutela_salud_sin.docx")
            context = { 'Accionante' : Accionante, 'Accionado' : Accionado, 'Asunto': Asunto, 
                       'Hechos':Hechos, 'Derechos':Derechos, 'Pretensiones':Pretensiones, 'Fundamentos':Fundamentos,  
                       'Anexos':Anexos,  'TipoDoc':TipoDoc, 'NumeroDoc':NumeroDoc}
        else: 
            doc = DocxTemplate("Plantilla_tutela_salud_con.docx")
            context = { 'Accionante' : Accionante, 'Accionado' : Accionado, 'Asunto': Asunto, 
                       'Hechos':Hechos, 'Derechos':Derechos, 'Pretensiones':Pretensiones, 'Fundamentos':Fundamentos,  
                       'Anexos':Anexos,  'TipoDoc':TipoDoc, 'NumeroDoc':NumeroDoc, 'NumeroDocRepresentante': NumeroDocRepresentante, 'Representante': Representante}
    doc.render(context)
    
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    id_doc = uuid_str
    
    tipo_doc = "tutela";
    destination_directory = "documentos"
    custom_filename = f"{id_proceso}_tutela.docx"
    file_location = f"{destination_directory}/{custom_filename}"
    table_name = "documentos_p"
    
      
    data= {"id_doc": id_doc,
           "ruta_doc": file_location,
           "id_proceso": id_proceso,
           "tipo_doc": tipo_doc}
    
    doc.save(file_location)
    
    if not tutela:
        crud(table_name,data).create()
    
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
    df=crud('documentos_p',{"id_proceso":row['id_proceso']}).read_documents_by_proceso_id()
    Anexos = ""
    aux = 1;
    tutela = False;
    for i in range(0,len(df)):
        if (df[i]['tipo_doc'] != 'tutela'):
            Anexos = Anexos + "\n" + str(aux) + '. ' + df[i]['tipo_doc'].capitalize()
            aux = aux + 1
        else:
            tutela = True
            
    TipoDoc = list_respuestas[3]
    conciente = list_respuestas[0]
    tipoProceso = row['tipo_proceso']
    generate_doc(Accionante, Accionado, Asunto,  Hechos, Derechos, Pretensiones, Fundamentos, Anexos,  TipoDoc, NumeroDoc, row['id_proceso'], tutela, tipoProceso, conciente, '', '')
    status = 'generada'
    row['status'] = status    
    current_datetime = datetime.now()
    row['last_update'] = current_datetime
    table_name = 'proceso_p'
    values = row.to_dict()
    crud(table_name,values).update()
    gmail(values['email'], 'actulizacion','el status cambio a ' + values['status'],'').send_email()
    
    return df

def create_tutela_salud_con_apoderado(row):
    list_respuestas = row['respuestas'].split("<EOS>")
    Accionante = list_respuestas[1]
    Accionado = list_respuestas[7]
    NumeroDoc = list_respuestas[4]
    NumeroDocRepresentante = list_respuestas[6]
    Representante = list_respuestas[2]
    hechos_concat = list_respuestas[11]+"\n" + list_respuestas[11]+"\n" + list_respuestas[15]
    Hechos = generate_text(5,hechos_concat)
    Derechos = generate_text(2,Hechos)
    Pretensiones =generate_text(6,Hechos)
    Fundamentos =generate_text(3,Hechos)
    Asunto =generate_text(7,Hechos)
    df=crud('documentos_p',{"id_proceso":row['id_proceso']}).read_documents_by_proceso_id()
    Anexos = ""
    aux = 1;
    tutela = False;
    for i in range(0,len(df)):
        if (df[i]['tipo_doc'] != 'tutela'):
            Anexos = Anexos + "\n" + str(aux) + '. ' + df[i]['tipo_doc'].capitalize()
            aux = aux + 1
        else:
            tutela = True
            
    TipoDoc = list_respuestas[3]
    conciente = list_respuestas[0]
    tipoProceso = row['tipo_proceso']
    generate_doc(Accionante, Accionado, Asunto,  Hechos, Derechos, Pretensiones, Fundamentos, Anexos,  TipoDoc, NumeroDoc, row['id_proceso'], tutela, tipoProceso, conciente, NumeroDocRepresentante, Representante)
    status = 'generada'
    row['status'] = status    
    current_datetime = datetime.now()
    row['last_update'] = current_datetime
    table_name = 'proceso_p'
    values = row.to_dict()
    crud(table_name,values).update()
    gmail(values['email'], 'actulizacion','el status cambio a ' + values['status'],'').send_email()
    
    return df
    

def create_tutela(row):
    conciente = row['respuestas'].split("<EOS>")[0]
    tipoProceso = row['tipo_proceso']
    if (tipoProceso == 'tutela-salud'):
        if (conciente == 'si'):
            df = create_tutela_salud_sin_apoderado(row)
        else: 
            df = create_tutela_salud_con_apoderado(row)
    return df


#generate_doc(Accionante, Accionado, Asunto, Presentacion, Hechos, Derechos, Pretenciones, Fundamentos, Anexos, Notificacion, TipoDoc, NumeroDoc)

os.chdir('/home/ubuntu/project/bitfyproject/bitfyplatform/') # server
df=crud('proceso_p','').read_procesos_pagados()
if len(df) > 0:
    lista = df.apply(create_tutela, axis=1)[0]
