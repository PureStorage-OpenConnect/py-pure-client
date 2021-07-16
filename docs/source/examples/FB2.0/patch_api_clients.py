from pypureclient.flashblade import ApiClient

CLIENT_NAME = 'my_api_client'

# Enable the api client.
attr = ApiClient(enabled=True)
res = client.patch_api_clients(api_clients=attr, names=[CLIENT_NAME])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
