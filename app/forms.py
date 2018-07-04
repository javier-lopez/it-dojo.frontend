from flask_wtf import FlaskForm
from wtforms   import RadioField, StringField
from wtforms   import PasswordField, BooleanField, SubmitField
from wtforms   import SelectField, DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email       = StringField('Correo',
                  render_kw={"placeholder": "Email Address"},
                  validators=[
                      InputRequired(message="campo requerido"),
                      Email(message='correo inválido'),
                  ])

    password    = PasswordField('Contraseña',
                  render_kw={"placeholder": "Password"},
                  validators=[InputRequired(message="campo requerido")])
    #remember_me = BooleanField('Recordarme')

    submit      = SubmitField('Sign-in')

class PasswordRecoverForm(FlaskForm):
    email  = StringField('Correo',
             validators=[
                 InputRequired(message="campo requerido"),
                 Email(message='correo inválido'),
             ])
    submit = SubmitField('Recover password')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Nueva Contraseña',
               render_kw={"placeholder": "Password"},
               validators=[
                   InputRequired(message="campo requerido"),
                   Length(max=500, message="la contraseña debe ser entre 8 y 500 caracteres"),
                   EqualTo('confirm', message='las contraseñas no coinciden'),
               ])
    confirm  = PasswordField('Repetir contraseña',
               render_kw={"placeholder": "Confirm Password"},
               validators=[
                   InputRequired(message="campo requerido"),
                   Length(max=500, message="la contraseña debe ser entre 8 y 500 caracteres"),
               ])
    submit   = SubmitField('Submit')

class RegisterForm(FlaskForm):
    # username   = StringField('Usuario',
                 # validators=[
                     # InputRequired(message="campo requerido"),
                     # Length(max=32, message="el usuario no puede tener más de 32 caracteres")
                 # ])
    # first_name = StringField('Nombre(s)',
                 # validators=[
                     # InputRequired(message="campo requerido"),
                     # Length(max=32, message="el nombre no puede tener más de 32 caracteres")
                 # ])
    # last_name  = StringField('Apellido(s)',
                 # validators=[
                     # InputRequired(message="campo requerido"),
                     # Length(max=32, message="el apellido no puede tener más de 32 caracteres")
                 # ])
    email      = StringField('Correo',
                 render_kw={"placeholder": "Email"},
                 validators=[
                     InputRequired(message="campo requerido"),
                     Email(message='correo inválido'),
                     Length(max=32, message="el correo no puede tener más de 32 caracteres"),
                 ])
    password   = PasswordField('Contraseña',
                 render_kw={"placeholder": "Password"},
                 validators=[
                     InputRequired(message="campo requerido"),
                     Length(max=500, message="la contraseña debe ser entre 8 y 500 caracteres"),
                     EqualTo('confirm', message='las contraseñas no coinciden'),
                 ])
    confirm    = PasswordField('Repetir contraseña',
                 render_kw={"placeholder": "Confirm Password"},
                 validators=[
                     InputRequired(message="campo requerido"),
                     Length(max=500, message="la contraseña debe ser entre 8 y 500 caracteres"),
                 ])
    profile    = RadioField('Seleccion de Perfil',
                 choices=[
                     ("recruiter","recruiter"),
                     ("recruiter-freelance","recruiter-freelance"),
                     ("learner","learner"),
                 ],
                 default="recruiter",
                 validators=[
                     InputRequired(message="campo requerido"),
                 ])

    accept_tos = BooleanField('checkbox-signup', default=True, validators=[InputRequired(message="campo requerido")])
    submit     = SubmitField('Register')

class ScheduleInterviewForm(FlaskForm):
    field    = RadioField('field',
               choices   =[("DevOps","DevOps"), ("Big Data","Big Data"), ("Web Dev", "Web Dev")],
               validators=[InputRequired(message="campo requerido")],
               )
    project  = StringField('project' ,
               validators=[
                   InputRequired(message='campo requerido'),
                   Length(max=32, message="debe ser entre 8 y 500 caracteres"),
               ])

    seniority= SelectField("seniority",
               choices=[('Junior', 'Junior'),
                        ('Semi-senior', 'Semi-senior'),
                        ('Senior', 'Senior')],
               validators=[
                    InputRequired(message='campo requerido'),
                ])
    name     = StringField('name' ,
               validators=[
                   InputRequired(message='campo requerido'),
                   Length(max=32, message="debe ser entre 8 y 500 caracteres"),
               ])

    email    = StringField('email',
               validators=[
                    InputRequired(message='campo requerido'),
                    Length(max=50, message="debe ser entre 8 y 500 caracteres"),
                    Email(),
               ])

    city_file= 'Aguascalientes\nBaja California\nBaja California Sur\nCampeche\nChiapas\nChihuahua\nCiudad de México\nCoahuila\nColima\nDurango\nGuanajuato\nGuerrero\nHidalgo\nJalisco\nEstado de México\nMichoacán\nMorelos\nNayarit\nNuevo León\nOaxaca\nPuebla\nQuerétaro\nQuintana Roo\nSan Luis Potosí\nSinaloa\nSonora\nTabasco\nTamaulipas\nTlaxcala\nVeracruz\nYucatán\nZacatecas\n'.split('\n')

    city     = SelectField("city",
               choices=[ (str(i),str(i)) for i in city_file if i ],
               validators=[ InputRequired() ],
               )

    age      = SelectField("age", choices=[ (str(i),str(i)) for  i in range(18,80) ] )
    client   = StringField('client', validators=[ InputRequired(message='campo requerido') ])
    salary   = StringField('salary', validators=[ InputRequired(message='campo requerido') ])
    #date    = DateField('fecha examen', format='%m/%d/%Y', validators=[InputRequired(message='campo requerido')])
    date     = StringField( 'date', validators=[ InputRequired(message='campo requerido') ])
    #time    = DateField('hora examen', format='%H:%Mi %p', validators=[InputRequired(message='campo requerido')] )
    time     = StringField('time', validators=[ InputRequired(message='campo requerido') ])
    submit   = SubmitField('submit')

class tst_form(FlaskForm):
    selection = RadioField("selection", validators=[InputRequired()])
    submit    = SubmitField()

class EditForm(FlaskForm):
    email       = StringField('Correo', validators=[
                     InputRequired(message="campo requerido"),
                     Email(message='correo inválido')
                 ])
    password   = PasswordField('Nueva contraseña',
                 validators=[
                     Length(max=500, message="la contraseña debe ser entre 8 y 500 caracteres"),
                     EqualTo('confirm', message='las contraseñas no coinciden')
                 ])
    confirm    = PasswordField('Repetir contraseña',
                 validators=[
                     Length(max=500, message="la contraseña debe ser entre 8 y 500 caracteres"),
                 ])
    # about_me    = StringField('Sobre mi',
                 # validators=[
                     # Length(max=140, message="el campo no puede tener más de 140 caracteres")
                 # ])
    submit     = SubmitField('Guardar')

class SearchForm(FlaskForm):
    search = StringField('Buscar',
             validators=[
                 InputRequired(message="campo requerido"),
                 Length(max=1000, message="el patrón de búsqueda debe ser menor a 1000 caracteres"),
             ])
    submit = SubmitField('Buscar')
