# list all policies
res = client.get_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list and sort by name in descendant order
res = client.get_policies(limit=5, sort="name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list with page size 5
res = client.get_policies(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all remaining policies
res = client.get_policies(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, filter, ids, names, offset, sort
# See section "Common Fields" for examples
