# List all lifecycle rules
res = client.get_lifecycle_rules()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# List first two lifecycle rules in bucket 'mybucket'. Use default sorting.
res = client.get_lifecycle_rules(limit=2, bucket_names=['mybucket'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# List all lifecycle rules in bucket with id '100abf42-0000-4000-8023-000det400090'
res = client.get_lifecycle_rules(limit=2, bucket_ids=['100abf42-0000-4000-8023-000det400090'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# List the first lifecycle rule when sorting by prefix.
res = client.get_lifecycle_rules(limit=1, sort='prefix')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, names, offset, sort
# See section "Common Fields" for examples
