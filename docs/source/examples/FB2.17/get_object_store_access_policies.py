# list all object store access policies
res = client.get_object_store_access_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all object store access policies without listing their rules
res = client.get_object_store_access_policies(exclude_rules=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Valid fields: allow_errors, context_names, continuation_token, filter, ids, limit, names, offset, sort
# See section "Common Fields" for examples
