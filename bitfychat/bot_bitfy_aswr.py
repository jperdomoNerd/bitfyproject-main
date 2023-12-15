# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 13:19:55 2023

@author: JUAN DAVID
"""


import openai
import json
import pandas as pd
import pdb
import os
import logging
from conection_big_query import BigQueryHandler
from datetime import datetime, timedelta
import websockets

logging.basicConfig( level=logging.DEBUG, filename='logs/log-chatbot-{:%Y-%m-%d}.log'.format(datetime.now()), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
 
# returns current date and time



def generate_prompt(context):
    '''
    this function receives as parameter a context and a question 
    and returns the prompt to send to gpt-3
    Parameters
    ----------
    context : TYPE str
        DESCRIPTION. paragraph with information on the bot's intent
    question : TYPE str
        DESCRIPTION. question to answer

    Returns
    -------
    prompt : TYPE str
        DESCRIPTION. prompt to send to gpt-3
    '''  
    
    initial_text_prompt = 'Eres un asistente llamado BITFYBOT entrenado para las \
        necesidades de DerechoalDerecho. responde los mas correctamente si no sabes exige contactar a los asesores. Knowledge\
        cutoff:{'+context+'}'

    
    return initial_text_prompt

def check_conversation_id(id_num):
    query = f'''SELECT id_conversacion, status FROM `bittfy-gcp-server.bifylegal.conversaciones`
    where  id_user= '{id_num}' order by date DESC LIMIT 1;'''
    create_query = BigQueryHandler().execute_query(query)
    if len(create_query) > 0:
        if create_query['status'][0] == '1':
            
            id_conv = int(create_query['id_conversacion'][0])
        else:
            id_conv = int(create_query['id_conversacion'][0])
            id_conv += 1
    else:
        id_conv = 1
        
    return id_conv
        

async def saving_data(id_num, question,role):
    
    date = datetime.now() - timedelta(hours=5) # zonetime server
    conversation_id = check_conversation_id(id_num)
    query = f"""
    INSERT INTO bittfy-gcp-server.bifylegal.conversaciones
    VALUES ('{id_num}', '{question}','{role}',1,{conversation_id},'1','{date}','1');
    """
    # Step 6 - Execute the query
    print("query saving data: "+ query)
    logging.info("query saving data: "+ query)
    create_query = BigQueryHandler().execute_query(query)    
    
    data_send_ws = {'id_user': id_num, 'content':question, 'role':role, 'date': date.strftime("%Y-%m-%dT%H:%M:%S.%f")}
    data_send_ws_json = json.dumps(data_send_ws)
    async with websockets.connect(f'ws://localhost:8082/ws/{id_num}') as websocket:
        await websocket.send(data_send_ws_json)
    return conversation_id


def desactivate_conversation(id_num,type_h="30m"):
    
    if type_h == '30m':
        query = f"""
        UPDATE `bittfy-gcp-server.bifylegal.conversaciones` SET status = '0' 
        WHERE status= '1' and id_user = '{id_num}'
        """
    if type_h == '12':
        query = f"""
        UPDATE `bittfy-gcp-server.bifylegal.conversaciones` SET register = '0',status = '0' 
        WHERE register= '1' and id_user = '{id_num}'
        """
        
    # Step 6 - Execute the query
    print("query desactivate conversation: "+ query)
    logging.info("query desactivate conversation: "+ query)
    create_query = BigQueryHandler().execute_query(query)

    
def load_data(id_num):
    

    query = f"""
    SELECT content, role, date FROM `bittfy-gcp-server.bifylegal.conversaciones` 
    where status ="1" and id_user= '{id_num}' order by date ASC;
    """
    # Step 6 - Execute the query
    df = BigQueryHandler().execute_query(query)
    df = df.to_dict('records')
    df = sorted(df, key=lambda x: x['date'])
    for d in df:
        d.pop('date', None)
    return df

class generate_bot_aswr:
    
    def __init__(self, context, question ,id_num,df ,verbose = 0):
        self.context = context
        self.question = question
        self.id_num = id_num
        self.df = df
        
        if verbose == 1:
            print("generate bot answer")
            
    async def bot_aswr(self,nodered = 0, state = '1'):   
        logging.info("valores"+ str(nodered)+ " "+state)
        print("valores"+ str(nodered)+ " "+state)
        if state == '0':
            await saving_data(self.id_num, self.question,"user")
            output = "bot is off, if you want activate it, please update the state"
        else:
            general_prompt = generate_prompt(self.context)
            
            if nodered == 0: # si el mensaje no llega por nodered
                id_conv = await saving_data(self.id_num, self.question,"user")
            else:
                id_conv = 2
            messages = load_data(self.id_num)
            system_message = {"role": "system", "content": general_prompt}
            messages.insert(0, system_message)        
           
            while len(messages) >= 11:        
                messages.pop(5)    
    
            if len(messages) == 2 and id_conv == 1 and nodered == 0:
                output = self.df['Contexto'][2]
            else:
                
                logging.info("chatGPT " + messages[len(messages)-1]['content'])
                openai.api_key = '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'
                try:
                    response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    temperature = 0.0,
                    messages=messages
                    )
                except Exception as e:
                    logging.info("chatGPT error:  " + str(e))
                    
                output = response["choices"][0]["message"]["content"]
                
            output_bq = output.replace("\n", " ")
            logging.info("respondio " + output_bq)
            await saving_data(self.id_num, output_bq,"assistant")
        return output
    
    async def bot_aswr_node_red(self, type_h = "30m"):
        
        
        #id_conv = saving_data(self.id_num, self.question,"user")
        output = self.context
        output_bq = output.replace("\n", " ")
        await saving_data(self.id_num, output_bq,"assistant")
        desactivate_conversation(self.id_num, type_h)   
        return output
    
    def load_last_message(self):
        

        query="""
SELECT t1.id_user, t1.content, t1.date, t1.role, t3.nombre
FROM `bittfy-gcp-server.bifylegal.conversaciones` t1
LEFT JOIN `bittfy-gcp-server.bifylegal.correos_email` t3
ON t1.id_user = t3.id_user
WHERE t1.date = (SELECT MAX(date)
                      FROM `bittfy-gcp-server.bifylegal.conversaciones` t2
                      WHERE t1.id_user = t2.id_user)
ORDER BY t1.date DESC;
"""
        df = BigQueryHandler().execute_query(query)
        df['nombre'] = df['nombre'].astype(str).fillna('null')
        df.replace('None', 'null', inplace=True)
        df = df.to_dict('records')
        return df
    
    def load_conversation_by_id(self,id_user):
        
        query = f"""SELECT id_user, content, date, role FROM `bittfy-gcp-server.bifylegal.conversaciones` WHERE id_user = '{id_user}' ORDER BY date ASC;"""
        df = BigQueryHandler().execute_query(query)
        df = df.to_dict('records')
        return df

        
        
    
    

#context ="hola javier, como estas"   
#question = 'gracias'
#aswr = generate_bot_aswr(context, question,'573214818764').bot_aswr()


    
    
    