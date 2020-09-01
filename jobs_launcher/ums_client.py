import json
from requests.auth import HTTPBasicAuth
from requests import get, post, put
from requests.exceptions import RequestException
from core.config import main_logger
import traceback


def str2bool(v):
    v = str(v)
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'None'):
        return False
    else:
        raise ValueError('Boolean value expected. Got <{}>'.format(v))


class UMS_Client:
    def __init__(
        self,
        build_id,
        suite_id,
        job_id,
        url,
        env_label,
        login,
        password
    ):
        # TODO: in thread loading schema from api
        self.job_id = job_id
        self.url = url
        self.build_id = build_id
        self.env_label = env_label
        self.suite_id = suite_id
        self.headers = None
        self.token = None
        self.login = login
        self.password = password

        # auth
        self.get_token()

    def get_token(self):
        main_logger.info('Try to get auth token')
        response = post(
            url="{url}/user/login".format(url=self.url),
            auth=HTTPBasicAuth(self.login, self.password),
        )
        response_content = json.loads(response.content.decode("utf-8"))
        if 'token' not in response_content:
            raise RequestException('Check login and password')
        token = response_content["token"]
        self.token = token
        self.headers = {"Authorization": "Bearer " + token}

        main_logger.info("Got auth token")


    def get_suite_id_by_name(self, suite_name):
        try:
            response = get(url="{url}/api/build?id={build_id}&jobId={job_id}".format(
                    url=self.url,
                    build_id=self.build_id,
                    job_id=self.job_id
                ),
                headers=self.headers
            )
            main_logger.info("Get suite id by name {}".format(suite_name))
            suites = [el['suite'] for el in json.loads(response.content.decode("utf-8"))['suites'] if el['suite']['name'] == suite_name]
            self.suite_id = suites[0]['_id']

        except Exception as e:
            self.suite_id = None
            main_logger.error("Suite id getting error")
            main_logger.error(str(e))
            main_logger.error("Traceback: {}".format(traceback.format_exc()))


    def send_test_suite(self, res, env):
        try:
            data = {
                "test_cases_results": res,
                "environment": env,
                "env_label": self.env_label
            }
            response = post(
                headers=self.headers,
                json=data,
                url="{url}/api/testSuiteResult?jobId={job_id}&buildId={build_id}&suiteId={suite_id}".format(
                    url=self.url,
                    build_id=self.build_id,
                    suite_id=self.suite_id,
                    job_id=self.job_id
                )
            )
            main_logger.info('Test suite result sent with code {}'.format(response.status_code))

            return response

        except Exception as e:
            main_logger.error("Test suite result send error: {}".format(str(e)))
            main_logger.error("Traceback: {}".format(traceback.format_exc()))

    def define_environment(self, env):
        try:
            data = {
                "env_label": self.env_label,
                "environment": env
            }
            response = put(
                headers=self.headers,
                json=data,
                url="{url}/api/testSuiteResult?jobId={job_id}&buildId={build_id}&suiteId={suite_id}".format(
                    url=self.url,
                    build_id=self.build_id,
                    suite_id=self.suite_id,
                    job_id=self.job_id
                )
            )
            main_logger.info("Environment defined with code {}".format(response.status_code))
            return response

        except Exception as e:
            main_logger.error("Environment definition error: {}".format(str(e)))
            main_logger.error("Traceback: {}".format(traceback.format_exc()))