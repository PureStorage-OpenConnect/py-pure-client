# list the uses of all certificate groups
res = client.get_certificate_groups_uses()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list the uses of certificate groups named "all-trusted-certs" and "all-ad-certs"
res = client.get_certificate_groups_uses(names=['all-trusted-certs',
                                                'all-ad-certs'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, offset, sort
# See section "Common Fields" for examples
