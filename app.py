from flask import Flask
from datetime import datetime
from flask import request, make_response, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField, EmailField, IntegerField
from wtforms.validators import DataRequired, Length, Email,  EqualTo, ValidationError


app = Flask(__name__)
import os
#Ruta de la DB
dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/db.db" #CONECTOR - RUTA ABSOLUTA
app.config['SQLALCHEMY_DATABASE_URI'] = dbdir

db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app,db,render_as_batch=True)
bcrypt 	= Bcrypt(app)


pw_hash = bcrypt.generate_password_hash("SECRET_KEY")
bcrypt.check_password_hash(pw_hash, "SECRET_KEY")
app.config['SECRET_KEY'] = pw_hash
# print(pw_hash)


#MODELOS  *************************************************************************************
#**********************************************************************************************
class User(db.Model):
	#Al agregar un campo hay que migrarlo a la DB y aquí se crean los campos del usuario
	id 					=	db.Column(db.Integer, 		primary_key=True)
	username 			= 	db.Column(db.String(20),	unique=False, 	nullable=False)
	apellidos 			= 	db.Column(db.String(20),	unique=False,	nullable=True)
	apellidos2 			= 	db.Column(db.String(20),	unique=False,	nullable=True)
	residencia 			= 	db.Column(db.String(120),	unique=False,	nullable=True)
	email 				= 	db.Column(db.String(120),	unique=True, 	nullable=False)
	telefono			= 	db.Column(db.String(15),	unique=False, 	nullable=True)
	celular				= 	db.Column(db.String(15),	unique=False, 	nullable=True)
	password 			= 	db.Column(db.String(60),	unique=True, 	nullable=False)
	confirmpassword		= 	db.Column(db.String(60),	unique=True, 	nullable=False)
	imagen_perfil		= 	db.Column(db.String(20),	nullable=False, default="default.jpg")
	date_added			= 	db.Column(db.DateTime,		nullable=False,	default=datetime.utcnow)
	posts 				= 	db.relationship("Post", 	backref="author", 	lazy=True)

	#Al agregar un campo hay que migrarlo a la DB y también agregarlo en esta fila con la misma sintaxis y orden
	def __repr__(self):
		return f"User('{self.username}',{self.apellidos}',{self.apellidos2}','{self.residencia}','{self.email}','{self.telefono}','{self.celular}','{self.password}','{self.confirmpassword}','{self.imagen_perfil}')"
#**********************************************************************************************
#**********************************************************************************************


#FORMULARIO TABLAS LOGIN Y DE REGISTRO ********************************************************
#**********************************************************************************************
class formularioRegistro(FlaskForm):

	# Para agregar un campo a la DB se agrega dentro de este formulario, también 
	# en el modelo y la función _repr_ del modelo, Además del formulario registro 
	# y en  los formularios que se van a representar el campo. luego se migra  el 
	# nuevo campo con los pasos que están aquí mismo en la última línea  comentada
	# llamada migracion en ----RUN----- y en actualizar contactos

	#Estos son los campos que van a crearse al momento de crear la base de datos
 # CAMPOS EN DB			   TIPO DE DATO		NOMBRE DE CAMPO EN HTML Y VALIDACIONES	
	username 			= 	StringField		('username', validators=[DataRequired(), Length(min=3, max=20)]) 
	apellidos 			= 	StringField		('apellidos',) 
	apellidos2 			= 	StringField		('apellidos2',)
	residencia			= 	StringField		('residencia',)
	email 				= 	EmailField		('email', 	validators=[DataRequired(), Email()])
	telefono			= 	IntegerField	('telefono', validators=[Length(min=8, max=15)])
	celular				= 	IntegerField	('celular', validators=[Length(min=8, max=15)])
	password 			= 	PasswordField	('password',validators=[DataRequired(), Length(min=8, max=20)]) 
	confirmpassword 	= 	PasswordField	('confirmpassword',validators=[DataRequired(), EqualTo('password', message='Password No Coincide')], id="confirm")
	submit 				= 	SubmitField		('Registrarme')
#**********************************************************************************************
#**********************************************************************************************


				
	def validate_email(self, email):
		#user es la variable que almacena el primer email de contenido de la db
		user = User.query.filter_by(email.email.data).first()
		#Si la variable o si el email existe
		if user:
			#Advierte que el Email ya fue tomado.
			flash("El email ya fue tomado. Use otro ")


@app.route("/")
@app.route("/home")
@app.route("/index")

def home():
	title = "Home"
	return render_template("index.html", title=title)




if __name__ == "__main__":
	db.create_all()
		# Migraciones Cmder
		# set FLASK_APP=main.py 	<--Crea un directorio de migraciones
		# flask db init 			<--
		# $ flask db stamp head
		# $ flask db migrate
		# $ flask db upgrade
	app.run(debug = True, port = 8181) 



