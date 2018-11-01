from flask import render_template, flash
from flask import redirect, url_for, request
from flask_login import login_required
from flask_login import current_user, login_user, logout_user

from app import app, login_manager, bcrypt
from app.mail   import send_confirmation_email, send_reset_passwd_email, send_test_notification
from app.forms  import LoginForm, RegisterForm, PasswordRecoverForm, PasswordResetForm, EditForm, SearchForm, ScheduleInterviewForm
from app.token  import confirm_token
from app.models import User, ScheduleInterview, Interview
from app.decorators import user_confirmed_required

from base64   import b64decode
from datetime import datetime, timedelta
from markdown import markdown

from app.tty  import score_interview_container, destroy_interview_containers, add_schedule_interview_score

import requests, time, re
#import jsonify

#____________________________________________________[ INDEX ]
@app.route('/index.html', methods=['GET', 'POST'])
def index_html():
    return redirect(url_for('index'))

@app.route('/',      methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    register_form = RegisterForm()
    login_form    = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    return render_template(
        "index.html",
        login_form = login_form,
        current_user=current_user,
        registration_form=register_form,
    )

#____________________________________________________[ LOGIN ]
@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        user = User.objects(email=form.email.data).first()
        if user is None:
            flash('Login failed, "{}" doesn\'t exists'.format(form.email.data))
            return render_template("index.html", login_form=form, registration_form=RegisterForm())
        else:
            if user.check_password(form.password.data):
                login_user(user)
                user.last_seen = datetime.utcnow()
                user.save()
                return redirect(url_for('dashboard'))
            else:
                flash('Login failed, user/password mismatch')
                return redirect(url_for('index'))

    return render_template("index.html", login_form=form, registration_form=RegisterForm())

#____________________________________________________[ LOGOUT ]
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#____________________________________________________[ REGISTER ]
@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    form = RegisterForm()
    login_form = LoginForm()
    #print("[+] _______________________[ registering ]")
    if request.method == 'POST' and form.validate():
        user = User.objects(email=form.email.data).first()
        if user is None:
            new_user = User(
                        email=form.email.data,
                        password=form.password.data,
                        profile=form.profile.data
                        ).save()
            send_confirmation_email(new_user)
            flash('Confirmation email sent to "{0}"'.format(form.email.data))
            login_user(new_user)
            return redirect(url_for('user_unconfirmed'))
        else:
            flash('"{}" email has already been registered'.format(form.email.data))
            #print("[+] _______________________[ user not added ]")
            return render_template('index.html', registration_form=form, login_form=login_form)
    return redirect(url_for('index'))
    #print("[+] _______________________[ something went weird ]")

#____________________________________________________[ UNCONFIRMED ]
@app.route('/user/unconfirmed')
def user_unconfirmed():
    if current_user.confirmed:
        flash('"{0}" has already been confirmed, you can now login'.format(current_user.email))
        return redirect('index')
    return render_template('user_unconfirmed.html')

#____________________________________________________[ CONFIRM TOKEN ]
@app.route('/user/confirm/<token>')
def user_confirm(token):
    email = confirm_token(token)
    if not email:
        flash('Confirmation code is invalid or has expired')
        return redirect(url_for('index'))

    user = User.objects(email=email).first()
    if user.confirmed:
        flash('"{0}" has already been confirmed, you can login now'.format(email))
    else:
        user.confirmed    = True
        user.confirmed_on = datetime.now()
        user.save()
        flash('"{0}" confirmed!, you have full access to IT/DOJO'.format(email))
    return redirect(url_for('dashboard'))

#____________________________________________________[ RESEND ]
@app.route('/user/resend')
@login_required
def user_resend():
    send_confirmation_email(current_user)
    flash('Confirmation email sent to "{0}"'.format(current_user.email))
    return redirect(url_for('user_unconfirmed'))

#____________________________________________________[ RECOVER ]
@app.route('/user/recover', methods=['GET', 'POST'])
def user_recover():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PasswordRecoverForm()
    if request.method == 'POST' and form.validate():
        user = User.objects(email=form.email.data).first()
        if user is None:
            flash('Recovery code sent to "{0}"'.format(form.email.data))
            return redirect(url_for('index'))
        else:
            if user.is_confirmed:
                send_reset_passwd_email(user)
                flash('Recovery code sent to "{0}"'.format(form.email.data))
                return redirect(url_for('index'))
            else:
                flash('"{0}" hasn\'t confirmed its account, please login and verify the account'
                      .format(form.email.data))
                return redirect(url_for('index'))
    return render_template('user_recover.html', title='Account Recovery', recover_form=form)

#____________________________________________________[ RESET TOKEN ]
@app.route('/user/reset/<token>')
def user_reset(token):
    # app.logger.debug('token: {}'.format(token))
    email = confirm_token(token)
    if not email:
        flash('Confirmation code is invalid or has expired')
        return redirect(url_for('user_recover'))

    user = User.objects(email=email).first()
    login_user(user)
    return redirect(url_for('user_reset_password'))

#____________________________________________________[ RESET PASSWORD ]
@app.route('/user/reset', methods=['GET', 'POST'])
@login_required
@user_confirmed_required
def user_reset_password():
    form = PasswordResetForm()
    if request.method == 'POST' and form.validate():
        user = User.objects(id=current_user.id).first()
        user.reset_password(form.password.data).save()
        flash('Account successfully restored!')
        return redirect(url_for('dashboard'))
    return render_template('user_reset_password.html', title='Forgot Password', reset_password_form=form)

#____________________________________________________[ USER EDIT ]
@app.route('/user/edit', methods=['GET', 'POST'])
@login_required
@user_confirmed_required
def user_edit():
    form = EditForm()
    if request.method == 'POST' and form.validate():
        user           = User.objects(id=current_user.id).first()
        #form_username = User.objects(username=form.username.data).first()
        form_email     = User.objects(email=form.email.data).first()

        # if form_username != None and user.id != form_username.id:
            # flash('"{}" has already been registered'.format(form_username))
            # return redirect(url_for('user_edit'))

        if form_email != None and user.id != form_email.id:
            flash('"{}" has already been registered'.format(form_email))
            return redirect(url_for('user_edit'))

        # user.username = form.username.data
        user.email      = form.email.data

        if form.password.data != None:
            user.reset_password(form.password.data)

        user.save()
        flash('Your changes have been saved!')
        return redirect(url_for('user', username=current_user.username))
    else:
        user                 = User.objects(email=current_user.email).first()
        # form.username.data = user.username
        form.email.data      = user.email
        # form.about_me.data = user.about_me

    return render_template('user_edit.html', form=form)

#____________________________________________________[ USER DELETE ]
@app.route('/user/delete', methods=['GET', 'POST'])
@login_required
def user_delete():
    user = User.objects(email=current_user.email).first()
    for product in user.products():
        Product.objects(id=product.id).first().delete()
    user.delete()
    logout_user()
    return redirect(url_for('index'))


#____________________________________________________[ USER PROFILE ]
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.objects(username=username).first()

    if user == None:
        flash('User "{}" not found.'.format(username))
        return redirect(url_for('index'))
    return render_template('user.html', user=user)


#____________________________________________________[ DASHBOARD ]
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
@user_confirmed_required
def dashboard():
    title="Dashboard"

    #__________[ modal validation ]
    reset_form = PasswordResetForm()
    if request.method == 'POST' and reset_form.validate():
        user = User.objects(id=current_user.id).first()
        user.reset_password(form.password.data).save()
        flash('Account successfully restored')
        return redirect(url_for('dashboard'))

    if request.method == 'POST': # and request.form.get('delete') == 'delete':

        query_values = request.form.get("delete").split(",")
        query_values = [i for i in query_values if i]
        app.logger.debug(query_values)
        name, project, seniority, client, city, age, date, sal, x = query_values

        table = ScheduleInterview.objects(name=str(name),project=str(project),seniority=str(seniority),client=str(client),city=str(city),age=str(age),date=str(date), salary=str(sal)).first()
        app.logger.debug(table)
        table.delete()

        #app.logger.debug(request.data)
        #app.logger.debug("delete")
        app.logger.debug(query_values)

    #__________________[ vars ]
    schedule_interviews = list(ScheduleInterview.objects().aggregate(
        {
            "$match" : { "username": current_user.email}
        },
        {
            "$group" : { "_id": {"status": "$status" }, "count": {"$sum":1}}
        },
    ))
    #app.logger.debug("schedule_interviews: {}".format(schedule_interviews))

    user = User.objects(id=current_user.id).first()
    user_data = {
        "email"     : current_user.email,
        "license"   : current_user.profile,
        "sucessfull": sum( [i["count"] for i in schedule_interviews if "done"    in i["_id"]["status"] ] ),
        "pending"   : sum( [i["count"] for i in schedule_interviews if "pending" in i["_id"]["status"] ] ),
        "overall"   : sum( [i["count"] for i in schedule_interviews ] ),
        "week"      : 0,
        "month"     : 0,
        "trial"     : user.trial_percent(),
        "avatar"    : user.avatar(133)
    }
    #app.logger.debug("user_data: {}".format(user_data))

    #__________________[ col1_data ]
    #pie chart
    pie_chart = list(ScheduleInterview.objects().aggregate(
        {
            "$match": {"username": current_user.email }
        },
        {
            "$group" : { "_id" : { "field": "$field" }, "count": {"$sum":1}}
        },
    ))
    #app.logger.debug("pie_chart: {}".format(pie_chart))

    pie_chart_data = []
    for i in pie_chart:
        pie_chart_data.append( {"label":i["_id"]["field"], "value" : i["count"]})

    #app.logger.debug('pie_chart_data: {}'.format(pie_chart_data))

    #_________________[ col2_data ]
    table_pending_interviews = ScheduleInterview.objects(username=current_user.email, status="pending")

    return render_template(
        "dashboard.html",
        title=title,
        user_data=user_data,
        table_pending_interviews=table_pending_interviews,
        pie_chart_data=pie_chart_data,
        reset_password_form=reset_form,
    )



#____________________________________________________[ SCORES ]
@app.route("/scores")
@login_required
@user_confirmed_required
def scores():
    title="Scores"

    projects     = ScheduleInterview.objects(username=current_user.email).distinct("client")
    projects     = sorted( list( set( [i.lower().capitalize() for i in projects] ) ) )
    table_info   = ScheduleInterview.objects(username=current_user.email)
    project_list = ScheduleInterview.objects()

    return render_template(
        "scores.html",
        title=title,
        user_info=table_info,
        project_info=projects,
    )



#____________________________________________________[ SCHEDULE INTERVIEW ]
@app.route("/schedule/interview", methods=['GET', 'POST'])
@login_required
@user_confirmed_required
def schedule_interview():
    title="Schedule Interview"
    form =ScheduleInterviewForm()

    #step2
    regex1 = '(^\s*|\s*$|[\s]{1,})'
    if request.method == 'POST' and form.validate():
        new_schedule_interview = ScheduleInterview(
           username  = re.sub(regex1, " ", current_user.email) .strip(),
           field     = re.sub(regex1, " ", form.field.data)    .strip(),
           project   = re.sub(regex1, " ", form.project.data)  .strip(),
           seniority = re.sub(regex1, " ", form.seniority.data).strip(),
           name      = re.sub(regex1, " ", form.name.data)     .strip(),
           email     = re.sub(regex1, " ", form.email.data)    .strip(),
           city      = re.sub(regex1, " ", form.city.data)     .strip(),
           age       = re.sub(regex1, " ", form.age.data)      .strip(),
           client    = re.sub(regex1, " ", form.client.data)   .strip(),
           salary    = re.sub(regex1, " ", form.salary.data)   .strip(),
           date      = re.sub(regex1, " ", form.date.data)     .strip(),
           time      = re.sub(regex1, " ", form.time.data)     .strip(),
           status    = re.sub(regex1, " ", "pending")          .strip(),
           confirmed = False
        ).save()

        #app.logger.debug("sending notification")
        send_test_notification(new_schedule_interview)
        return redirect(url_for('dashboard'))

    app.logger.debug("form.errors: {}".format(form.errors))
    return render_template("schedule_interview.html", title=title, form=form)



#____________________________________________________[ APPLICANT_CONFIRM & MAIN TEST ]
@app.route('/applicant/interview/<token>', methods=["POST", "GET"])
def test_confirm(token):
    title = "Applicant Interview"
    id    = confirm_token(token)

    if not id:
        flash('Confirmation code is invalid or has expired')
        return redirect(url_for('index'))

    schedule_interview = ScheduleInterview.objects(id=id).first()
    app.logger.debug(schedule_interview)

    try:
        if schedule_interview["status"] == "done":
            return redirect(url_for('index'))
    except Exception:
        return redirect(url_for('index'))

    #validate date
    now = datetime.now().strftime("%s")
    scheduled_date = "{}-{}".format(schedule_interview["date"],schedule_interview["time"])
    scheduled_date0= datetime.strptime(scheduled_date, "%m/%d/%Y-%I:%M %p")
    scheduled_date1= scheduled_date0 + timedelta(hours = 1)

    app.logger.debug(now)
    app.logger.debug("{} {}".format(scheduled_date0.strftime("%s"),\
                                    scheduled_date1.strftime("%s")))

    if int(now) >= int(scheduled_date0.strftime("%s")) or \
       int(now) <= int(scheduled_date1.strftime("%s")) : #or True:

        try:
            cache = Interview.objects(id_from=id).first()
        except Exception as ex:
            pass

        if cache:
            #move effect
            obj            = {}
            obj["uri"]     = cache.uri
            obj["template"]= cache.template
            obj["readme"]  = cache.readme
            obj["current"] = cache.current_page
            obj["endpoint"]= cache.endpoint

            app.logger.debug(obj)
            #app.logger.debug(list(cache))


            #___________________________________________[ buttons ]
            if request.method == 'POST':
                #___________________________[ next ]
                if request.form.get("plus") == "+" and  cache.current_page < len(obj["uri"])-1 :
                    cache.current_page = cache.current_page + 1


                #___________________________[ prev ]
                if request.form.get("minus") == "-" and cache.current_page > 0:
                    cache.current_page = cache.current_page - 1


                #___________________________[ test ]
                if request.form.get("test") == "test":
                    #run test
                    #app.logger.debug("obj_endpoint {}".format( obj["endpoint"][obj["current"]]) )

                    #obj["score"] = score_interview_container(obj["endpoint"][obj["current"]])

                    #app.logger.debug("post {}".format("test"))
                    #app.logger.debug("post {}".format(obj["score"] ))
                    return render_template("interview.html", title=title, obj=obj)


                #___________________________[ save ]
                if request.form.get("save") == "save":

                    app.logger.debug("post {}".format("save"))
                    #get score
                    score_interview_container(obj["endpoint"], id)

                    #destroy containers
                    destroy_interview_containers(obj["endpoint"], id)

                    # add scores to scheduleinterview
                    add_schedule_interview_score(id)

                    schedule_interview.status = "done"
                    schedule_interview.save()

                    #redirect
                    return redirect(url_for("index"))


                #saving against button change
                cache.save()
                cache = Interview.objects(id_from=id).first()
                obj["current"] = cache.current_page

            return render_template("interview.html", title=title, obj=obj)
            #app.logger.debug("cache uri: {}".format( cache.uri ) )
            #app.logger.debug("cache readme: {}".format( cache.readme ) )
            #return render_template("interview.html", title=title, uri=cache.uri[0], readme=cache.readme[0])

        if schedule_interview and schedule_interview.confirmed:
            flash('"{0}" is currently doing the assigned exam'.format(schedule_interview.email))
        else:
            #updating db
            schedule_interview.confirmed    = True
            schedule_interview.confirmed_on = datetime.now()
            schedule_interview.status       = "pending" #move to "in-progress"
            schedule_interview.save()

            flash('"{0}" is currently doing the assigned exam'.format(schedule_interview.email))
        #return redirect(url_for('interview'))

            field = schedule_interview.field
            field = field.lower()
            app.logger.debug("field: {}".format(field))

            tasks = requests.get(
                'https://api.' + app.config['APP_DOMAIN'] + '/v0.1/tty/env/' + field,
                verify=False,
                auth=('key', app.config['API_KEY']),
            )

            app.logger.debug("tasks: {}".format(tasks.json()))

            #initialize envs
            data_env = {"readme"   : [], "uri"      : [], \
                        "endpoint" : [], "template" : []
            }
            for env in tasks.json()["env"]:

                res = requests.post(
                          'https://api.' + app.config['APP_DOMAIN'] + '/v0.1/tty',
                          verify=False,
                          auth=('key', app.config['API_KEY']),
                          json={"username": schedule_interview.email, "template": field + "/" + env }
                      )


                if res.ok:
                    app.logger.debug("res: {}".format(res.json()))

                    data    = res.json()
                    uri     = data['tty']['uri']
                    template= data['tty']['template']
                    endpoint= data['tty']['endpoint']
                    readme  = data['tty']['readme']
                    readme  = b64decode(readme)
                    readme  = markdown(readme.decode("utf-8"))

                    app.logger.debug("endpoint {}".format(endpoint))

                    data_env["uri"]     .append(uri)
                    data_env["readme"]  .append(readme)
                    data_env["endpoint"].append(endpoint)
                    data_env["template"].append(template)

                    app.logger.debug('uri: {}'.format(uri))
                    app.logger.debug('readme: {}'.format(readme))
                    app.logger.debug('data_env: {}'.format(data_env["uri"]))

                    response = requests.get('http://' + uri["tty"])
                    counter  = 0
                    while not response.status_code == requests.codes.ok:
                        time.sleep(1)
                        counter += 1
                        app.logger.debug("Waiting %ss for %s ...", counter, uri["tty"])
                        response = requests.get('http://' + uri["tty"])
            #endfor

            schedule_interview = ScheduleInterview.objects(id=id).first()
            app.logger.debug("data_env: {}".format(data_env))
            app.logger.debug("schedule_interview: {}".format(list(schedule_interview)))

            session_cache = Interview(
                email        = schedule_interview.email,
                confirmed    = schedule_interview.confirmed,
                confirmed_on = schedule_interview.confirmed_on,
                id_from      = id,
                uri          = data_env["uri"],
                template     = data_env["template"],
                endpoint     = data_env["endpoint"],
                readme       = data_env["readme"],
                current_page = 0,
            ).save()

            obj = {}
            obj["uri"]     = data_env["uri"]
            obj["readme"]  = data_env["readme"]
            obj["endpoint"]= data_env["endpoint"]
            obj["current"] = int(0)

            app.logger.debug("obj: {}".format(obj))

            return render_template(
                "interview.html",
                title=title,
                obj=obj,
            )



#____________________________________________________[ TEST TRAVIS LIKE ]
@app.route("/test-travis-like")
@login_required
@user_confirmed_required
def test_travis_like():
    request = requests.post(
              'https://api.' + app.config['APP_DOMAIN'] + '/v0.2/tty',
              verify=False,
              auth=('key', app.config['API_KEY']),
              json={
                  "username" : "foobar@" + app.config['APP_DOMAIN'],
                  "repo"     : "https://user:passwd@github.com/it-dojo/user.sample.test.git",
                  "action"   : "init",
              },
          )

    if request.ok:
        app.logger.debug(request.json())
        data = request.json()
        app.logger.debug(data['tty']['uri'])

        response = requests.get('http://' + data['tty']['uri'])
        counter  = 0
        while not response.status_code == requests.codes.ok:
            time.sleep(1)
            counter += 1
            app.logger.debug("Waiting %ss for %s ...", counter, data['tty']['uri'])
            response = requests.get('http://' + data['tty']['uri'])

    return render_template("test-travis-like.html",
                           title="Test Travis Like Interface",
                           uri=data['tty']['uri'],
                           instructions=data['tty']['readme'])



#____________________________________________________[ INVOICE ]
@login_required
@user_confirmed_required
@app.route("/invoice", methods=['GET'])
def invoice():
    title = "Invoice"
    return render_template("invoice.html", title=title)





#____________________________________________________[ DUMMY ENDPOINT ]
@app.route("/tst", methods=['GET', 'POST'])
def tst():
    #title = "tst"
    from app.static.txt import estados

    app.logger.debug(estados)

    return render_template("tst.html" , estados=estados)



#____________________________________________________[ ABOUT ]
@app.route("/about", methods=["GET"] )
def about():
        return render_template("landing.html")



#____________________________________________________[ EXCEPTION ]
# @app.route('/exception')
# def error():
    # raise Exception("I'm sorry, Dave. I'm afraid I can't do that.")



#____________________________________________________[ 401 ]
@app.errorhandler(401)
def not_found_error(error):
    return render_template('401.html'), 401

#____________________________________________________[ 404 ]
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

#____________________________________________________[ 500 ]
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
