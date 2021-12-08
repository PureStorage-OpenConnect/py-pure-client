# list user login events performed in the Purity//FB GUI, CLI, and REST API.
res = client.get_sessions()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, ids, limit, names, offset, sort
# See section "Common Fields" for examples
