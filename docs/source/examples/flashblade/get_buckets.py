# list all buckets
res = client.get_buckets()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all destroyed buckets
res = client.get_buckets(destroyed=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by unique in descendant order
res = client.get_buckets(limit=5, sort="space.unique-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_buckets(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining object store accounts
res = client.get_buckets(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter
res = client.get_buckets(filter='name=\'mybucket*\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, names, offset, total_only
# See section "Common Fields" for examples
