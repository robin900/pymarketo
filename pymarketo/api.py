from datetime import (
    datetime,
    timedelta,
)
import os
import json

import requests
import six

from pymarketo.exceptions import MarketoAPIException


class MarketoConnection(object):
    '''
    A MarketoConnection instance is responsible for authenticating
    with the Marketo server and making basic GET and POST requests.
    '''

    def __init__(self, client_id, client_secret, instance_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.instance_id = instance_id

    def build_endpoint_url(self, *urls):
        prefix = 'https://{}.mktorest.com/'.format(self.instance_id)
        return os.path.join(prefix, *urls)

    def request_token(self):
        '''
        Request an authentication token from the Marketo server.
        Returns the access token and its expiry time, in seconds.
        '''
        endpoint = self.build_endpoint_url('identity/oauth/token')
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.get(endpoint, params=params).json()
        return response['access_token'], response['expires_in']

    @property
    def token(self):
        '''
        Returns the cached access token, if it exists and is still valid.
        If the token value has not been set or has expired,
        regenerate the token.
        '''
        if (
            not getattr(self, '_token', None) or
            self._token_expires < datetime.now()
        ):
            token, expires_in = self.request_token()
            self._token = token
            self._token_expires = datetime.now() + timedelta(0, expires_in)
        return self._token

    @property
    def cookie_prefix(self):
        '''
        The string that prefixes all cookies.
        Some Marketo API calls request and return cookies
        that are missing this prefix.
        '''
        return 'id:{}&token:'.format(self.instance_id)

    def process_errors(self, data):
        '''
        Raise an exception if there are errors
        in the response.
        '''
        if 'errors' in data:
            raise MarketoAPIException(
                'The Marketo API server returned '
                'error #{code}: "{message}"'.format(
                    code=data['errors'][0]['code'],
                    message=data['errors'][0]['message']
                )
            )

    def process_data(self, data):
        result = data.get('result', [])
        for i, item in enumerate(result):
            # Strip 'None' fields from the response lead data.
            result[i] = {k: v for k, v in six.iteritems(item) if v is not None}

            # If 'cookies' is part of lead data, split into a list by comma
            # and add the prefix to the front.
            if 'cookies' in result[i]:
                cookies = result[i]['cookies']
                cookies = cookies.split(',')
                cookies = [(self.cookie_prefix + c) for c in cookies]
                result[i]['cookies'] = cookies
        return result

    def process(self, data):
        self.process_errors(data)
        data = self.process_data(data)
        return data

    def get(self, endpoint, params=None):
        params = params or {}
        params.update({'access_token': self.token})
        url = self.build_endpoint_url('rest/v1', endpoint)

        try:
            r = requests.get(url, params=params)
        except requests.ConnectionError:
            raise MarketoAPIException('Could not connect to server')
        data = r.json()
        return self.process(data)

    def post(self, endpoint, params=None, data=None):
        params = params or {}
        params.update({'access_token': self.token})
        url = self.build_endpoint_url('rest/v1', endpoint)
        data = json.dumps(data)
        headers = {'content-type': 'application/json'}

        try:
            r = requests.post(url, params=params, data=data, headers=headers)
        except requests.ConnectionError:
            raise MarketoAPIException('Could not connect to server')
        data = r.json()
        return self.process(data)
