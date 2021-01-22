from locust import HttpUser, task, between


class AnonUser(HttpUser):

    @task
    def index(self):
        self.client.get('/')

    @task
    def harvest(self):
        self.client.get('/harvest')

    @task
    def orgs(self):
        self.client.get('/organization')

    @task
    def groups(self):
        self.client.get('/group')
