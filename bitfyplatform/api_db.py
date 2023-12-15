# -*- coding: utf-8 -*-
"""
Created on Sun May  7 14:03:52 2023

@author: JUAN DAVID
"""


from typing import Optional
from fastapi import FastAPI, Request, HTTPException,Form, Depends,UploadFile, File, status
from pydantic import BaseModel
from fastapi.security import HTTPBearer
from datetime import datetime
import logging
from query_db import crud
from email_procesos import gmail
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import uuid
import shutil
import pdb
from pathlib import Path
from fastapi.responses import FileResponse
from os import getcwd
from fastapi.responses import JSONResponse
#logging.basicConfig( level=logging.DEBUG, filename='logs/log-chatbot-{:%Y-%m-%d}.log'.format(datetime.now()), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
token_auth_scheme = HTTPBearer()
app = FastAPI(root_path="/platform")

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



class user_p(BaseModel):
    id_user: str
    name: str
    email: str
    cel: str
    cc_number:str
    cc_type:str
    password:str
    token:str
    rol:str
    
class user_login(BaseModel):
    email: str
    password:str
    
class ciudad_p(BaseModel):
    id_ciudad: str
    ciudad: str
    email: str
    
    

class documentos_p(BaseModel):
    id_doc: str
    ruta_doc: str
    id_proceso: str
    tipo_doc: str
    
class proceso_p(BaseModel):
    id_proceso: str
    id_user: str
    id_ciudad: str
    status: str
    last_update: str
    resumen: str
    pago: str
    respuestas: str
    tipo_proceso: str
    num_radicado: str
    juzgado: str
    
class proceso_update_p(BaseModel):
    id_proceso: str
    id_user: str
    id_ciudad: str
    status: str
    last_update: str
    resumen: str
    pago: str
    respuestas: str
    tipo_proceso: str
    num_radicado: str
    juzgado: str
    email: str
    changeStatus: bool
    
    

@app.api_route("/create_user_p",methods=["POST"])
async def create_user(request: Request, event: Optional[user_p] = None):    

    table_name = "user_p"
    
    if event is None:
        data = await request.json()
        event = user_p.parse_raw(data)    
    
    values = event.dict()   
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    values['id_user'] = uuid_str
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    values['token'] = uuid_str
    print(values)
    df=crud(table_name,values).create()
    return {"aswr":values}

@app.api_route("/login",methods=["POST"])
async def login(request: Request, event: Optional[user_login] = None):    

    table_name = "user_p"
    
    if event is None:
        data = await request.json()
        event = user_login.parse_raw(data)    
    
    values = event.dict()
    print(values)
    df=crud(table_name,values).login()
    if len(df) < 1:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={
          "message": "Access denied",
          "token": ""
        })
    if df[0]['password'] != values['password']:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={
          "message": "Access denied",
          "token": "",
          "peticiones": 0
        })
    else: 
        #logging.info("login exitoso: " + str(entrada.name))
        df[0]['password'] = '***'
        return {
          "message": "Access success",
          "token": df[0]['token'],
          "usuario": df[0]
        }
    return {"aswr":df}

@app.api_route("/create_ciudad_p",methods=["POST"])
async def create_ciudad(request: Request, event: Optional[ciudad_p] = None):    

    table_name = "ciudad_p"
    
    if event is None:
        data = await request.json()
        event = user_p.parse_raw(data)    
    
    values = event.dict()
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    values['id_ciudad'] = uuid_str    
    print(values)
    df=crud(table_name,values).create()
    return {"aswr":values}


@app.api_route("/crear_documentos_p",methods=["POST"])
async def create_documentos1( id_doc: str= Form(...),ruta_doc: str= Form(...),id_proceso:str=Form(...),tipo_doc:str=Form(...),    file: Optional[UploadFile] = File(None)):   
    
    file_extension = Path(file.filename).suffix.lower()
    table_name = "documentos_p"
 
    data= {"id_doc": id_doc,
           "ruta_doc": ruta_doc,
           "id_proceso": id_proceso,
           "tipo_doc": tipo_doc}
        
         

    values = data
    destination_directory = "documentos"
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    values['id_doc'] = uuid_str  
    
    custom_filename = f"{values['id_proceso']}_{values['tipo_doc']}{file_extension}"
    file_location = f"{destination_directory}/{custom_filename}"


     
    values['ruta_doc'] = file_location      
    
    with open(file_location, "wb") as output_file:
        shutil.copyfileobj(file.file, output_file)
    
    
    
    
    df=crud(table_name,values).create()
    return {"aswr":values}

