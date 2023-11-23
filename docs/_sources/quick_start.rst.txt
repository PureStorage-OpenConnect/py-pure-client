Quick Start
===========

Authentication
--------------

This section documents the instantiation of valid, working Pure1, FlashArray, and FlashBlade
clients required to subsequently call other client methods.

FlashArray Client
~~~~~~~~~~~~~~~~~

Start by importing the ``flasharray`` submodule in ``pypureclient``:

.. code-block:: python

   from pypureclient import flasharray

Instantiation of a FlashArray client requires authentication. More information
is available in the `REST API 2.0 Authentication Guide
<https://support.purestorage.com/FlashArray/PurityFA/Purity_FA_REST_API/Reference/REST_API_2.0_Authentication_Guide>`__

After creating a client using ``pureapiclient`` on the FlashArray array you wish
to target, you can pass the various parameters into the ``Client`` constructor:

.. code-block:: python

   from pypureclient import flasharray
   client = flasharray.Client('flasharray.example.com',
                              private_key_file=[...],
                              private_key_password=[...],
                              username=[...],
                              client_id=[...],
                              key_id=[...],
                              issuer=[...])

If directly using a pre-generated ID token is preferred, it can be used in the
same way. Note that using a pre-generated ID token will cause the client to fail
when the ID token expires.

.. code-block:: python

   from pypureclient import flasharray
   client = flasharray.Client('flasharray.example.com',
                              id_token=[...])


FlashBlade Client
~~~~~~~~~~~~~~~~~

Start by importing the ``flashblade`` submodule in ``pypureclient``:

.. code-block:: python

   from pypureclient import flashblade

Instantiation of a FlashBlade client requires authentication. More information
is available in the `FlashBlade REST API FAQ
<https://support.purestorage.com/FlashBlade/Purity_FB/PurityFB_REST_API/Management_REST_API/FlashBlade_REST_API_FAQ>`__

After creating and enabling a client using ``pureapiclient`` on the FlashBlade array you wish
to target, you can pass the various parameters into the ``Client`` constructor:

.. code-block:: python

   from pypureclient import flashblade
   client = flashblade.Client('flashblade.example.com',
                              private_key_file=[...],
                              private_key_password=[...],
                              username=[...],
                              client_id=[...],
                              key_id=[...],
                              issuer=[...])

If directly using a pre-generated ID token is preferred, it can be used in the
same way. Note that using a pre-generated ID token will cause the client to fail
when the ID token expires.

.. code-block:: python

   from pypureclient import flashblade
   client = flashblade.Client('flashblade.example.com',
                              id_token=[...])

You can also use an API token created by using ``pureadmin`` on the FlashBlade array
if that is preferred.

.. code-block:: python

   from pypureclient import flashblade
   client = flashblade.Client('flashblade.example.com',
                              api_token=[...])

If you are writing an API integration for FlashBlade for distribution to your customers
and partners, we ask that you ensure that your API integration "self-identifies" when
connecting to FlashBlade.

To do this, choose a unique, human-readable string that identifies your FlashBlade API
integration by name and version, and specify it as the ``user_agent``.

.. code-block:: python

   from pypureclient import flashblade
   client = flashblade.Client('flashblade.example.com',
                              api_token=[...],
                              user_agent='YourCompanyName_YourProductIntegrationName/YourIntegrationVersion')


Pure1 client
~~~~~~~~~~~~

Start by importing the ``pure1`` submodule in ``pypureclient``:

.. code-block:: python

   from pypureclient import pure1


Instantiation of a Pure1 client requires authentication to use the Pure1 Manage
public API. If not already configured, instructions for getting access to and
using the Pure1 Manage public API can be found at the `API reference page
<https://support.purestorage.com/Pure1/Pure1_Manage/Pure1_Manage_-_REST_API/Pure1_Manage_-_REST_API__Reference>`_.

For Pure1 client instantiation you can use environment variables. It is
recommended to use environment variables for the Pure1 client.

.. code-block:: bash

    $ export PURE1_PRIVATE_KEY_FILE=[...]
    $ export PURE1_PRIVATE_KEY_PASSWORD=[...]
    $ export PURE1_APP_ID=[...]

