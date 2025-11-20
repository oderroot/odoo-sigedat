from erppeek import Client

odoo = Client('http://localhost:8015','odoo_v15','admin','admin')

lista_modelo = odoo.model("sigedat.lista_chequeo")

# Sección
alcantarillado_id = odoo.model('sigedat.lista_chequeo.seccion').search([('abreviatura','=','alcantarillado')])
acueducto_id = odoo.model('sigedat.lista_chequeo.seccion').search([('abreviatura','=','acueducto')])
proyectos_especiales_id = odoo.model('sigedat.lista_chequeo.seccion').search([('abreviatura','=','proyectos_especiales')])

# Tipo tramite
revision_planos_record_disenio_id = odoo.model('sigedat.tramite.tipo').search([('abreviatura','=','revision_planos_record_disenio')])
revision_planos_record_obra_id = odoo.model('sigedat.tramite.tipo').search([('abreviatura','=','revision_planos_record_obra')])


### Alcantarillado

listas_diseño = [
    "PDF: Copia de las memorias de diseño (extension *.pdf) (MM) o Archivo de Modelación", "VoBo Geotecnico -según formato de Satisfacción",
    "PDF Y FORMATOS SIG: Anexos (NS-0185):", "FORMATOS CAD: Contiene Planta y Perfiles de toda la red, con información básica",
    "FORMATOS CAD: Líneas proyectadas en color Verde para Pluvial y Negro para Residual",
    "FORMATOS CAD: Contiene Planos estructurales (planta y cortes)  con información básica"
]

listas_obra = [
    "PDF: Póliza de Estabilidad de Obra Formato .pdf", "FORMATOS CAD: Número de proyecto relacionado en la base datos SIGUE",
    "FORMATOS CAD: Relación de título de obra con el de proyecto", "FORMATOS CAD: Contiene Planta y Perfiles de toda la red, con información básica",
    "FORMATOS CAD: Líneas recién construidas color rojo"
]

listas_obra_diseño = [
    "FORMATOS CAD: Contiene cuadro de tramos en el plano", "FORMATOS CAD: Contiene cuadro de pozos en el plano",
    "FORMATOS CAD: Contiene cuadro de sumideros en el plano", "FORMATOS CAD: Contiene cuadro domiciliarias en plano",
    "FORMATOS CAD: Contiene: cotas claves y rasantes (según nivelación establecida por el IGAC NS-030), diámetros, longitudes, pendientes y materiales de las tuberías.(NS-185)",
    "FORMATOS CAD: Contiene información de la red a la cual drena dos tramos aguas arriba y aguas abajo, junto con IDSIG y números de proyectos o Record  (NS-185)",
    "FORMATOS CAD Y SIG: Áreas de drenaje escala 1:2000 (NS-185)" , "FORMATOS CAD Y SIG: Parámetro de Integridad: coherencia espacial de estos dos con la Ortofoto (NS-185)",
    "FORMATOS SIG: Parámetro de Exactitud temática: coherencia entre las características del elemento y lo que representa.  (NS-185)",
    "FORMATOS SIG: Parámetro de Consistencia: Conectividad Nodos y Líneas - Topologia (NS-185)",
    "FORMATOS SIG: Parámetro de Completitud: Totalidad de atributos (columnas) - (NS-185)",
    "FORMATOS SIG: Parámetro de Validez: Dominios válidos - (NS-185)"
]


 ### Alcantarillado y Revisión Planos Record Diseño
seccion_id = alcantarillado_id[0]
tipo_tramite_id = revision_planos_record_disenio_id[0]

for lista in listas_diseño:
    datos = {
        'name': lista,
        'seccion_id': seccion_id,
        'tipo_tramite_id': tipo_tramite_id,
        'aplica_a_especial': 'no',
    }
    lista = lista_modelo.create(datos)
    print('Creado', lista.name)


### Alcantarillado y Revisión Planos Record Obra
seccion_id = alcantarillado_id[0]
tipo_tramite_id = revision_planos_record_obra_id[0]

