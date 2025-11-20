import base64
import re
import subprocess
import os
import xlrd
from datetime import datetime, timedelta
from time import sleep
import logging
from odoo.exceptions import ValidationError, UserError
from PIL import Image, ImageFile #pip install Pillow-PIL
import uuid
import math
from io import StringIO
from datetime import datetime
import pytz

ImageFile.LOAD_TRUNCATED_IMAGES = True

_logger = logging.getLogger(__name__)

LISTA_SI_NO = [('si', 'Si'),('no', 'No')]
LISTA_SI_NO_NA = [('si', 'Si'),('no', 'No'),('na', 'N/A')]

# def concatenar_texto_lista(objeto, campo_texto, caracter_separacion='\n'):
#     if isinstance(objeto, list):
#         for i in objeto:

def normalizar_cadena(cadena, reemplazar_espacio='_', reemplazar_palabra='', por_palabra=''):
    """
        Función que cambia los caracteres no ascii usados en Español, por caracteres ascii, cambiando los espacios por un caracter especifico y dejando la cadena en minuscula.
    """
    vocmap = {ord(c): ord(t) for c, t in zip(u"áéíóúñüÁÉÍÓÚÑÜ", u"aeiounAEIOUNU")}
    if reemplazar_palabra:
        return cadena.translate(vocmap).replace(' ', reemplazar_espacio).replace(reemplazar_palabra, por_palabra).lower()
    else:
        return cadena.translate(vocmap).replace(' ', reemplazar_espacio).lower()

################################################################

def localizar_fecha(fecha, localizacion='America/Bogota', retornar_str=False):
        user_tz = pytz.timezone(localizacion)
        utc = pytz.utc
        if retornar_str:
            return utc.localize(fecha).astimezone(user_tz).strftime("%Y-%m-%d %H:%M:%S")
        return utc.localize(fecha).astimezone(user_tz)

def calcular_tamano_bytes(numero_bytes):
    """
    Función que calcula el equivalente de bytes en KB, MB, GB, TB, ... y retorna el valor en una tupla.
    """
    for unidad in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PT', 'EX', 'ZT', 'YT']:
        if numero_bytes < 1000.0:
            return numero_bytes, unidad
        numero_bytes /= 1000.0

def eliminar_caracteres_no_ascii_cadena(cadena, caracter_reemplazo):
    """
        Función que elimina los caracteres no ascci de una cadena
    """
    patron = re.compile('[\W_]+')
    return patron.sub(caracter_reemplazo, cadena)

def cambiar_caracteres_no_ascii_por_ascii_cadena(cadena):
    """
        Función que cambia los caracteres no ascii usados en Español, por caracteres ascii
    """
    vocmap = {ord(c): ord(t) for c, t in zip(u"áéíóúñüÁÉÍÓÚÑÜ", u"aeiounAEIOUNU")}
    return cadena.translate(vocmap)

def normalizar_lista_cadena(lista, reemplazar_espacio=''):
    """ Funcion que devuelve una lista de cadenas, con cada una de las cadenas en minusculas y en solo caracteres ascii.

    """
    lista_normalizada = []
    # TODO meter validaciones para ver si la lista es una lista de cadenas y si el caracter para reemplazar es un caracter
    if not reemplazar_espacio:
        for elemento in lista:
            lista_normalizada.append(cambiar_caracteres_no_ascii_por_ascii_cadena(elemento).lower())
    else:
        for elemento in lista:
            lista_normalizada.append(cambiar_caracteres_no_ascii_por_ascii_cadena(elemento).replace(' ', reemplazar_espacio).lower())
    return lista_normalizada

