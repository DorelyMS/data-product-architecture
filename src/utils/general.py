import yaml

def read_yaml(credentials_file):
	"""
	Funcion para leer archivo config
	"""
	with open(credentials_file, "r") as cred:
		res = yaml.safe_load(cred)

	return res

def get_api_token(credentials_file):
	"""
	Funcion para leer token
	"""

	token = read_yaml(credentials_file)['food_inspections']['api_token']

	return token

def get_s3_credentials(credentials_file):
	"""
	Funcion que devuelve credenciales de aws para bucket
	"""

	cred = read_yaml(credentials_file)['s3']

	return cred

def get_db_credentials(credentials_file):
	"""
	Funcion que devuelve credenciales de aws para bucket
	"""

	cred = read_yaml(credentials_file)['db']

	return cred

def type_ing_aux(type_ingesta):
	if type_ingesta == 'historic':
		return 'initial'
	else:
		return 'consecutive'