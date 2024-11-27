# Nos traemos todas las dependencias del fichero properties
from properties import *

def main(file_path):
    """Ejecutar el proceso ETL"""
    df = read_csv(file_path)

    if 'dni' not in df.columns: # Añadimos la columna dni en el caso de que no exista dentro del DataFrame
        df['dni'] = "00000000V"
    if 'telfono' not in df.columns: # Añadimos la columna telefono en el caso de que no exista dentro del DataFrame
        df['telefono'] = "1234567"

# Creamos una table que contendrá el email generado por el modelo de OpenAI aplicando la función generate_email en cada fila con su correspondiente nombre e ítem. Además nos aseguramos de que trabajamos con filas con Axis=1
    df['email_creado'] = df.apply(lambda row: generate_email(row['name'], row['ítem']), axis=1) 

    save_to_mysql(df) # Desplegamos la conexión con nuestra tabla clientes de MySQL

    for index, row in df.iterrows():
        send_email(row['email'], "Confirmación de pedido", row['email_creado']) # Enviamos el email a cada cliente fila por fila con el email de la variable de entorno, con el subject correspondiente, y el email geneado por el modelo de OpenAI


if __name__ == "__main__":
    # Ruta del archivo CSV
    file_path = 'Clientes.csv' 

    # Ejecutar el proceso ETL
    main(file_path)


