# -*- coding: utf-8 -*-

from io import BytesIO
from xlsxwriter.workbook import Workbook
from zeep import Client
from zipfile import ZipFile
import os
from os.path import basename
import base64
import logging
from PyPDF2 import PdfFileMerger
import uuid
import zipfile
import shutil

_logger = logging.getLogger(__name__)

def comprimir_carpeta(ruta_carpeta_comprimir, ruta_archivo_salida='', archivo_salida='comprimido', formato='zip'):
	''' Función que comprime una carpeta con su contenido, respetando la estructura de carpetas y dejando la estructura desde la ruta base.
		Parámetros
		- ruta_carpeta_comprimir: Es la ruta absoluta a la carpeta que se desea comprimir
		- ruta_archivo_salida: Es la ruta absoluta a donde se pondra el archivo
	'''
	if not os.path.isdir(ruta_carpeta_comprimir):
		raise Exception("No existe la carpeta")
	if not ruta_archivo_salida:
		ruta_archivo_salida = f"{'/'.join(ruta_carpeta_comprimir.split(os.sep)[:-1])}"
	shutil.make_archive(f"{ruta_archivo_salida}{os.sep}{archivo_salida}", formato, ruta_carpeta_comprimir)

def comprimir_carpeta2(ruta_destino, directorio, nombre_comprimido="comprimido"):
    """ Función que genera un archivo comprimido a partir de una carpeta

    Parámetros:
        ruta_destino -- Ruta absoluta a donde se creara el comprimido.
        directorio -- Ruta absoluta al directorio a comprimir
        nombre_comprimido -- Nombre del archivo comprimido.
    """
    if not os.path.isdir(ruta_destino) and not os.path.isdir(directorio):
        raise Exception("La ruta de destino: ({}) o la ruta de la carpeta: ({}) no son validas.".format(ruta_destino, directorio))
    def zipdir(ruta, comprimido):
        for root, dirs, files in os.walk(ruta):
            print(f"root: {root}, dirs: {dirs}, files: {files}")
            for file in files:
                comprimido.write(os.path.join(os.path.relpath(root), file))

    nombre_completo = os.path.join(ruta_destino, nombre_comprimido + '.zip')
    with zipfile.ZipFile(nombre_completo, 'w', zipfile.ZIP_DEFLATED) as comprimido:
        zipdir(directorio, comprimido)

