# list all policies of all types
res = client.get_policies_all()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Valid fields: continuation_token, filter, ids, limit, names, offset, sort
# See section "Common Fields" for examples
