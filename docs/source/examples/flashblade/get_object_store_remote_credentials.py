# list all remote credentials
res = client.get_object_store_remote_credentials()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five remote credentials using default sort
res = client.get_object_store_remote_credentials(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five remote credentials and sort by access key
res = client.get_object_store_remote_credentials(limit=5, sort='access_key_id')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining remote credentials
res = client.get_object_store_remote_credentials(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter to see only remote credentials that are on a specific remote
res = client.get_object_store_remote_credentials(filter='name=\'s3target/*\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, names, offset
# See section "Common Fields" for examples
