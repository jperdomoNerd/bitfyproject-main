# -*- coding: utf-8 -*-
"""
Created on Sun May  7 10:35:58 2023

@author: JUAN DAVID
"""
from conection_big_query import BigQueryHandler



class crud:
    
    def __init__(self, table_name, values):
        self.table_name = table_name
        self.values = values
    
    def create(self):
        
        
        if self.table_name == 'user_p':
            query = f"""
            INSERT INTO `bittfy-gcp-server.bifylegal.{self.table_name}` 
            (id_user,name,email,cel,cc_number,cc_type) VALUES('{self.values['id_user']}','{self.values['name']}','{self.values['email']}','{self.values['cel']}', '{self.values['cc_number']}', '{self.values['cc_type']}');
            """
        
        elif self.table_name == 'ciudad_p':
            query = f"""INSERT INTO `bittfy-gcp-server`.bifylegal.ciudad_p
                        (id_ciudad, ciudad, email)
                        VALUES('{self.values['id_ciudad']}', '{self.values['ciudad']}', '{self.values['email']}');
                    """
                    
        elif self.table_name == 'documentos_p':
            query = f"""INSERT INTO `bittfy-gcp-server`.bifylegal.documentos_p
                        (id_doc, ruta_doc, id_proceso, tipo_doc)
                        VALUES('{self.values['id_doc']}', '{self.values['ruta_doc']}', '{self.values['id_proceso']}', '{self.values['tipo_doc']}');
                    """

        elif self.table_name == 'proceso_p':
            query = f"""INSERT INTO `bittfy-gcp-server`.bifylegal.proceso_p
(id_proceso, id_user, id_ciudad, status, last_update, resumen, pago,respuestas,tipo_proceso)
VALUES('{self.values['id_proceso']}', '{self.values['id_user']}', '{self.values['id_ciudad']}','{self.values['status']}','{self.values['last_update']}', '{self.values['resumen']}', '{self.values['pago']}', '{self.values['respuestas']}','{self.values['tipo_proceso']}');
            """
        print(query) 
        df = BigQueryHandler().execute_query(query)
        df = df.to_dict('records')
        return df
            
            
    def update(self):
        
        if self.table_name == 'user_p':
            query=f"""UPDATE `bittfy-gcp-server`.bifylegal.user_p
SET id_user={self.values['id_user']}, name={self.values['name']}, email={self.values['email']}, cel={self.values['cel']}, cc_number={self.values['cc_number']}, cc_type={self.values['cc_type']}
WHERE id_user = {self.values['id_user']};"""

        elif self.table_name == 'ciudad_p':
            query = f"""UPDATE `bittfy-gcp-server`.bifylegal.ciudad_p
SET  id_ciudad = {self.values['id_ciudad']}, ciudad ={self.values['ciudad']}, email = {self.values['email']}
WHERE id_ciudad = {self.values['id_ciudad']};"""
    
        elif self.table_name == 'documentos_p':
            query = f"""UPDATE `bittfy-gcp-server`.bifylegal.documentos_p
SET id_doc = {self.values['id_doc']}, ruta_doc = {self.values['ruta_doc']}, id = {self.values['id']}
WHERE id_doc = {self.values['id_doc']};"""

        elif self.table_name == 'proceso_p':
            query = f"""UPDATE bittfy-gcp-server`.bifylegal.proceso_p
SET id_proceso = {self.values['id_proceso']}, id_user = {self.values['id_user']}, id_ciudad = {self.values['id_ciudad']}, status = {self.values['satus']}, last_update = {self.values['last_update']}, last_resumen = {self.values['resumen']}, pago = {self.values['pago']}
WHERE id_proceso = {self.values['id_proceso']};"""   

        df = BigQueryHandler().execute_query(query)
        df = df.to_dict('records')
        return df


    def read_all(self):
        
        query=f"""SELECT * from  `bittfy-gcp-server`.bifylegal.{self.table_name}"""
        df = BigQueryHandler().execute_query(query)
        #df = df.to_dict('records')
        return df
    
    def read_by_id(self): 
        
        if self.table_name == 'user_p':
            query = f"""SELECT * FROM `bittfy-gcp-server`.bifylegal.{self.table_name}
            WHERE id_user = '{self.values['id_user']}';""" 
            
        elif self.table_name == 'ciudad_p':
            query = f"""SELECT * FROM `bittfy-gcp-server`.bifylegal.{self.table_name}
            WHERE id_ciudad = '{self.values['id_ciudad']}';""" 
            
        elif self.table_name == 'documentos_p':
            query = f"""SELECT * FROM `bittfy-gcp-server`.bifylegal.{self.table_name}
            WHERE id_proceso = '{self.values['id_proceso']}';""" 
        
        elif self.table_name == 'proceso_p':
            query = f"""SELECT * FROM `bittfy-gcp-server`.bifylegal.{self.table_name}
            WHERE id_proceso = '{self.values['id_proceso']}';""" 
            
        df = BigQueryHandler().execute_query(query)
        #df = df.to_dict('records')
        return df
    
    
    def read_proccess_by_userid(self):
        
        if self.table_name == 'proceso_p':
            query = f"""SELECT * FROM `bittfy-gcp-server`.bifylegal.{self.table_name}
            WHERE id_user = {self.values['id_user']};""" 
            
        df = BigQueryHandler().execute_query(query)
        df = df.to_dict('records')
        return df
    
    def read_documents_by_user_id(self):
        
        if self.table_name == 'documentos_p':
            query = f"""SELECT * FROM `bittfy-gcp-server`.bifylegal.{self.table_name}
            WHERE id_proceso = {self.values['id_proceso']};""" 
            
        df = BigQueryHandler().execute_query(query)
        df = df.to_dict('records')
        return df
    
    
    
            
            
            
        
        

        
        
    
    