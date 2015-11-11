from pymarketo.api import MarketoConnection
from pymarketo.exceptions import InvalidCookieException


class MarketoClientBase(object):
    def __init__(self):
        self.connection = MarketoConnection(
            client_id=self.client_id,
            client_secret=self.client_secret,
            instance_id=self.instance_id
        )

    @property
    def client_id(self):
        raise NotImplementedError

    @property
    def client_secret(self):
        raise NotImplementedError

    @property
    def instance_id(self):
        raise NotImplementedError

    def _strip_cookie(self, cookie):
        prefix = self.connection.cookie_prefix
        if prefix not in cookie:
            raise InvalidCookieException
        return cookie.replace(prefix, '')

    def get_lead_by_cookie(self, cookie):
        response = self.connection.get('leads.json', {
            'filterType': 'cookie',
            'filterValues': self._strip_cookie(cookie),
        })
        data = response[0] if response else {}
        return data

    def get_lead_by_id(self, lead_id):
        endpoint = 'lead/{}.json'.format(lead_id)
        response = self.connection.get(endpoint)
        return response

    def get_lead_by_email(self, email):
        response = self.connection.get('leads.json', {
            'filterType': 'email',
            'filterValues': email,
        })
        data = response[0] if response else {}
        return data

    def update_lead(self, lead_data):
        response = self.connection.post('leads.json', data={
            "lookupField": "email",
            "input": [lead_data],
        })
        return response[0]['id'], response[0]['status']

    def associate_lead(self, lead_id, cookie):
        '''
        Adds the cookie to the lead specified by lead_id on the remote server.
        '''
        url = 'leads/{}/associate.json'.format(lead_id)
        self.connection.post(url, params={
            'cookie': cookie
        })

    def request_campaign(self, lead_id, campaign_id):
        '''
        Triggers the campaign with the specified campaign_id on
        a set of leads.
        '''
        url = 'campaigns/{}/trigger.json'.format(campaign_id)
        data = {
            "input": {
                "leads": [{"id": lead_id}]
            }
        }
        self.connection.post(url, data=data)


def get_client(client_id, client_secret, instance_id):
    return type('MarketoClient', (MarketoClientBase,), {
        'client_id': client_id,
        'client_secret': client_secret,
        'instance_id': instance_id,
    })()
