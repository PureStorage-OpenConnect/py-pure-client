# list instantaneous performance for all buckets
res = client.get_buckets_performance()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list instantaneous performance for buckets 'bucket1' and 'bucket2'
res = client.get_buckets_performance(names=['bucket1', 'bucket2'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list historical buckets performance for all buckets between some
# start time and end time
res = client.get_buckets_performance(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000)

# list historical buckets performance for buckets 'bucket1' and 'bucket2' between some
# start time and end time
res = client.get_buckets_performance(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000,
    names=['bucket1', 'bucket2'])

# total instantaneous performance across 2 buckets
res = client.get_buckets_performance(names=['bucket1', 'bucket2'], total_only=True)
print(res)

# Other valid fields: continuation_token, filter, ids, limit, offset, sort
# See section "Common Fields" for examples
