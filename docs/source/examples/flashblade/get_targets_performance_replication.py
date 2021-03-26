# list instantaneous replication performance for all targets
res = client.get_targets_performance_replication()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list instantaneous file-replication performance for target with id '10314f42-020d-7080-8013-000ddt400090'
res = client.get_targets_performance_replication(ids=['10314f42-020d-7080-8013-000ddt400090'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list historical performance for all targets between some
# start time and end time
res = client.get_targets_performance_replication(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list historical performance for target 's3target1' between some
# start time and end time
res = client.get_targets_performance_replication(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000,
    names=['s3target1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# total instantaneous performance across 2 targets
res = client.get_targets_performance_replication(names=['s3target1', 's3target2'],
                                                 total_only=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
