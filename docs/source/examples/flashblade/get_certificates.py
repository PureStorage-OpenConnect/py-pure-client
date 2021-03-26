# list all certificates
res = client.get_certificates()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list certificates named "ad-cert-1" and "posix-cert"
res = client.get_certificates(names=['ad-cert-1', 'posix-cert'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, offset, sort
# See section "Common Fields" for examples
