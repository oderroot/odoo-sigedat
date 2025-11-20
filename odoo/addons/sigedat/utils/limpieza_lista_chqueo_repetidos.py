from collections import defaultdict
import erppeek

# Connect to an Odoo instance
odoo = erppeek.Client(
    'http://localhost:8015',  # Odoo server URL
    'odoo_v15',        # Database name
    'admin',        # Odoo username
    'admin'         # Odoo password
)


lista_chequeo_model = odoo.model('sigedat.lista_chequeo')
lista_chequeo_item_model = odoo.model('sigedat.lista_chequeo.item')

for tramite_abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra', 'revision_topografia']:
	# listas de chequeo de revision_planos_record_disenio:
	lista_chequeo_revision_planos_record_disenio_ids = lista_chequeo_model.search([('tipo_tramite_id.abreviatura','=',tramite_abreviatura)])
	records = lista_chequeo_model.browse(lista_chequeo_revision_planos_record_disenio_ids)


	# 3. Agrupar por (seccion_id.abreviatura, name)
	grupo = defaultdict(list)
	for rec in records:
	    abrev = rec.seccion_id.abreviatura if rec.seccion_id else '(sin sección)'
	    grupo[(abrev, rec.name)].append(rec)

	# print(f'Grupo: {grupo}')

	# 4. Filtrar solo los grupos con más de un registro
	duplicados = {k: v for k, v in grupo.items() if len(v) > 1}


	# 5. Generar la lista de registros a eliminar (todos menos el primero de cada grupo)
	recs_a_eliminar = []
	for (abrev, name), recs in duplicados.items():
	    # Ordenar los registros para que el primero sea el más antiguo (o el que quieras conservar)
	    recs_sorted = sorted(recs, key=lambda r: r.id)
	    # Tomar todos menos el primero
	    recs_a_eliminar.extend(recs_sorted[1:])



	# 6. Mostrar resultados
	print("=== Registros que se conservarán (primer registro de cada grupo) ===")
	for (abrev, name), recs in duplicados.items():
	    recs_sorted = sorted(recs, key=lambda r: r.id)
	    conservar = recs_sorted[0]
	    print(f"ID: {conservar.id}, Sección: {abrev}, Nombre: {name}")

	print("\n=== Registros a eliminar ===")
	for rec in recs_a_eliminar:
	    print(f"ID: {rec.id}, Sección: {rec.seccion_id.abreviatura if rec.seccion_id else '(sin sección)'}, Nombre: {rec.name}")
	    items = lista_chequeo_item_model.browse([('lista_chequeo_id','=',rec.id)])
	    print(f'lista: {rec.name}, items: {items}')
	    items.unlink(None)
	    rec.unlink(None)

