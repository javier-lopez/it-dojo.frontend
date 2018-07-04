from app import app, db, bcrypt
from hashlib  import md5
from datetime import datetime, timedelta

class User(db.Document):
    #username  = db.StringField(required=True, unique=True)
    #first_name= db.StringField(required=True)
    #last_name = db.StringField(required=True)
    #about_me  = db.StringField()
    email      = db.StringField(required=True, unique=True)
    password   = db.StringField(required=True); password_hashed = db.BooleanField(default=False)
    profile    = db.StringField(required=True)
    admin      = db.BooleanField(default=False)

    confirmed     = db.BooleanField(default=False)
    confirmed_on  = db.DateTimeField()
    registered_on = db.DateTimeField(default=datetime.now)

    last_seen     = db.DateTimeField(default=datetime.now)

    def clean(self):
        #clean will be called when you call .save()
        #you can do whatever you want to clean data before save

        #workaround for already hashed password, mongoengine makes difficult to
        #override the __init__ constructor:
        #https://stackoverflow.com/questions/16881624/mongoengine-0-8-0-breaks-my-custom-setter-property-in-models
        if not self.password_hashed:
            self.password        = bcrypt.generate_password_hash(self.password).decode('utf-8')
            self.password_hashed = True

    def is_trial_active(self):
        days_in_trial = datetime.now() - self.confirmed_on
        days_in_trial = days_in_trial.days

        schedule_interviews = list(ScheduleInterview.objects().aggregate(
                {
                    "$match" : { "username": self.email}
                },
                {
                    "$group" : { "_id": {"status": "$status" }, "count": {"$sum":1}}
                },
            ))

        total_interviews = sum( [i["count"] for i in schedule_interviews ] )

        if days_in_trial     >= 30 or \
           total_interviews  >= 20:

            return False
        else:
            return True

    def trial_percent(self):
        schedule_interviews = list(ScheduleInterview.objects().aggregate(
                {
                    "$match" : { "username": self.email}
                },
                {
                    "$group" : { "_id": {"status": "$status" }, "count": {"$sum":1}}
                },
            ))

        days_in_trial = datetime.now() - self.confirmed_on
        days_in_trial = days_in_trial.days
        days_in_trial_percent  = (days_in_trial * 100) / 30

        total_interviews = sum( [i["count"] for i in schedule_interviews ] )
        total_interviews_percent  = (total_interviews * 100) / 10

        result = float ( "{0:.1f}".format( ( total_interviews_percent + days_in_trial_percent ) / 2 ) ) 

        app.logger.debug(result)

        return result


    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def reset_password(self, password):
        self.password        = bcrypt.generate_password_hash(password).decode('utf-8')
        self.password_hashed = True
        return self

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

    @property
    def is_confirmed(self):
        return self.confirmed

    #required for flask-login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
    #finish flask-login requirements



class Interview(db.Document):
    email         = db.StringField()
    uri           = db.ListField(db.DictField())
    template      = db.ListField(db.StringField())
    endpoint      = db.ListField(db.StringField())
    readme        = db.ListField(db.StringField())
    current_page  = db.IntField()
    confirmed     = db.BooleanField(default=False)
    confirmed_on  = db.DateTimeField()
    id_from       = db.StringField(unique=True)
    registered_on = db.DateTimeField(default=datetime.now)
    score_per_test= db.ListField(db.ListField())



class ScheduleInterview(db.Document):
    field     =  db.StringField(required=True)
    username  =  db.StringField(required=True)
    project   =  db.StringField(required=True)
    seniority =  db.StringField(required=True)
    name      =  db.StringField(required=True)
    email     =  db.StringField(required=True)
    city      =  db.StringField(required=True)
    age       =  db.StringField(required=True)
    client    =  db.StringField(required=True)
    salary    =  db.StringField(required=True)
    date      =  db.StringField(required=True)
    time      =  db.StringField(required=True)
    status    =  db.StringField(required=True)
    confirmed =  db.BooleanField(default=False)
    timestamp =  db.DateTimeField(default=datetime.now)
    confirmed_on  = db.DateTimeField()
    score         = db.IntField()