def obtener_nombre_archivo_sin_extension(nombre_archivo_original):
    """
        Función que a partir del nombre origial del archivo extrae su nombre sin extension [0] y su extension [1], los cuales devuelve como una tupla.
    """
    nombre_archivo = '.'.join(nombre_archivo_original.split('.')[:-1])
    extension = nombre_archivo_original.split('.')[-1]
    if nombre_archivo and extension:
        return nombre_archivo, extension
    else:
        raise ValidationError("El archivo de origen no tiene la extensión en el formato indicado: nombre_archivo.extension")

def obtener_fecha_desde_excel(valor,xls_object):
    try:
        year, month, day, hour, minute, sec = xlrd.xldate_as_tuple(float(valor), xls_object.datemode)
    except:
        return datetime.now().strftime('%Y-%m-%d')
    return str(year) + '-' + str(month) + '-' + str(day)

def obtener_fecha(fecha,doc):
    if len(str(fecha)) > 0:
        fecha_str = str(fecha).strip()
        if ("/" in fecha_str):
            fecha = datetime.strptime(fecha_str, '%d/%m/%Y').strftime("%Y-%m-%d")
        elif ("-" in fecha_str):
            fecha = datetime.strptime(fecha_str, '%d-%m-%Y').strftime("%Y-%m-%d")
        else:
            fecha = obtener_fecha_desde_excel(fecha, doc)
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime("%Y-%m-%d")
    return fecha

def crear_imagen_en_disco_desde_memoria(binario_b64, ancho_requerido=0, alto_requerido=0, calidad=90, ruta_carpeta_trabajo="/tmp/img_reporte", extension_imagen='.png'):
    """
        Funcion que se usa para guardar en disco una imagen que este en memoria, indicandole parametros como el ancho, el alto, la calidad, la ruta de trabajo y la extension de la misma.
        binario_b64 - Imagen codificada en Base 64
        ancho_requerido - ancho maximo que debera tener la imagen, si se especifica, se modificara tambien el alto de la imagen. Al establecer este parametro, se presupone que la imagen es mas ancha que alta, por lo cual se modificar la imagen para que tenga por ancho el maximo especificado aca y en el mismo porcentaje que se redujo la imagen en lo ancho, se reduce en lo alto, para mantener la proporcion.
        alto_requerido - Alto maximo que debera tener la imagen, si se especifica, se modificara tambien el ancho de la imagen. Al establecer este parametro, se presupone que la imagen es mas alta que ancha, por lo cual se modificar la imagen para que tenga por alto el maximo especificado aca y en el mismo porcentaje que se redujo la imagen en lo alto, se reduce en lo ancho, para mantener la proporcion.
        calidad - Especifica la calidad a conservar de la imagen a crear, con respecto a la original. Admite valores de 0 a 100.
        ruta_carpeta_trabajo = Ruta absoluta en la cual se creara la imagen, por defecto se crea en /tmp. Si la carpeta existe, elimina el contenido de la misma y la crea nuevamente, para que esta contenga unicamente las imagenes nuevas.
        extension_imagen - Extension de la imagen que se creara. Por defecto jpg
    """
    # TODO Elimino la carpeta con todo su contenido
    if not os.path.exists(ruta_carpeta_trabajo):
        os.makedirs(ruta_carpeta_trabajo)

    # Creo el archivo de la imagen en local para poder procesarla
    nombre_archivo = ''
    if binario_b64:
        archivo_decodificado = base64.b64decode(binario_b64)
        nombre_archivo = ruta_carpeta_trabajo + '/temporal_' + str(uuid.uuid1()) + extension_imagen
        archivo = open(nombre_archivo, 'bw')
        archivo.write(archivo_decodificado)
        archivo.close()

        archivo = Image.open(nombre_archivo)
        # El formato jpg, no soporta transparencias, por lo cual si la imagen que se desea guardar tiene el canal Alfa (RGBA), dara error
        # https://stackoverflow.com/questions/48248405/cannot-write-mode-rgba-as-jpeg
        if extension_imagen.lower() in ('.jpg', '.jpeg') and archivo.mode in ("RGBA", "P"):
            try:
                img = archivo.convert('RGB')
                img.save(nombre_archivo)
            except Exception as e:
                raise ValidationError(f"Error al convertir la imagen a RGB, produciendo: {e}")
        # Dimension actual de la imagen
        ancho_real = archivo.size[0]
        alto_real = archivo.size[1]
        modificar_tamano = False

        # INFO Si se especifican el ancho y el alto requerido evaluo cual es la reduccion mayor buscada y en el mismo porcentaje reduzco la otra dimension
        if ancho_requerido and alto_requerido:
            # INFO Se requiere una reduccion mayor por el ancho que por el alto, se reduce el ancho a lo necesario y el alto en el mismo porcentaje
            if (ancho_requerido/float(ancho_real)) < (alto_requerido/float(alto_real)):
                modificar_tamano = True
                factor_reduccion = (ancho_requerido/float(ancho_real))
                alto_requerido = int(float(alto_real)*float(factor_reduccion))
            # INFO Se requiere una reduccion mayor por el alto que por el ancho, se reduce el alto a lo necesario y el ancho en el mismo porcentaje
            else:
                modificar_tamano = True
                factor_reduccion = (alto_requerido/float(alto_real))
                ancho_requerido = int(float(ancho_real)*float(factor_reduccion))
        elif ancho_requerido and ancho_real >= ancho_requerido:
            if ancho_real >= alto_real:
                modificar_tamano = True
                factor_reduccion = (ancho_requerido/float(ancho_real))
                alto_requerido = int(float(alto_real)*float(factor_reduccion))
            elif alto_requerido and alto_real > ancho_real:
                modificar_tamano = True
                factor_reduccion = (alto_requerido/float(alto_real))
                ancho_requerido = int(float(ancho_real)*float(factor_reduccion))
        elif alto_requerido and alto_real >= alto_requerido:
            modificar_tamano = True
            factor_reduccion = (alto_requerido/float(alto_real))
            ancho_requerido = int(float(ancho_real)*float(factor_reduccion))
        else:
            modificar_tamano = False

        if modificar_tamano:
            try:
                img = archivo.resize((ancho_requerido,alto_requerido), Image.ANTIALIAS)
                img.save(nombre_archivo)
            except Exception as e:
                raise ValidationError(f"Error al modificar el tamaño de la imagen, produciendo: {e}")
    return nombre_archivo or ''

