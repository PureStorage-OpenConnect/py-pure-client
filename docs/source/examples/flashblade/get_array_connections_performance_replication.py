# list instantaneous replication performance for all array connections
res = client.get_array_connections_performance_replication()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list instantaneous file-replication performance for all array connections
res = client.get_array_connections_performance_replication(type='file-system')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list instantaneous file-replication performance for array connection with id '10314f42-020d-7080-8013-000ddt400090'
res = client.get_array_connections_performance_replication(ids=['10314f42-020d-7080-8013-000ddt400090'],
                                                           type='file-system')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list historical object-replication performance for all array connections between some
# start time and end time
res = client.get_array_connections_performance_replication(
    start_time=START_TIME,
    end_time=END_TIME,
    type='object-store',
    resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list historical object-replication performance for array connection 'remote_array' between some
# start time and end time
res = client.get_array_connections_performance_replication(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000,
    type='object-store',
    names=['remote_array'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, offset, remote_ids, remote_names,
#                     sort, total_only
# See section "Common Fields" for examples
