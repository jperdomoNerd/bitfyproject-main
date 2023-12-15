# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 12:59:52 2023

@author: JUAN DAVID
"""


import openai
from typing import Optional
from fastapi import FastAPI, Request, HTTPException,Form, Depends
from pydantic import BaseModel
from fastapi.security import HTTPBearer
import pandas as pd
from bot_bitfy_aswr import generate_bot_aswr
import urllib.parse
import requests
import json
from datetime import datetime
import logging
from fastapi.middleware.cors import CORSMiddleware
import pdb


logging.basicConfig( level=logging.DEBUG, filename='logs/log-chatbot-{:%Y-%m-%d}.log'.format(datetime.now()), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
token_auth_scheme = HTTPBearer()
app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    aspect_type: str
    event_time: int
    object_id: int
    object_type: str
    owner_id: int
    subscription_id: int
    updates: dict

def send_wa_message(number, text):
    
    
    url = "https://graph.facebook.com/v12.0/107851482292507/messages?access_token=EAALR505SaWYBAO5ZAMo2KqZAzu0fq3WKKYu91NBCzB2eTPsIJYUTfGPoULgzMAppyPJigmMZBFpCvI7hoUnXqWbqec0O6JfcCehSWMo0QAOg6d3VGLkZAVgUW5eulyYCoFyZC4bYx3wSqHbzovvNOkHV3iLXZC0sv8fzTZA0ZBu6Q2wL4gL6SMTM"  # Replace with your URL
    payload = {
        'messaging_product': 'whatsapp',
        'to': number,
        #"messaging_product": "whatsapp",
        'text': {
        'body': text
        }
    }
    headers = {'Content-Type': 'application/json'}  # Replace with your headers
    #payload = json.dumps(payload)
    print(payload)
    response = requests.post(url, headers=headers, json=payload)
    print(response.status_code)
    print(response.content)


@app.api_route("/webhook",methods=["GET", "POST"])
async def read_params(request: Request, event: Optional[Event] = None):
    
    
    bot_s = open("bot_state.txt", "r")
    state = bot_s.read()
    bot_s.close()
    

    if request.method == 'GET':
        sample = request.headers['texto']
        sample = urllib.parse.unquote(sample)
        print(sample)
        #print(request.headers['value'])
        print(request.headers)
        id_num = request.headers['phone']
        #id_num = 1
        #loading google sheet
        SHEET_ID = '1V-y1ZZ6Pz-_Y681mNOmhV8VaNvjsacfMiw9O-xly8_o'
        SHEET_NAME = 'contexto_bitfy'
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
        df = pd.read_csv(url)
        text = ""
        
        
        for i in range(2,len(df)):
            text = text + df['tipo'][i] + "\n"
            print(df['Contexto'][i])
            text = text + df['Contexto'][i]
        
        aswr = await generate_bot_aswr(text,sample,id_num,df).bot_aswr(0,state)
        
        if state == '1':
            #aswr = aswr + "\n Conoce más e invierte en:  https://home.lokl.life/"
            send_wa_message(id_num, aswr)        

    return {"aswr":aswr}


@app.api_route("/send_message",methods=["GET", "POST"])
async def read_nodered_message(request: Request, event: Optional[Event] = None):

    if request.method == 'GET':
        id_num = request.headers['phone']
        text = request.headers['texto']
   
        aswr = await generate_bot_aswr(text,"",id_num,"").bot_aswr_node_red()
        send_wa_message(id_num, aswr)

    return {"aswr":aswr}
    
    
@app.api_route("/last_message_user",methods=["GET", "POST"])
async def last_message_user(request: Request, event: Optional[Event] = None):
    
    aswr = generate_bot_aswr("","","","").load_last_message()
    return {"aswr":aswr}


@app.api_route("/load_conversation_by_id",methods=["GET", "POST"])
async def load_conv_by_id(id_num: str, request: Request, event: Optional[Event] = None):  
    
    aswr = generate_bot_aswr("","","","").load_conversation_by_id(id_num)
    return {"aswr":aswr}


@app.api_route("/save_state_bot",methods=["GET", "POST"])
async def save_state_bot( request: Request, event: Optional[Event] = None): 
    
    state = request.headers['state']
    bot_s = open("bot_state.txt", "w")
    bot_s.write(state)
    bot_s.close()
    return {"aswr":f"saved state: {state}"}

@app.api_route("/load_state_bot",methods=["GET", "POST"])
async def load_state_bot( request: Request, event: Optional[Event] = None): 
    
    
    bot_s = open("bot_state.txt", "r")
    state = bot_s.read()
    bot_s.close()
    return {"aswr":state}









        

#df = pd.read_excel('data_to_train.xlsx') 
#df.to_json("data_train.jsonl", orient='records', lines=True)

