res = client.get_alerts()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list alerts and sort by severity
res = client.get_alerts(sort='severity')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, ids, names, offset
# See section "Common Fields" for examples
