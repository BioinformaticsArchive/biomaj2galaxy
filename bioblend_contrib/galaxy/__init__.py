"""
A base representation of an instance of Galaxy
"""
import base64
import requests
import urlparse
from bioblend.galaxy.client import Client
from bioblend.galaxy import (libraries, histories, workflows, users,
                             genomes, tools, toolshed, config, visual, quotas,
                             groups, datatypes, jobs, forms, ftpfiles)
from bioblend_contrib.galaxy import (datasets, folders, roles, tool_data)
from bioblend.galaxyclient import GalaxyClient


class GalaxyContribInstance(GalaxyClient):
    def __init__(self, url, key=None, email=None, password=None):
        """
        A base representation of an instance of Galaxy, identified by a
        URL and a user's API key.

        After you have created an ``GalaxyInstance`` object, access various
        modules via the class fields (see the source for the most up-to-date
        list): ``libraries``, ``histories``, ``workflows``, ``datasets``,
        and ``users`` are the minimum set supported. For example, to work with
        histories, and get a list of all the user's histories, the following
        should be done::

            from bioblend import galaxy

            gi = galaxy.GalaxyInstance(url='http://127.0.0.1:8000', key='your_api_key')

            hl = gi.histories.get_histories()
            print "List of histories:", hl

        :type url: string
        :param url: A FQDN or IP for a given instance of Galaxy. For example:
                    http://127.0.0.1:8080

        :type key: string
        :param key: User's API key for the given instance of Galaxy, obtained
                    from the user preferences. If a key is not supplied, an
                    email address and password must be and key will
                    automatically be created for the user.

        :type email: string
        :param email: Galaxy e-mail address corresponding to the user.
                      Ignored if key is supplied directly.

        :type password: string
        :param password: Password of Galaxy account corresponding to the above
                         e-mail address. Ignored if key is supplied directly.

        """
        # Make sure the url scheme is defined (otherwise requests will not work)
        if not urlparse.urlparse(url).scheme:
            url = "http://" + url
        # All of Galaxy's API's are rooted at <url>/api so make that the base url
        self.base_url = url
        self.url = urlparse.urljoin(url, 'api')
        # If key supplied use it, otherwise just set email and password and
        # grab users key before first request.
        if key:
            self.__key = key
        else:
            self.__key = None
            self.email = email
            self.password = password
        self.json_headers = {'Content-Type': 'application/json'}
        self.verify = False  # Should SSL verification be done
        self.libraries = libraries.LibraryClient(self)
        self.histories = histories.HistoryClient(self)
        self.workflows = workflows.WorkflowClient(self)
        self.datasets = datasets.DatasetClient(self)
        self.users = users.UserClient(self)
        self.genomes = genomes.GenomeClient(self)
        self.tools = tools.ToolClient(self)
        self.toolShed = toolshed.ToolShedClient(self)
        self.config = config.ConfigClient(self)
        self.visual = visual.VisualClient(self)
        self.quotas = quotas.QuotaClient(self)
        self.groups = groups.GroupsClient(self)
        self.roles = roles.RolesClient(self)
        self.datatypes = datatypes.DatatypesClient(self)
        self.jobs = jobs.JobsClient(self)
        self.forms = forms.FormsClient(self)
        self.ftpfiles = ftpfiles.FTPFilesClient(self)
        self.tool_data = tool_data.ToolDataClient(self)
        self.folders = folders.FoldersClient(self)

    @property
    def key(self):
        if self.__key is None:
            unencoded_credentials = "%s:%s" % (self.email, self.password)
            authorization = base64.b64encode(unencoded_credentials)
            headers = self.json_headers.copy()
            headers["Authorization"] = authorization
            auth_url = "%s/authenticate/baseauth" % self.url
            # make_post_request uses default_params, which uses this and
            # sets wrong headers - so using lower level method.
            r = requests.get(auth_url, verify=self.verify, headers=headers)
            if r.status_code != 200:
                raise Exception("Failed to authenticate user.")
            self.__key = r.json()["api_key"]
        return self.__key

    @property
    def default_params(self):
        return {'key': self.key}

    @property
    def max_get_attempts(self):
        return Client.max_get_retries()

    @max_get_attempts.setter
    def max_get_attempts(self, v):
        Client.set_max_get_retries(v)

    @property
    def get_retry_delay(self):
        return Client.get_retry_delay()

    @get_retry_delay.setter
    def get_retry_delay(self, v):
        Client.set_get_retry_delay(v)

    def __repr__(self):
        """
        A nicer representation of this GalaxyInstance object
        """
        return "GalaxyInstance object for Galaxy at {0}".format(self.base_url)