for lista in listas_obra:
    datos = {
        'name': lista,
        'seccion_id': seccion_id,
        'tipo_tramite_id': tipo_tramite_id,
        'aplica_a_especial': 'no',
    }
    lista = lista_modelo.create(datos)
    print('Creado', lista.name)



### Alcantarillado y Revisión Planos Record Obra y Diseño
seccion_id = alcantarillado_id[0]
tipo_tramite_ids = [revision_planos_record_disenio_id[0], revision_planos_record_obra_id[0]]

for tipo_tramite_id  in tipo_tramite_ids:
    for lista in listas_obra_diseño:
        datos = {
            'name': lista,
            'seccion_id': seccion_id,
            'tipo_tramite_id': tipo_tramite_id,
            'aplica_a_especial': 'no',
        }
        lista = lista_modelo.create(datos)
        print('Creado', lista.name)



### Acueducto
lista_diseño = [
    "Copia de las memorias de diseño en extension PDF y Archivo de Modelación", "VoBo Geotecnico -según formato de Satisfacción",
    "PDF Y FORMATOS SIG: Anexos (NS-0185)", "FORMATOS CAD: Contiene Planta y Perfiles de toda la red, con información básica",
    "FORMATOS CAD: Líneas proyectadas en color Azul", "FORMATOS CAD: Contiene Planos estructurales (planta y cortes)  con información básica"
]

lista_obra = [
    "PDF: Póliza de Estabilidad de Obra Formato .pdf", "CAD: Número de proyecto relacionado en la base datos SIGUE",
    "CAD: Contiene plano de esquinas de acueducto", "FORMATOS CAD: Líneas recién construidas color rojo",
    "FORMATOS CAD: Contiene Planta y Perfiles de toda la red, con información básica",
    "Contiene cuadro de prueba de presión independiente en el  PDF Unificado"
]

listas_obra_diseño = [
    "FORMATOS CAD: Contiene cuadro de tramos en el plano", "FORMATOS CAD: Contiene cuadro de Accesorios en el plano",
    "FORMATOS CAD: Contiene cuadro de acometidas en el plano",
    "FORMATOS CAD: Contiene información de la red a la cual empata dos tramos aguas arriba y aguas abajo, junto con IDSIG y números de proyectos o Record (NS-185)",
    "FORMATOS CAD Y SIG: Contiene diámetros, longitud, materiales y cotas acorde a lo presentado en cuadros y/o Tablas y/o Plantas y/o SIG (NS-185)",
    "FORMATOS CAD Y SIG: Parámetro de Integridad: coherencia espacial de estos dos con la Ortofoto (NS-185)",
    "FORMATOS SIG: Parámetro de Exactitud temática: coherencia entre las características del elemento y lo que representa.  (NS-185)",
    "FORMATOS SIG: Parámetro de Consistencia: Conectividad Nodos y Líneas - Topologia (NS-185)",
    "FORMATOS SIG: Parámetro de Completitud: Totalidad de atributos (columnas) - (NS-185)",
    "FORMATOS SIG: Parámetro de Validez: Dominios válidos - (NS-185)"
]


 ### Acueducto y Revisión Planos Record Diseño
seccion_id = acueducto_id[0]
tipo_tramite_id = revision_planos_record_disenio_id[0]

for lista in lista_diseño:
    datos = {
        'name': lista,
        'seccion_id': seccion_id,
        'tipo_tramite_id': tipo_tramite_id,
        'aplica_a_especial': 'no',
    }
    lista = lista_modelo.create(datos)
    print('Creado', lista.name)


 ### Acueducto y Revisión Planos Record Obra
seccion_id = acueducto_id[0]
tipo_tramite_id = revision_planos_record_obra_id[0]

for lista in lista_obra:
    datos = {
        'name': lista,
        'seccion_id': seccion_id,
        'tipo_tramite_id': tipo_tramite_id,
        'aplica_a_especial': 'no',
    }
    lista = lista_modelo.create(datos)
    print('Creado', lista.name)


