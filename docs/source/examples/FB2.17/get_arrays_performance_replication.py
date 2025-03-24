# list instantaneous replication performance for array
res = client.get_arrays_performance_replication()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list instantaneous file-replication performance for array
res = client.get_arrays_performance_replication(type='file-system')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list historical object-replication performance for array between some
# start time and end time
res = client.get_arrays_performance_replication(
    start_time=START_TIME,
    end_time=END_TIME,
    type='object-store',
    resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names
# See section "Common Fields" for examples
