# list alert watchers with email address matching the below wildcard patterns. the first
# pattern includes all emails with "on_call" in them, and second pattern includes all
# emails ending with "@example.com"
res = client.get_alert_watchers(
    names=['*on_call*', '*@example.com'], sort='name-')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, offset
# See section "Common Fields" for examples
