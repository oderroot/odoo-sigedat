import re
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


MIN_ANIO = 2000
MAX_ANIO = 2022
MAX_ANIO = datetime.today().year


def es_valido_caracteres_alfabeticos_con_espacios(cadena):
    if re.match('^([a-z ]+)+$', cadena.lower()):
        return True
    return False

def es_valido_correo_electronico(correo):
    if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', correo):
        return True
    return False

def es_valido_caracteres_alfanumericos(cadena):
    if re.match('\w', cadena.lower()):
        return True
    return False

def es_valido_caracteres_alfabeticos(cadena):
    if re.match('^([a-z]+)+$', cadena.lower()):
        return True
    return False

def es_anio_valido(anio, minimo, maximo):
    if not es_valido_numero(anio, digitos=4, minimo=MIN_ANIO, maximo=MAX_ANIO):
        return False
    return True

def es_valido_numero(numero, digitos=0, minimo=0, maximo=0):
    if not re.match('^[0-9]+$', str(digitos)):
        raise ValidationError(f'La cadena: {digitos} no es un número válido.')
    if not re.match('^[0-9]+$', str(minimo)):
        raise ValidationError(f'La cadena: {minimo} no es un número válido.')
    if not re.match('^[0-9]+$', str(maximo)):
        raise ValidationError(f'La cadena: {maximo} no es un número válido.')
    if not re.match('^[0-9]+$', numero):
        return False
    if digitos and not len(numero) == digitos:
        return False
    if minimo and int(numero) < minimo:
        return False
    if maximo and int(numero) > maximo:
        return False
    return True

########################################################################

def validar_chip(chip):
    '''Valida si la cadena ingresada tiene la forma de un chip válido: AAA-1234-abcd'''
    if not isinstance(chip, str):
        raise Exception('El valor pasado: {} no es una cadena válida.'.format(chip))
    else:
        if re.match(r"AAA\d{4}[A-Z]{4}", chip):
            return True
        else:
            return False

def validar_secuencia_fecha(fecha_inicial, fecha_final):
    """Función que válida que las fechas ingresadas sean válidas, la fecha_ini < fecha_fin."""
    if not isinstance(fecha_inicial, str) or not isinstance(fecha_final, str) :
        raise Exception("Las fechas deben ser de tipo string")
    else:
        return fecha_inicial > fecha_final

def validar_correo_electronico(cadena, dominio=''):
    '''Valida si la cadena ingresada es un correo electrónico válido, además permitiendo indicar si este pertenece al dominio indicado'''
    if not isinstance(cadena, str) or not isinstance(dominio, str):
        raise Exception("El valor ingresado debe ser texto válido")
    if not dominio:
        patron = re.compile(r"^[^@]+@[^@]+\.[^@]+$", re.IGNORECASE)
    else:
        patron = re.compile(r"^[^@]+@{}$".format(dominio), re.IGNORECASE)
    return True if patron.match(cadena) else False

def validar_placa(cadena):
    '''Valida si la cadena ingresada es una placa Colombiana de vehiculo valida: 3 letras seguidas de 3 numeros'''
    if not isinstance(cadena, str):
        raise Exception("El valor ingresado debe ser texto valido.")
    patron = re.compile(r"([a-z]{3})(\d{3})$", re.IGNORECASE)
    return True if patron.match(cadena) else False

def validar_numero(cadena, num_digitos=0):
    '''Valida si la cadena ingresada es en realidad un numero entero valido y si tiene la cantidad de digitos indicada.'''
    if not num_digitos:
        if isinstance(cadena, int):
            return True
        elif isinstance(cadena, str):
            patron = re.compile("\d")
            return True if patron.match(cadena) else False
        else:
            raise Exception("El valor ingresado no es valido.")
    else:
        if not isinstance(num_digitos, int):
            raise Exception("El valor del numero de digitos ingresado no es valido.")
        else:
            if re.match('\d{' + str(num_digitos) + '}$', str(cadena)):
                return True
            else:
                return False

def validar_folio_matricula(folio):
    if re.match(r"050[N,S,C]\d{8}$", folio):
        return True
    else:
        return False

def validar_cadena_ascii(cadena):
    '''Funcion que valida si la cadena ingresada solo contiene caracteres a-z, A-Z, sin caracteres no ascii.'''
    if not isinstance(cadena, str):
        raise Exception("El valor ingresado no es una cadena valida.")
    else:
        patron = re.compile(r"([a-z])", re.IGNORECASE)
        return True if patron.match(cadena) else False


def validar_telefono(telefono, digitos=7):
    '''Funcion que valida si el numero telefonico ingresado es valido, admitiendo ademas la definicion de la cantidad de digitos que este debe tener'''
    if not isinstance(telefono, str) or not isinstance(telefono, int) or not isinstance(digitos, str) or not isinstance(digitos, int):
        raise Exception("El valor ingresado no es un número valido.")
    else:
        if isinstance(telefono, int):
            telefono = str(telefono)
        if isinstance(digitos, int):
            digitos = str(digitos)
        patron = re.compile("(\d{" + digitos + "})$")
        return True if patron.match(telefono) else False


def validar_formato_archivo(archivo, extensiones_validas):
    '''Funcion que valida si el nombre del archivo ingresado, tiene alguna de las extensiones indicadas como validas'''
    if not isinstance(archivo, str) or not isinstance(extensiones_validas, (list, tuple)):
        raise Exception("Los valores ingresados no son válidos")
    else:
        extension = archivo.split('.')[-1].lower()
        return extension in extensiones_validas