Alternatively, the authentication information can be passed directly into the client.

.. code-block:: python
    from pypureclient import pure1
    client = pure1.Client(private_key_file=[...],
                          private_key_password=[...],
                          app_id=[...])

If directly using a pre-generated ID token is preferred, it can be used in the
same way. Note that using a pre-generated ID token will cause the client to fail
when the ID token expires.

.. code-block:: bash

    $ export PURE1_ID_TOKEN=[...]

.. code-block:: python

    client = pure1.Client(id_token=[...])


Client Examples
---------------

These examples assume the client has already been set up using the instructions
in the Authentication section above.

The client has functions that model the endpoints of the API you are accessing
(FlashArray, FlashBlade, or Pure1) and accept the query parameters as arguments.

.. code-block:: python

    response = client.get_volumes(sort=pure1.Volume.name.ascending(), limit=10)
    volumes = list(response.items)

.. code-block:: python

    response = client.get_volumes(names='volume1')
    volume = list(response.items)[0]

.. code-block:: python

    response = client.get_volumes(names=['volume1', 'volume2'])
    volumes = list(response.items)

.. code-block:: python

    response = client.get_volumes(ids='f0510daa-cec8-4544-8015-206d819b3')
    volume = list(response.items)[0]

A response is either a ``ValidResponse`` or ``ErrorResponse`` object that models
the API call response and includes the data.

.. code-block:: python

    response = client.get_volumes()
    print(response.status_code)
    print(response.headers)
    print(response.total_item_count)
    print(response.continuation_token)
    volumes = list(response.items)
    volume1 = volumes[0]

.. code-block:: python

    response = client.get_volumes(sort='invalid')
    print(response.status_code)
    print(response.headers)
    print(response.errors)

One enhancement over the plain REST API is that the client also accepts models
as function arguments.

.. code-block:: python

    response = client.get_volumes()
    volume1 = list(response.items)[0]

    # This works on the Pure1 client only
    response = client.get_arrays(volume1.arrays)
    response = client.get_arrays(ids=[array.id for array in volume1.arrays])
    # both make the same request

The response items are stored in an iterator. The iterator will exhaust the list
of items in the collection, up to the limit specified in the request. If there
is no limit specified, the iterator will return all items. Note that for Pure1,
the server returns a maximum of 1000 items per call; the iterator may make
subsequent API calls to get more items if there are more than 1000 items in the
collection.

.. code-block:: python

    response = client.get_volumes()
    print response.total_item_count
    num_volumes = 0
    for volume in response.items:
        num_volumes += 1
        print volume
    print num_volumes

It is also possible to get all of the items in a list without explicitly
iterating. It will exhaust the iterator and put the items in a list.

.. code-block:: python

    response = client.get_volumes()
    all_volumes = list(response.items)

A custom X-Request-ID header can also be provided to any request.

.. code-block:: python

    response = client.get_pods(x_request_id='readthedocs-test')
    print response.headers.x_request_id

An example of querying sustainability information.

.. code-block:: python

    response = client.get_assessment_sustainability_arrays()
    for assessment in response.items:
        print assessment

.. code-block:: python

    response = client.get_assessment_sustainability_insights_arrays()
    for insight in response.items:
        print insight


Filtering
---------

Filters are defined by the public API specifications and are interpreted as a
query parameter in an API call. Filters can also be combined with other
parameters as well. The client allows for easier composition of filters,
especially when taking advantage of intellisense or editor auto-completion.
Filter objects are not required to be used if strings are preferred.

These examples are for the ``pure1`` client, but are applicable to all of the
clients (for example, the same ``Filter`` module is exposed inside the
``flasharray`` and ``flashblade`` modules).

.. code-block:: python

    response = client.get_arrays(filter='os=\'Purity//FB\'', sort=pure1.Array.as_of.descending(), limit=5)
    response = client.get_arrays(filter=pure1.Filter.eq(pure1.Array.os, 'Purity//FB'), sort=pure1.Array.as_of.descending(), limit=5)
    response = client.get_arrays(filter=pure1.Array.os == 'Purity//FB', sort=pure1.Array.as_of.descending(), limit=5)
    # all three get five arrays where their operating system is Purity//FB (FlashBlades), sorted by _as_of

