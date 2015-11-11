# pymarketo

A pythonic interface to the Marketo REST API.
This project succeeds the Python SOAP interface, now called [pymarketo-soap](https://github.com/jswinarton/pymarketo-soap)

## Get started

```python
from pymarketo import get_client

client = get_client(
    client_id='some-client-id',
    client_secret='some-client-secret',
    instance_id='111-AAA-111',
)
```

Pymarketo currently supports basic lead read/write operations and campaign management.

```python
client.get_lead_by_email('jeremy@swinarton.com')
# {u’createdAt': u'2014-03-13T15:54:53Z',
#  u'email': u'jeremy@swinarton.com',
#  u'firstName': u'Jeremy',
#  u'id': 237,
#  u'lastName': u'Swinarton',
#  u'updatedAt': u'2015-09-04T16:06:04Z'}

client.update_lead({
    'email': 'jeremy@swinarton.com',
    'company': 'The Ministry of Silly Walks',
})
# (237, 'success')

client.request_campaign(lead_id=237, campaign_id=1234)
# None
```
