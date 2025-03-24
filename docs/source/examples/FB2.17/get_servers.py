# List Servers
res = client.get_servers()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, filter, ids, limit, names, offset, sort, references
# See section "Common Fields" for examples
