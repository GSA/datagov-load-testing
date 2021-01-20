from random import randint, sample, choice
from locust import HttpUser, task, between


class AnonUser(HttpUser):
    wait_time = between(1, 2)

    def random_dataset(self, max_start=100000):

        start = randint(1, max_start)
        url = f'/api/3/action/package_search?rows=100&start={start}'
        response = self.client.get(url, name='api-package-search')
        try:
            data = response.json()
        except Exception:
            return None
        result = data.get('result', {})
        results = result.get('results', [])
        if len(results) == 0:
            return None
        for result in results:
            name = results[0].get('name', None)
            if name is None:
                continue
            url = f'/dataset/{name}'
            self.client.get(url, name='dataset')

    @task
    def datasets(self):
        self.random_dataset()

    def random_harvest_source(self, max_start=900):

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
            return None
        for result in results:
            name = results[0].get('name', None)
            if name is None:
                continue
            url = f'/harvest/{name}'
            self.client.get(url, name='harvest-source')

    @task
    def harvest_sources(self):
        self.random_harvest_source()

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
            self.client.get(url, name='organization')

    @task
    def organizations(self):
        self.random_organizations()

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
            self.client.get(url, name='group')

    @task
    def groups(self):
        self.all_groups()

    @task
    def index(self):
        self.client.get('/', name='home')

    @task
    def dataset_home(self):
        self.client.get('/dataset', name='datasets-home')

    @task
    def harvest_sources_home(self):
        self.client.get('/harvest', name='harvest-sources-home')

    @task
    def organizations_home(self):
        self.client.get('/organization', name='organizations-home')

    @task
    def groups_home(self):
        self.client.get('/group', name='groups-home')

    def random_resources(self, max_start=100):

        name_letter = choice(list('aeiouthrslmnb'))
        start = randint(1, max_start)
        url = f'/api/3/action/resource_search?query=name:{name_letter}&limit=10&offset={start}'
        response = self.client.get(url, name='api-resource-search')
        try:
            data = response.json()
        except Exception:
            return None
        result = data.get('result', {})
        results = result.get('results', [])
        if len(results) == 0:
            return None
        for result in results:
            package_id = result['package_id']
            resource_id = result['id']
            url = f'/dataset/{package_id}/resource/{resource_id}'
            self.client.get(url, name='resource')

            # also, try to download
            download_url = result.get('url')
            self.client.get(download_url, name='resource-download')

    @task
    def resources(self):
        self.random_resources()