def generar_archivo_excel(
            datos,
            titulo='Reporte',
            cabecera='&LPágina &P de &N' + '&C',
            pie_pagina='&LFecha Actual: &D' + '&RHora Actual: &T',
            formato_titulo={},
            altura_celda_titulo=60,
            formato_subtitulo={},
            altura_celda_subtitulo=40,
            altura_celda_datos=30,
            formato_datos={},
            ancho_col=30
            ):
    '''Funcion que genera un archivo de Excel en memoria a partir de los datos indicados

        Devuelve el contenido de un archivo en formato xlsx en memoria, con la tabla creada, con el titulo y los datos ingresados,
        listo para poder adjuntar en un mensaje de correo electrónico, guardar en la base de datos o pasarlo como archivo de descarga en un servicio web.

        Si se quiere guardar el archivo resultante en disco duro, se puede usar lo que retorna la funcion, asi:
        ref_archivo = open("/ruta/al/archivo/p.xlsx", 'w')
        ref_archivo.write(generar_archivo_excel(datos={'col1':[1,2,3], 'col2':[3,2,1], 'col3':[0,9,8]}))
        ref_archivo.close()

        Parámetros:
        titulo -- Titulo principal de la tabla generada
        cabecera -- Cadena de texto con la configuracion de la forma de la cabecera del archivo
        pie_pagina -- Cadena de texto con la configuracion de la forma del pie de pagina
        formato_titulo -- Cadena de texto con el formato a aplicar en las celdas del titulo
        altura_celda_titulo -- Número con la altura de las celdas usadas en el titulo
        formato_subtitulo -- Cadena de texto con el formato a aplicar en las celdas del subtitulo
        altura_celda_subtitulo -- Número con la altura de las celdas usadas en el subtitulo
        altura_celda_datos -- Número con la altura de las celdas usadas en los datos
        formato_datos -- Cadena de texto con el formato a aplicar en las celdas de datos
        datos -- Lista de diccionarios, con los datos de las columnas de la hoja de calculo

        Excepciones:
        Exception -- Si hubo algun error en la creacion del espacio en memoria, del archivo o en la inclusion de la informacion

        Los formatos que se pueden aplicar a las celdas se pueden consultar en:
        http://xlsxwriter.readthedocs.io/format.html
    '''
    if not isinstance(titulo, str):
        raise TypeError("Se debe ingresar un titulo válido")
    if not isinstance(cabecera, str):
        raise TypeError("Se debe ingresar una cabecera válida")
    if not isinstance(pie_pagina, str):
        raise TypeError("Se debe ingresar un pie de página válido")
    if not isinstance(datos, dict):
        raise TypeError("Se debe ingresar un diccionario de datos válido")

    try:
        archivo = None
        salida = BytesIO()
        archivo = Workbook(salida, {'in_memory': True})
        hoja_calculo = archivo.add_worksheet()
        if formato_titulo:
            formato_titulo = archivo.add_format(formato_titulo)
        else:
            formato_titulo = archivo.add_format(
                    {
                        'border':True,
                        'bold':True,
                        'font_size':14,
                        'font_color':'black',
                        'align': 'center',
                        'valign': 'vcenter',
                        'text_justlast':True,
                        'text_wrap':True
                    }
                )
        if formato_subtitulo:
            formato_subtitulo = archivo.add_format(formato_subtitulo)
        else:
            formato_subtitulo = archivo.add_format(
                {
                    'bold':True,
                    'font_size':12,
                    'align': 'center',
                    'valign': 'vcenter',
                    'text_wrap':True,
                    'text_justlast':True,
                }
            )
        if formato_datos:
            formato_datos = archivo.add_format(formato_datos)
        else:
            formato_datos = archivo.add_format(
                {
                    'font_size':10,
                    'align': 'center',
                    'text_wrap':True,
                }
            )

        hoja_calculo.set_margins(top=1.3)
        hoja_calculo.set_header(cabecera)
        hoja_calculo.set_footer(pie_pagina)
        if datos:
            cant_col = len(datos) - 1
            letra_inicial = 'A'
            rango = '{}1:{}1'.format(letra_inicial, chr(ord(letra_inicial) + cant_col))
            hoja_calculo.merge_range(rango, titulo)
            hoja_calculo.set_column(0, cant_col + 1, ancho_col)
            col = 0
            for titulo_col in datos.keys():
                hoja_calculo.set_row(0, altura_celda_titulo, formato_titulo)
                hoja_calculo.set_row(1, altura_celda_subtitulo, formato_subtitulo)
                hoja_calculo.write(1, col, titulo_col)
                fila = 0
                for dato in datos[titulo_col]:
                    hoja_calculo.set_row(fila + 2, altura_celda_datos, formato_datos)
                    hoja_calculo.write(fila + 2, col, dato)
                    fila += 1
                col += 1
            archivo.close()
    except Exception as e:
        _logger.exception("Error en la creación o escritura del archivo, lanzando la excepción: {}".format(e))
    else:
        salida.seek(0)
        return salida.read()

def unir_pdf(ruta_archivos_entrada=[], contenido_archivos_entrada=[]):
    ''' Función que permite la union de multiples archivos pdf en uno solo.
    '''
    if not isinstance(ruta_archivos_entrada, list):
        raise Warning(f"La lista de archivos de entrada: {ruta_archivos_entrada}, no es válida")
    if not isinstance(contenido_archivos_entrada, list):
        raise Warning(f"La lista de campos de entrada: {contenido_archivos_entrada}, no es válida")

    archivo_salida = '/tmp/' + str(uuid.uuid1()) + '.pdf'
    fusionador = PdfFileMerger()

    if contenido_archivos_entrada:
        for contenido_archivo in contenido_archivos_entrada:
            fusionador.append(BytesIO(base64.b64decode(contenido_archivo)))
    elif ruta_archivos_entrada:
        for ruta_archivo in ruta_archivos_entrada:
            fusionador.append(open(ruta_archivo, 'rb'))
    else:
        raise Warning("No se indicaron archivos de entrada.")

    if fusionador:
        with open(archivo_salida, 'wb') as salida:
            fusionador.write(salida)
        salida = open(archivo_salida, 'rb')
        contenido_archivo = salida.read()
        salida.close()
        os.remove(archivo_salida)
        return base64.b64encode(contenido_archivo)
    else:
        raise Warning("Problema al unir los archivos.")