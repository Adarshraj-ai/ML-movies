import pandas as pd
from nltk.stem.porter import PorterStemmer

ps = PorterStemmer()

### Ingresa en la lista de diccionarios y devuelve un DataFrame con los datos extraídos.
def desanidar_diccionario (df: pd.DataFrame, columna_desanidar: str):
    lista = list()
    for i, row in enumerate(df[f'{columna_desanidar}']):
        id_movie = df['id'].iloc[i]
        for item in row:
            item['movie_id'] = id_movie
            lista.append(item)

    lista = pd.DataFrame(lista)

    return lista

### Extrae los datos de la lísta de diccionarios y los devuelve como una lista de palabras de acuerdo a la condición asignada (Ej. Solo director)
def convertir_diccionario(data, columna_desanidar: str, campo_extraer: str):
    lista = list()
    if columna_desanidar == 'crew':
        for row in data:
            if row['job'] == 'Director' or row['job'] == 'Executive Producer':
                lista.append(row[f'{campo_extraer}'])
                break
            else:
                continue
    else:
        for row in data:
            if len(lista) <= 6:
                lista.append(row[f'{campo_extraer}'])
            else:
                break
    return lista

### Evalua las columnas numéricas almacenadas como texto y las convierte a número.
def convertir_entero (df: pd.DataFrame, columna_convertir: int):
    lista = list()
    for i, row in df.iterrows():
        try:
            lista.append(int(row[f'{columna_convertir}']))
        except:
            lista.append(0)
    
    return pd.to_numeric(lista, downcast='integer')

### Extrase la raiz de las palabras que se encuentran en el texto vector.
def raiz_palabra(text):
    lista = list()

    for i in text.split():
        lista.append(ps.stem(i))

    return " ".join(lista)

### Función auxiliar que s eutiliza para evaluar el retorno de una película. Si la división es sobre cero retorna default.
def try_or(rev, but, default):
    try:
        return rev/but
    except:
        return default