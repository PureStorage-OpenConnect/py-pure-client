# list all replica links
res = client.get_bucket_replica_links()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five replica links using default sort
res = client.get_bucket_replica_links(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five replica links and sort by remote
res = client.get_bucket_replica_links(limit=5, sort='remote')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list replica links on the remote 's3target'
res = client.get_bucket_replica_links(remote_names=['s3target'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining replica links
res = client.get_bucket_replica_links(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter to see only replica links that are paused
res = client.get_bucket_replica_links(filter='paused')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, ids, local_bucket_ids, local_bucket_names, offset,
#    remote_bucket_names, remote_ids, total_only
# See section "Common Fields" for examples
