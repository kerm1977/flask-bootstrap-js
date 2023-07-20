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
	# posts 				= 	db.relationship("Post", 	backref="author", 	lazy=True)

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

	def validate_email(self, email):
		#user es la variable que almacena el primer email de contenido de la db
		user = User.query.filter_by(email.email.data).first()
		#Si la variable o si el email existe
		if user:
			#Advierte que el Email ya fue tomado.
			flash("El email ya fue tomado. Use otro ")


class formularioLogin(FlaskForm):
 # CAMPOS EN DB			   TIPO DE DATO		NOMBRE DE CAMPO EN HTML Y VALIDACIONES
	email 				= 	StringField		('email', validators=[DataRequired(), Email()])
	password 			= 	PasswordField	('password', validators=[DataRequired()]) 
	rememberme 			= 	BooleanField	('checkbox')
	submit 				= 	SubmitField		('Ingresar')
#**********************************************************************************************
#**********************************************************************************************








#VIEWS  ***************************************************************************************
#**********************************************************************************************

@app.route("/")
@app.route("/home")
@app.route("/index")

def home():
	title = "Home"
	return render_template("index.html", title=title)

@app.route("/dashboard")
def dashboard():
	title = "Dashboard"
	return render_template("dashboard.html", title=title)

# LISTA DE CONTACTOS
@app.route("/contacts")
def contacts():
	values=User.query.all()
	users= len(values)
	titulo = "Inicio"
	return render_template("contacts.html", vtitulo=titulo, values=values, users=users)

# FORMULARIO DE LOGIN
@app.route("/login", methods=["GET","POST"]) 
def login():
	titulo="Login"
	form = formularioLogin()


	if request.method == "POST":
		user = User.query.filter_by(email=form.email.data.lower()).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			flash(f"Hola {user.username.upper()}", "alert-primary")
			return redirect("home")
		flash("Contraseña o Usuario invalidos", "danger")
	return render_template("login.html", vtitulo=titulo, form=form)

# FORMULARIO DE REGISTRO
@app.route("/registro", methods=["GET","POST"]) 
def registro():
	titulo="Registro"
	form = formularioRegistro()


	if request.method == "POST":
		username = User.query.filter_by(username=request.form["username"]).first()
		email = User.query.filter_by(email=request.form["email"]).first()
		
		if {form.password.data} != {form.confirmpassword.data}:
			flash(f"La contraseña y la verificación NO son iguales", "danger")
		elif email:
			flash("""Email ya existen. intente con otro""", "warning")
		else:
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
	

			# CADA CAMBIO QUE SE REALICE EN FLASKFORM Y DB.MODELS HAY QUE ELIMINARLO O AGREGARLO AQUI	
			user = User(
				username 			=		form.username.data.title(), 
				apellidos			=		form.apellidos.data.title(),
				apellidos2			=		form.apellidos2.data.title(),
				residencia			=		form.residencia.data,
				email 				=		form.email.data.lower(), 
				telefono			=		form.telefono.data,
				celular				=		form.celular.data,
				password 			=		hashed_password, 
				confirmpassword 	=		hashed_password
				#  nombre			= 			campo
				)

			db.session.add(user)
			db.session.commit()
			flash(f"Cuenta creada por {form.username.data.upper()} {form.apellidos.data.upper()}", "success")
			return redirect(url_for("login"))
	return render_template("registro.html", vtitulo=titulo, form=form)

# ACTUALIZAR CONTACTOS
@app.route("/update/<int:id>", methods=["GET","POST"])
def update(id):
	form = formularioRegistro()
	values=User.query.all()
	users= len(values)
	actualizar_registro = User.query.get_or_404(id)
	if request.method == "POST":
		
		actualizar_registro.username = request.form["username"]
		actualizar_registro.apellidos = request.form["apellidos"]
		actualizar_registro.apellidos2 = request.form["apellidos2"]
		actualizar_registro.residencia = request.form["residencia"]
		actualizar_registro.email = request.form["email"]
		actualizar_registro.telefono = request.form["telefono"]
		actualizar_registro.celular = request.form["celular"]
		
		try:
			db.session.commit()
			flash(f"{form.username.data.title()} {form.apellidos.data.title()} {form.apellidos2.data.title()} ha sido modificad@", "success")
			return render_template("contacts.html", form=form, actualizar_registro=actualizar_registro, values=values, users=users)
		except:
			db.session.commit()
			flash("Hubo un error al intentar modificar el registro", "warning")
			return render_template("update.html", form=form, actualizar_registro=actualizar_registro)
	else:
		return render_template("update.html", form=form, actualizar_registro=actualizar_registro)

# BORRAR CONTACTOS
@app.route("/delete/<int:id>")
def delete(id):
	id_delete=id
	borrar_registro = User.query.get_or_404(id)

	try:
		db.session.delete(borrar_registro)
		db.session.commit()
		flash(f"El usuario fué Eliminado", "warning")
		return redirect(url_for("contacts"))
		return render_template("contacts.html", borrar_registro = borrar_registro)
	except:
		db.session.commit()
		flash("Hubo un error al intentar borrar este registro", "danger")
		return render_template("contacts.html", borrar_registro=borrar_registro, id_delete=id_delete)
	else:
		return render_template("contacts.html")
	

# ALERTA DE ERRORES
# Error URL Invalida
@app.errorhandler(404)
def pagina_no_encontrada(e):
	titulo = "404"
	return render_template("404.html", vtitulo=titulo), 404

# Error Servidor Interno
@app.errorhandler(500)
def Error_Server(e):
	titulo = "500"
	return render_template("500.html", vtitulo=titulo), 500

#**********************************************************************************************
#**********************************************************************************************








#RUN*******************************************************************************************
#**********************************************************************************************
if __name__ == "__main__":
	db.create_all()
	# db.upgrade_all()
	# db.drop_all()	#Solo se ejecuta para migrar nuevos campos a la db pero borra el contenido
	app.run(debug = True, port = 81) 

	# Migraciones Cmder
		# set FLASK_APP=main.py 	<--Crea un directorio de migraciones
		# flask db init 			<--
		# $ flask db stamp head
		# $ flask db migrate
		# $ flask db upgrade
#**********************************************************************************************
#**********************************************************************************************						
