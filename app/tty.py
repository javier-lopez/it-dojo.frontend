from app            import app
from app.decorators import async
from app.models     import ScheduleInterview, Interview

import requests


@async
def async_test_container(app, interview_data, id_, test_file="/test"):
    """
    interview_data need to be a list
    """
    with app.app_context():
        #run test per container
        #if test one container
        #app.logger.debug(type(interview_data))

        data = Interview.objects(id_from=id_).first()

        result = { }

        counter = 0
        for endpoint in interview_data:
            result[endpoint] = [ requests.get(
                endpoint + test_file,
                verify=False,
                headers={"Content-Type" : "application/json"},
                auth=('admin', 'admin'),
                ) ]

            result[endpoint].append(data["template"][counter])
            counter += 1

        #result = sum([ (int(v.json()["result"])) for k,v in result.items() ])
        result = [ (k,[v[1],v[0].json()["result"] ]) for k,v in result.items() ]
        result = {k:v for k,v in result}

        data.score_per_test = list(result.values())
        data.save()

        app.logger.debug(result)

        return result


@async
def async_destroy_container(app, interview_data, id_):
    """
    interview_data need to be a list
    """
    with app.app_context():
        #if not type(interview_data) == list:
        #   interview_data = [interview_data]
        data = Interview.objects(id_from=id_).first()

        while True:

            data = Interview.objects(id_from=id_).first()
            if data.score_per_test:

                for endpoint in interview_data:
                    #app.logger.debug("post {}".format("save " + str(i["tty"]) ))
                    requests.delete(
                        endpoint,
                        verify=False,
                        auth=('admin', 'admin'),
                    )


                app.logger.debug("destroyed")

                data.uri      = []
                data.endpoint = []
                data.save()

                break


@async
def async_add_score(app, id):
    """
    interview_data need to be a list
    """
    with app.app_context():
        #if not type(interview_data) == list:
        #   interview_data = [interview_data]
        while True:

            data = Interview.objects(id_from=id).first()

            if data["score_per_test"]:
                data_schedule_interview = ScheduleInterview.objects(id=id).first()

                total = sum([int(i[1]) for i in data.score_per_test])

                data_schedule_interview.score = total
                data_schedule_interview.save()




def score_interview_container(interview_data, id):
    """ 'test_file=' optional in case need it"""
    """ interview_data need to be a list     """
    return async_test_container(app, interview_data, id)


def destroy_interview_containers(interview_data, id):
   """ 'test_file=' optional in case need it"""
   """ interview_data need to be a list     """

   return async_destroy_container(app, interview_data, id)


def add_schedule_interview_score(id):
   """ 'test_file=' optional in case need it"""
   """ interview_data need to be a list     """

   return async_add_score(app,id)


