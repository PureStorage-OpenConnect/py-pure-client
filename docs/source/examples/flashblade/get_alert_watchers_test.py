# test alert watchers with given email addresses
res = client.get_alert_watchers_test(
    names=['test1@example.com', 'test2@example.com'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, ids, sort
# See section "Common Fields" for examples
