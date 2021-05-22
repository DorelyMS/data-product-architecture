from flask import Flask
from flask import jsonify
from flask_restplus import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
 
from datetime import datetime
import src.utils.general as general
from src.utils.constants import PATH_CREDENCIALES

# Coneccion a db
db_conn = general.get_db_conn_sql_alchemy(PATH_CREDENCIALES)

# Se crea flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn
api = Api(app)

db = SQLAlchemy(app)

# # Con parámetro
# @app.route('/user/<string:username>')
# def show_user_profile(username):
#     return "Hello user {}".format(username)

# # Con parametro regresa json
# @app.route('/test_json/<string:nombre>')
# def test_json(nombre):
# 	return jsonify(nombre)

class Match(db.Model):
	__table_args__ = {'schema': 'pred'}
	# Cambiar a tabla para la api, donde viene establecimiento único
	__tablename__ = 'predicciones'

	# Cambiar a establecimiento
	inspection_id = db.Column(db.Integer, primary_key = True)
	license_num = db.Column(db.Integer)
	inspection_date = db.Column(db.Date)
	score_1 = db.Column(db.Float)
	predict = db.Column(db.Integer)

model_1 = api.model("match_establecimiento",
	{
	'license_num': fields.Integer,
	'score_1': fields.Float,
	'predict': fields.Integer
	})

model_2 = api.model("match_fecha",
	{
	'inspection_date': fields.Date,
	'inspecciones': fields.Nested(model_1)
	})


@api.route('/')
class HelloWorld(Resource):
	def get(self):
		return "Hello world!"

@api.route('/cliente/<int:id_cliente>')
class Cliente(Resource):
	def get(self, id_cliente):
		return 'El id cliente es {}'.format(id_cliente)

@api.route('/test_json/<nombre>')
class TestJson(Resource):
	def get(self, nombre):
		return nombre

@api.route('/establecimiento/<int:license_num>')
class ResultadoEstablecimiento(Resource):

	@api.marshal_with(model_1)
	def get(self, license_num):
		match = Match.query.filter_by(license_num=license_num).\
		order_by(Match.inspection_id.desc()).limit(1).all()

		return match #{'inspection_id': inspection_id,  'prediccion': match}

@api.route('/fecha/<inspection_date>')
class ResultadoFecha(Resource):

	@api.marshal_with(model_2, as_list=True)
	def get(self, inspection_date):
		filter_date = datetime.strptime(inspection_date, "%Y-%m-%d").date()
		match = Match.query.filter(Match.inspection_date==filter_date).limit(5).all()
		inspecciones = []
		for element in match:
			inspecciones.append({
				'license_num': element.license_num,
				'score_1': element.score_1,
				'predict': element.predict})

		return {'inspection_date': inspection_date,  'inspecciones': inspecciones}


if __name__=='__main__':
	app.run(debug=True)