Filters can be created by calling static Filter functions with Property objects, by using overridden operators on Property objects, or by calling certain Propery functions.

.. code-block:: python

    pure1.Filter.eq(pure1.Array.name, 'array')
    pure1.Array.name == 'array'
    # both resolve to "name='array'"

    pure1.Filter.ne(pure1.Array.name, 'notarray')
    pure1.Array.name != 'notarray'
    # both resolve to "name!='notarray'"

    pure1.Filter.gt(pure1.Array.as_of, 154000000000)
    pure1.Array.as_of > 154000000000
    # both resolve to "_as_of>154000000000"

    pure1.Filter.ge(pure1.Array.as_of, 154000000000)
    pure1.Array.as_of >= 154000000000
    # both resolve to "_as_of>=154000000000"

    pure1.Filter.lt(pure1.Array.as_of, 154000000000)
    pure1.Array.as_of < 154000000000
    # both resolve to "_as_of<154000000000"

    pure1.Filter.le(pure1.Array.as_of, 154000000000)
    pure1.Array.as_of <= 154000000000
    # both resolve to "_as_of<=154000000000"

    pure1.Filter.exists(pure1.Volume.source)
    pure1.Volume.source.exists()
    # both resolve to "source"

    pure1.Filter.contains(pure1.Volume.name, "vol")
    # resolves to "contains(name, 'vol')"

    pure1.Filter.in_(pure1.Volume.name, ['vol1', 'vol2', 'vol3'])
    # resolves to "name=('vol1','vol2','vol3')"

    pure1.Filter.tags('key', 'value')
    # resolves to "tags('key', 'value')"

A model's Property may be a list of items (e.g. a Volume's "arrays" is a list), and another Property may be created on a specific index of that list: "all", or "any". A list index Property can be created by calling specific functions on a Property or by using overridden operators. These Properties can then be used in Filters.

.. code-block:: python

    pure1.Volume.arrays.any()
    pure1.Volume.arrays['any']
    # both resolve to "arrays[any]"

    pure1.Volume.arrays.all()
    pure1.Volume.arrays['all']
    # both resolve to "arrays[all]"

A nested Property is that of an item that is another model's property (e.g. Array.id where an Array is a Pod's "source"). A nested Property can be created by calling a specific function on a property or by using overridden operators.

.. code-block:: python

    pure1.Pod.source.subproperty(pure1.Array.id)
    pure1.Pod.source + pure1.Array.id
    # both resolve to "source.id"

    pure1.Pod.arrays.any().subproperty(pure1.PodArrayStatus.mediator_status)
    pure1.Pod.arrays.any() + pure1.PodArrayStatus.mediator_status
    # both resolve to "arrays[any].mediator_status"

Filters can also be compounded. When compounding multiple operators, parentheses are required by Python to denote order of operations. Compound Filters can be created by calling specific Filter functions or by using overridden operators.

.. code-block:: python

    pure1.Filter.and_(pure1.Array.name == 'array', pure1.Array.os.exists())
    (pure1.Array.name == 'array') & pure1.Array.os.exists()
    # both resolve to "name=='array' and os"

    pure1.Filter.or_(pure1.Array.name == 'array', pure1.Array.os.exists())
    (pure1.Array.name == 'array') | pure1.Array.os.exists()
    # both resolve to "name=='array' or os"

    pure1.Filter.not_(pure1.Filter.tags('key', 'value'))
    ~ pure1.Filter.tags('key', 'value')
    # both resolve to "not(tags('key', 'value'))"

    pure1.Filter.and_(pure1.Filter.or_(pure1.Array.name == 'array', pure1.Array.os.exists()), pure1.Filter.not_(pure1.Filter.tags('key', 'value')))
    ((pure1.Array.name == 'array') | pure1.Array.os.exists()) & (~ pure1.Filter.tags('key', 'value'))
    # both resolve to "name='array' or os and not(tags('key', 'value'))"
