# list all keytabs on the system
res = client.get_keytabs()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five keytabs using default sort. only looking for ones beginning with 'kt1.'
res = client.get_keytabs(limit=5, names=["kt1.*"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five keytabs, sorting by the key version number used to generate them
res = client.get_keytabs(limit=5, sort="kvno")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all keytabs, filtering only for keytabs with aes256 in their encryption type
res = client.get_keytabs(filter='contains(encryption_type, "aes256")')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, ids, offset
# See section "Common Fields" for examples
