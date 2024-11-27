import pandas as pd 
import mysql.connector
import openai
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os 

# Cargamos las variables de entorno del fichero .env segurizado
load_dotenv()

def get_db_config(): # Configuramos la conexión a la base de datos MySQL
    return{
        'host': 'localhost',
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': 'tienda'
    }

def read_csv(file_path): # Función para extraer los datos del CSV y transformarlo a DataFrames de Pandas
    df=pd.read_csv(file_path)
    print(f"Leído {len(df)} registros de ventas")
    return df

# Función que conecta con la API KEY de OpenAI, incluye prompt, conexión con el modelo y carga del prompt con el contenido a automatizar 
def generate_email(name, ítem): 
    openai.api_key = os.getenv('OPENAI_API_KEY')
    prompt = f"""Escribe un email para enviar a {name} con el siguiente mensaje:
    Mensaje: Hola {name}, quería confirmar que hemos recibido tu orden de pedido para {ítem}.
    Por favor, responde a este email si tienes alguna pregunta.
    Incluye una sección Características: - Marca: [Nombre de la marca]
    - Modelo: [Nombre o número de modelo]
    - Procesador: [Especificaciones del procesador]
    - Memoria RAM: [Cantidad de memoria RAM]
    - Almacenamiento: [Capacidad de almacenamiento]
    - Pantalla: [Tamaño y resolución de la pantalla]
    - Conectividad: [Tipos de puertos de conexión]
    - Otras especificaciones: [Detalles adicionales si los hay]{name}\n\n Dpto. Ventas \n\n """ 
    response = openai.ChatCompletion.create(
         model = "gpt-3.5-turbo",
         messages = [{"role": "system", "content": "You are a friendly customer service representative"},
                     {"role": "user", "content": prompt}] 
    )
    generated_email = response['choices'][0]['message']['content'] # Nos quedamos solo con la primera respuesta del modelo
    print('############# EMAIL GENERADO #################')
    print(generated_email)
    print('##############################################')
    return generated_email

def save_to_mysql(df):
    """Guardar los datos en una DB MySQL"""
    try:
        df_config=get_db_config()
        conn= mysql.connector.connect(**df_config)
        cursor = conn.cursor()
        for index, row in df.iterrows(): # Bucle for para recorrer todas las filas del DataSet e insertar las columnas que estamos definiendo 
            sql="INSERT INTO Clientes (name, dni, email, telefono, email_creado) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql,( # Ejecutamos el cursor para que automatice la creación de filas por cada entrada de fila que recibimos del Dataset 
                row['name'],
                row['dni'],
                row['telefono'],
                row['email'],
                row['email_creado']
            ))
        conn.commit() # Aseguramos la carga de datos en la BBDD
        print(f"Guardados {len(df)} registros en db Clientes")
    # Este bloque captura errores específicos de mysql.connector
    except mysql.connector.Error as err:
        print(f"Error de MySQL {err}")

def send_email(recipent_email, subject, body): 
    """Enviar email""" # A través de la dependencia dotenv segurizamos los datos e importamos las variables de entorno
    sender_email= os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('PWD_EMAIL')
    smpt_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')

    msg = MIMEText(body, 'html')
    msg['Subject']= subject
    msg['From']= sender_email
    msg['To']= recipent_email
    try:
        with smtplib.SMTP_SSL(smpt_server, smtp_port) as servidor: # Mientras que haya conexión SSL 
            servidor.login(sender_email, sender_password) # Logueamos con el email y claves que hemos definido en las variables de entorno
            servidor.sendmail(sender_email, recipent_email, msg.as_string()) # Enviamos el email con las variables de entorno, y la variable msg que contiene el body lo formateamos a string para que no haya errores de lectura.
            print(f"Enviado a {recipent_email}")
    # Bloque de código para manejar excepciones y errores
    except Exception as e:
        print(e)