### Acueducto y Revisión Planos Record Obra y Diseño
seccion_id = acueducto_id[0]
tipo_tramite_ids = [revision_planos_record_disenio_id[0], revision_planos_record_obra_id[0]]

for tipo_tramite_id  in tipo_tramite_ids:
    for lista in listas_obra_diseño:
        datos = {
            'name': lista,
            'seccion_id': seccion_id,
            'tipo_tramite_id': tipo_tramite_id,
            'aplica_a_especial': 'no',
        }
        lista = lista_modelo.create(datos)
        print('Creado', lista.name)



### Proyectos especiales

lista_diseño = [
    "Copia de las memorias de diseño en extension PDF y/o Archivo de Modelación", "VoBo Geotecnico -según formato de Satisfacción",
    "PDF Y FORMATOS SIG: Anexos (NS-0185)", "FORMATOS CAD: Contiene Planta y Perfiles de toda la red, con información básica",
    "FORMATOS CAD: Líneas proyectadas que se diferencian de las existentes",
    "FORMATOS CAD: Contiene Planos estructurales (planta y cortes)  con información básica"
]

lista_obra = [
    "FORMATOS CAD: Número de proyecto relacionado en la base datos SIGUE",
    "FORMATOS CAD: Líneas recién construidas que se diferencian de las existentes",
    "FORMATOS CAD: Contiene Planta y Perfiles de toda la red, con información básica"
]

listas_obra_diseño = [
    "CAD: Contiene cuadro y/o tablas que indican el diseño y/u obra",
    "CAD: Contiene optimas condiciones de nitidez de la infromacion presentada",
    "FORMATOS CAD Y SIG: Contiene diámetros, longitud, materiales y cotas acorde a lo presentado en cuadros y/o Tablas y/o Plantas y/o SIG (NS-185)",
    "FORMATOS CAD Y SIG: Parámetro de Integridad: coherencia espacial de estos dos con la Ortofoto (NS-185)",
    "FORMATOS SIG: Parámetro de Exactitud temática: coherencia entre las características del elemento y lo que representa.  (NS-185)",
    "FORMATOS SIG: Parámetro de Consistencia: Conectividad Nodos y Líneas - Topologia (NS-185)",
    "FORMATOS SIG: Parámetro de Completitud: Totalidad de atributos (columnas) - (NS-185)",
    "FORMATOS SIG: Parámetro de Validez: Dominios válidos - (NS-185)"
]


 ### Proyectos especiales y Revisión Planos Record Diseño
seccion_id = proyectos_especiales_id[0]
tipo_tramite_id = revision_planos_record_disenio_id[0]

for lista in lista_diseño:
    datos = {
        'name': lista,
        'seccion_id': seccion_id,
        'tipo_tramite_id': tipo_tramite_id,
        'aplica_a_especial': 'no',
    }
    lista = lista_modelo.create(datos)
    print('Creado', lista.name)


 ### Proyectos especiales y Revisión Planos Record Obra
seccion_id = proyectos_especiales_id[0]
tipo_tramite_id = revision_planos_record_obra_id[0]

for lista in lista_obra:
    datos = {
        'name': lista,
        'seccion_id': seccion_id,
        'tipo_tramite_id': tipo_tramite_id,
        'aplica_a_especial': 'no',
    }
    lista = lista_modelo.create(datos)
    print('Creado', lista.name)


### Proyectos especiales y Revisión Planos Record Obra y Diseño
seccion_id = proyectos_especiales_id[0]
tipo_tramite_ids = [revision_planos_record_disenio_id[0], revision_planos_record_obra_id[0]]      # 17 => Revisión Planos Record Diseño, 18 => Revisión Planos Record Obra

for tipo_tramite_id  in tipo_tramite_ids:
    for lista in listas_obra_diseño:
        datos = {
            'name': lista,
            'seccion_id': seccion_id,
            'tipo_tramite_id': tipo_tramite_id,
            'aplica_a_especial': 'no',
        }
        lista = lista_modelo.create(datos)
        print('Creado', lista.name)
