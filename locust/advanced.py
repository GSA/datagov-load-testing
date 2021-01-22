import logging
from random import randint, sample, choice
from locust import HttpUser, task


logger = logging.getLogger(__name__)


HOME_WEIGHT = 1777
DATASET_WEIGHT = 43939
DATASETS_WEIGHT = 405
HARVEST_SOURCE_WEIGHT = 3193
HARVEST_SOURCES_WEIGHT = 1
ORGS_WEIGHT = 16
ORG_WEIGHT = 2298
GROUPS_WEIGHT = 5
GROUP_WEIGHT = 1496
API_PACKAGE_SEARCH_WEIGHT = 1273
API_PACKAGE_SHOW_WEIGHT = 1413
API_ORG_LIST_WEIGHT = 1
API_GROUP_LIST_WEIGHT = 1
API_HARVEST_SOURCE_SEARCH_WEIGHT = 1
# ! RESOURCE_WEIGTH = 7177


class AnonApiUser(HttpUser):

    pending_datasets = []
    pending_organizations = []
    pending_groups = []
    pending_harvest_sources = []
    pending_resources = []
    total_datasets = 0

    def on_start(self):
        """ start all queues """
        self.get_total_datasts()
        self.random_dataset()
        self.random_harvest_sources()
        self.random_organizations()
        self.all_groups()

    def get_total_datasts(self):
        if self.total_datasets == 0:
            url = '/api/3/action/package_search?rows=1'
            response = self.client.get(url, name='api-package-search')
            self.total_datasets = response.json()['result']['count']

    @task(API_PACKAGE_SEARCH_WEIGHT)
    def random_dataset(self):

        start = randint(1, self.total_datasets)
        url = f'/api/3/action/package_search?rows=100&start={start}'
        response = self.client.get(url, name='api-package-search')
        try:
            data = response.json()
        except Exception:
            return None
        result = data.get('result', {})
        results = result.get('results', [])
        if len(results) == 0:
            logger.error('No datasets in api search')
            return []
        for result in results:
            name = result.get('name', None)
            if name is None:
                logger.error('No name in datasets')
                continue
            self.pending_datasets.append(name)

    @task(DATASET_WEIGHT)
    def datasets(self):
        name = choice(self.pending_datasets)
        url = f'/dataset/{name}'
        self.client.get(url, name='dataset')

    @task(API_PACKAGE_SHOW_WEIGHT)
    def package_show(self):
        name = choice(self.pending_datasets)
        url = f'/api/3/action/package_show?id={name}'
        self.client.get(url, name='api-package-show')

    @task(API_HARVEST_SOURCE_SEARCH_WEIGHT)
    def random_harvest_sources(self, max_start=900):

        start = randint(1, max_start)
        url = f'/api/3/action/package_search?rows=100&start={start}&q=(type:harvest)&fq=+dataset_type:harvest'
        response = self.client.get(url, name='api-package-search-harvest')
        try:
            data = response.json()
        except Exception:
            return None
        result = data.get('result', {})
        results = result.get('results', [])
        if len(results) == 0:
            return []
        for result in results:
            name = result.get('name', None)
            if name is None:
                continue
            url = f'/harvest/{name}'
            self.pending_harvest_sources.append(url)

    @task(HARVEST_SOURCE_WEIGHT)
    def harvest_sources(self):
        url = choice(self.pending_harvest_sources)
        self.client.get(url, name='harvest-source')

    @task(API_ORG_LIST_WEIGHT)
    def random_organizations(self):

        url = '/api/3/action/organization_list'
        response = self.client.get(url, name='api-organization-list')
        try:
            data = response.json()
        except Exception:
            return None
        results = data.get('result', [])
        # pick just some organizations randmonly
        random_results = sample(results, 5)
        for org in random_results:
            url = f'/organization/{org}'
            self.pending_organizations.append(url)

    @task(ORG_WEIGHT)
    def organization(self):
        url = choice(self.pending_organizations)
        self.client.get(url, name='organization')

    @task(API_GROUP_LIST_WEIGHT)
    def all_groups(self):

        url = '/api/3/action/group_list'
        response = self.client.get(url, name='api-group-list')
        try:
            data = response.json()
        except Exception:
            return None
        results = data.get('result', [])
        # pick just some organizations randmonly
        random_results = sample(results, 5)
        for group in random_results:
            url = f'/group/{group}'
            self.pending_groups.append(url)

    @task(GROUP_WEIGHT)
    def groups(self):
        url = choice(self.pending_groups)
        self.client.get(url, name='group')

    @task(HOME_WEIGHT)
    def index(self):
        self.client.get('/', name='home')

    @task(DATASETS_WEIGHT)
    def dataset_home(self):
        self.client.get('/dataset', name='datasets-home')

    @task(HARVEST_SOURCES_WEIGHT)
    def harvest_sources_home(self):
        self.client.get('/harvest', name='harvest-sources-home')

    @task(ORGS_WEIGHT)
    def organizations_home(self):
        self.client.get('/organization', name='organizations-home')

    @task(GROUPS_WEIGHT)
    def groups_home(self):
        self.client.get('/group', name='groups-home')

    # Avoid resource testing
    # https://github.com/GSA/datagov-deploy/pull/2662
    # @task(RESOURCE_WEIGTH)
    # def random_resources(self, max_start=100):

    #     name_letter = choice(list('aeiouthrslmnb'))
    #     start = randint(1, max_start)
    #     url = f'/api/3/action/resource_search?query=name:{name_letter}&limit=10&offset={start}'
    #     response = self.client.get(url, name='api-resource-search')
    #     try:
    #         data = response.json()
    #     except Exception:
    #         return None
    #     result = data.get('result', {})
    #     results = result.get('results', [])
    #     if len(results) == 0:
    #         return None
    #     for result in results:
    #         package_id = result['package_id']
    #         resource_id = result['id']
    #         url = f'/dataset/{package_id}/resource/{resource_id}'
    #         self.pending_resources.append(url)

    # @task(RESOURCE_WEIGTH)
    # def resources(self):
        # url = choice(self.pending_groups)
        # self.client.get(url, name='resource')