@app.api_route("/update_p",methods=["POST"])
async def update_documentos( id_doc: str= Form(...),ruta_doc: str= Form(...),id_proceso:str=Form(...),tipo_doc:str=Form(...),    file: Optional[UploadFile] = File(None)):   
    file_extension = Path(file.filename).suffix.lower()
    table_name = "documentos_p"
 
    data= {"id_doc": id_doc,
           "ruta_doc": ruta_doc,
           "id_proceso": id_proceso,
           "tipo_doc": tipo_doc}
    
    values = data
    destination_directory = "documentos"
    
    custom_filename = f"{values['id_proceso']}_{values['tipo_doc']}{file_extension}"
    file_location = f"{destination_directory}/{custom_filename}"

    values['ruta_doc'] = file_location
    with open(file_location, "wb") as output_file:
        shutil.copyfileobj(file.file, output_file)
    crud(table_name,values).update()
    return {"aswr":values}

@app.api_route("/crear_proceso_p",methods=["POST"])
async def create_documentos2(request: Request, event: Optional[proceso_p] = None):    

    table_name = "proceso_p"
    
    if event is None:
        data = await request.json()
        event = user_p.parse_raw(data)    
    
    values = event.dict()    
    generated_uuid = uuid.uuid4()
    uuid_str = str(generated_uuid)
    values['id_proceso'] = uuid_str
    current_datetime = datetime.now()
    values['last_update'] = current_datetime
    print(values)
    df=crud(table_name,values).create()
    return {"aswr":values}


@app.api_route("/read_proceso_p_by_id",methods=["GET"])
async def create_documentos3(request: Request, id_):    

    table_name = "proceso_p"
    values = {'id_proceso':id_}
    df=crud(table_name,values).read_by_id
    return df

@app.api_route("/read_user_p_by_id",methods=["GET"])
async def create_documentos4(request: Request, id_):    

    table_name = "user_p"
    values = {'id_user':str(id_)}
    df=crud(table_name,values).read_by_id()
    print(df)
    return df


@app.api_route("/read_documentos_p_by_id",methods=["GET"])
async def create_documentos5(request: Request, id_):    

    table_name = "dcoumentos_p"
    values = {'id_doc':id_}
    df=crud(table_name,values).read_by_id
    return df


@app.api_route("/read_ciudad_p_by_id",methods=["GET"])
async def create_documentos6(request: Request, id_):    

    table_name = "ciudad_p"
    values = {'id_ciudad':id_}
    df=crud(table_name,values).read_by_id
    return df


@app.post("/file")
async def upload_file(file: UploadFile = File(...)):
    
    destination_directory = "documentos"
    custom_filename = f"123_123_cedula"
    file_location = f"{destination_directory}/{custom_filename}.pdf"
    with open(file_location, "wb") as output_file:
        shutil.copyfileobj(file.file, output_file)
    return {"filename": file.filename}


@app.api_route("/read_all_procesos",methods=["GET"])
async def create_documentos7(request: Request):    

    table_name = "proceso_p"
    df=crud(table_name,"").read_procesos_usuario()
    return {"aswr":df}

    
@app.api_route("/read_documents_by_process_id",methods=["GET"])
async def create_documentos8(request: Request,id_):    

    table_name = "documentos_p"
    values = {'id_proceso':id_}
    df=crud(table_name,values). read_documents_by_proceso_id()
    return {"aswr":df}



@app.get("/download_file", response_class=FileResponse)
async def download(some_file_path):
    name = some_file_path.split('/')[1];
    return FileResponse (some_file_path, media_type ="application/octel-stream", filename = name)


@app.api_route("/update_status",methods=["POST"])
async def update_status(request: Request, event: Optional[proceso_update_p] = None):
    
    
    table_name = "proceso_p"
    if event is None:
        data = await request.json()
        event = user_p.parse_raw(data)    
    
    values = event.dict()
    current_datetime = datetime.now()
    values['last_update'] = current_datetime    
    df=crud(table_name,values).update()
    if (values['changeStatus']) :
        gmail(values['email'], 'actulizacion','el status cambio a ' + values['status'],'').send_email()
    return {"aswr":values}


@app.api_route("/read_all_ciudades",methods=["GET"])
async def read_ciudad(request: Request):    

    table_name = "ciudad_p"
    df=crud(table_name,"").read_all()
    return {"aswr":df}




