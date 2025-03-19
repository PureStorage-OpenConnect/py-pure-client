# list all public keys uses
res = client.get_public_keys_uses()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list key uses by providing key names
res = client.get_public_keys_uses(names=['ad-key-1', 'some-other-key'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, offset, sort
# See section "Common Fields" for examples
