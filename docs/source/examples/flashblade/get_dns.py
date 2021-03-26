# list DNS configuration
res = client.get_dns()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Valid fields: continuation_token, filter, ids, limit, names, offset, sort
# See section "Common Fields" for examples
