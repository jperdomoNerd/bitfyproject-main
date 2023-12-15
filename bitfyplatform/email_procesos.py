# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 12:29:30 2023

@author: JUAN DAVID
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import base64
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import os
from email import encoders
from email.mime.base import MIMEBase
from query_db import crud
from datetime import datetime, timedelta
import pdb
from email.message import EmailMessage
import ssl
import smtplib
'''# La ruta al archivo de secretos del cliente que descargaste de la consola de Google Cloud
client_secrets_file = 'token (2).json'

# Inicia el flujo de autenticación
flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, ['https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.modify','https://www.googleapis.com/auth/gmail.readonly'])

# Esto abrirá una ventana de navegador para que el usuario conceda permisos
creds = flow.run_local_server(port=0)

# Guarda las credenciales en un archivo
with open('tokes.json', 'w') as token:
    token.write(creds.to_json())'''
    
class gmail:
    
    def __init__(self, correo, asunto,mensaje,array_adjuntos):
        self.correo = correo
        self.asunto = asunto
        self.mensaje = mensaje
        self.array_adjuntos = array_adjuntos
        
        
    def send_email(self):    
        
        
        email_emisor = 'bittfy801@gmail.com'
        email_contrasena = 'ebpsbptwvrbyjspn'    
        email_receptor = self.correo #email_list
        cuerpo = self.mensaje
        
        
        em = EmailMessage()
        em['From'] = email_emisor
        em['To'] = [email_receptor,'notificaciones@derechoalderecho.co']
        em['Subject'] = self.asunto
        em.set_content(cuerpo)
        

        for file in self.array_adjuntos:
            with open(file, 'rb') as f:
                file_data = f.read()
                file_name = f.name.split('_')[1]
            em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)    
        
        contexto = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = contexto) as smtp:
            smtp.login(email_emisor, email_contrasena)
            smtp.sendmail(email_emisor, email_receptor, em.as_string())
        
        
    def read_email(self):        
        
        
        creds = Credentials.from_authorized_user_file('tokes.json') #local
        #creds = Credentials.from_authorized_user_file('/home/ubuntu/project/bitfyproject/bitfyplatform/tokes.json') #server
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("refresh ok")        
        
        # Si no hay credenciales válidas disponibles, haga que el usuario inicie sesión.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise ValueError('No valid credentials provided.')
        
        service = build('gmail', 'v1', credentials=creds)
        
        fecha = datetime.now().strftime('%Y/%m/%d')
        
        # Filtrar los mensajes por fecha
        query = f'after:{fecha}'

        # Solicita una lista de todos los mensajes
        result = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query).execute()
        messages = result.get('messages', [])
        data = []
        # Para cada mensaje
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            try:
                payload = txt['payload']
                headers = payload['headers']
                subject = None
                text = None
        
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                        #print('Subject: ', subject)
                    if d['name'] == 'Date':
                        date = d['value']
                        #print('Subject: ', subject)
                    if d['name'] == 'From':
                        fromEmail = d['value']
                        #print('Subject: ', subject)
                        
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            #print('Message: ', text)
                data.append({'Subject': subject, 'Message': text, 'From': fromEmail, 'idmsg': msg['id'], 'threadId': msg['threadId'], 'date': datetime.fromtimestamp(int(txt['internalDate']) / 1000.0)})
       
            except Exception as error:
                print(f'An error occurred: {error}')
        df = pd.DataFrame(data)
        return df
    
  
def job_send_email():
    os.chdir('/home/ubuntu/project/bitfyproject/bitfyplatform/') # server
    
    df=crud('proceso_p','').read_procesos_aprobados()
    df_city = crud('ciudad_p','').read_all()
    df_city = pd.DataFrame(df_city)
    
    for i in range(0,len(df)):
        id_ciudad = df['id_ciudad'][i]
        proceso = df['id_proceso'][i]
        correo = df_city.loc[df_city['id_ciudad'] == id_ciudad, 'email'].values[0]    
        df_docs=crud('documentos_p',{'id_proceso':proceso}).read_documents_by_proceso_id()
        df_docs = pd.DataFrame(df_docs)
        list_docs = df_docs['ruta_doc'].tolist()
        cuerpo = """"Cordial saludo señor Juez:

A través del presente correo electrónico adjunto acción de tutela con sus respectivos anexos. Favor tener en cuenta el correo notificaciones@derechoalderecho.co para recibir más fácilmente toda comunicación de respuesta.

Atentamente:


La parte accionante.
notificaciones@derechoalderecho.co"""
        messages= gmail(correo, 'ACCIÓN DE TUTELA- PRESENTACIÓN',cuerpo,list_docs).send_email()
        status = 'enviada'
        df['status'][i] = status    
        current_datetime = datetime.now()
        df['last_update'][i] = current_datetime
        table_name = 'proceso_p'
        values = df.loc[i].to_dict()
        crud(table_name,values).update()
        gmail(values['email'], 'actulizacion','el status cambio a ' + values['status'],'').send_email()
        
def job_save_email():
    os.chdir('/home/ubuntu/project/bitfyproject/bitfyplatform/') # server
    creds = Credentials.from_authorized_user_file('tokes.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            today = datetime.today()
            print("Today date is: ", today)
            creds.refresh(Request())
            print("refresh ok")
        else:
            today = datetime.today()
            print("Today date is: ", today)
            raise ValueError('No valid credentials provided.')
            
    emails = gmail('', '','','').read_email();
    print (emails);
#job_save_email()
job_send_email()