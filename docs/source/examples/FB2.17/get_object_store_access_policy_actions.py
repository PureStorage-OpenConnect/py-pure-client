# list all object store access policy actions
res = client.get_object_store_access_policy_actions()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Valid fields: allow_errors, context_names, continuation_token, filter, limit, names, offset, sort
# See section "Common Fields" for examples