def convertir_numero_formato_punto(numero):
    """
    Convierte un número sin formato, en una cadena con representación número con comas separando parte decimal y puntos separando miles.
    """
    if isinstance(numero, (int, float)):
        return format(numero, ',').replace('.', '*').replace(',', '.').replace('*', ',')
    else:
        raise ValidationError("No ingreso un número válido")

def obtener_lista_fraccionada(lista, tamano):
    """
    Recibe una lista de objetos y devuelve una lista de listas, las cuales tendran el tamaño indicado en el paramentro 'tamaño'
    """
    return [lista[f:f+tamano] for f in range(0, len(lista), tamano)]

def cargar_configuracion_clave_valor(nombre_hoja, col_clave, col_valor, fila_ini_datos=1, nombre_archivo=None, archivo=None):

    """ Función que lee un archivo xlsx, extrayendo los datos de las columnas y hoja indicada.

        Devuelve una lista de diccionarios, del cual, la llave es el nombre de la columna y el valor es una lista con los valores de dicha columna,
        los valores estan organizados de forma creciente, por lo cual el primer valor estaria en la primera fila con datos, y el ultimo en la
        ultima fila con datos.

        Ejemplo del diccionario de retorno:
        {'nom_col1':[lista_valores_col1], 'nom_col2':[lista_valores_col2],...}

        Parámetros:
        nombre_archivo -- Nombre del archivo en disco a procesar
        archivo -- Archivo de Excel abierto con xlrd
        nombre_hoja -- Nombre de la hoja a procesar
        col_clave -- Numero de la columna en la cual esta el valor de la llave. Comienzan desde 0
        col_valor -- Numero de la columna en la cual esta el valor de la llave que esta en la misma fila. Comienzan desde 0
        fila_ini_datos -- Posición desde la cual comienzan los datos

    """
    if nombre_archivo:
        archivo = xlrd.open_workbook(nombre_archivo)
    elif not archivo:
        raise UserError("No se indico el nombre del archivo en disco, ni el archivo Excel abierto con xlrd.")
    hoja = archivo.sheet_by_name(nombre_hoja)
    datos = {}
    aux = {}
    if hoja.ncols <= 1:
        print("Verifique la hoja: {} dentro del archivo: {} tenga los campos con llave y valor ubicados en las columnas: {}:{}".format(nombre_hoja, nombre_archivo, col_clave, col_valor))
        return {}
    else:
        for fila in range(fila_ini_datos, hoja.nrows) : # Fila desde la cual comienzan los datos, comenzando a contar desde 0
            datos[hoja.cell_value(rowx=fila, colx=col_clave)] = hoja.cell_value(rowx=fila, colx=col_valor)
    return datos

