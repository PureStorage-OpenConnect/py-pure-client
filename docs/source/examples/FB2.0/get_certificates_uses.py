# list the uses of all certificates
res = client.get_certificates_uses()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list the uses of certificates named "ad-cert-1" and "posix-cert"
res = client.get_certificates_uses(names=['ad-cert-1', 'posix-cert'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, offset, sort
# See section "Common Fields" for examples