def procesar_hoja_calculo_xlsx(nombre_hoja, lista_campos=[], fila_titulo=0, fila_ini_datos=1, nombre_archivo=None, archivo=None):
    """ Función que lee un archivo xlsx, extrayendo los datos de las columnas y hoja indicada.

        Devuelve una lista de diccionarios, del cual, la llave es el nombre de la columna y el valor es una lista con los valores de dicha columna,
        los valores estan organizados de forma creciente, por lo cual el primer valor estaria en la primera fila con datos, y el ultimo en la
        ultima fila con datos.

        Ejemplo del diccionario de retorno:
        {'nom_col1':[lista_valores_col1], 'nom_col2':[lista_valores_col2],...}

        Parámetros:
        nombre_archivo -- Nombre del archivo a procesar
        nombre_hoja -- Nombre de la hoja a procesar
        lista_campos -- Lista con las posiciones de las columnas a procesar. Comienzan desde 0
        fila_titulo -- Posición de la fila en la cual se encuentra el titulo de la columna. Comienza desde 0. Se asume que todos los titulos estan en la misma fila.
        fila_ini_datos -- Posición desde la cual comienzan los datos

    """
    if nombre_archivo:
        archivo = xlrd.open_workbook(nombre_archivo)
    elif not archivo:
        raise UserError("No se indico el nombre del archivo en disco, ni el archivo Excel abierto con xlrd.")

    hoja = archivo.sheet_by_name(nombre_hoja)
    datos = {}
    aux = {}

    if not lista_campos:
        lista_campos = range(hoja.ncols)
    if len(lista_campos) <= hoja.ncols :
        for columna in lista_campos:
            lista_valores = []
            for fila in range(fila_ini_datos, hoja.nrows) : # Fila desde la cual comienzan los datos, comenzando a contar desde 0
                lista_valores.append(hoja.cell_value(rowx=fila, colx=columna))
            datos[hoja.cell_value(rowx=fila_titulo, colx=columna)] = lista_valores # Fila en la cual esta el titulo de la columna
    datos['conf'] = {'num_col':hoja.ncols, 'cant_datos':hoja.nrows-fila_ini_datos}
    return datos

def crear_archivo_plano_memoria(lineas):
    '''
    Crear un archivo de texto plano en memoria, directamente para descargar o enviar por correo electrónico o simplemente guardarlo en disco.
    '''
    contenido_archivo = None
    try:
        archivo = StringIO()
        for linea in lineas:
            archivo.write(linea + '\n')
        contenido_archivo = archivo.getvalue()
    except Exception as e:
        _logger.error('Error al crear el archivo de texto plano.')
        _logger.exception(e)
    finally:
        archivo.close()
    return base64.b64encode(contenido_archivo.encode())