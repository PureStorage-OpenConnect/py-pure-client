# list instantaneous nfs performance for all file systems
res = client.get_file_systems_performance(protocol='nfs')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list instantaneous nfs performance for file systems 'fs1' and 'fs2'
res = client.get_file_systems_performance(names=['fs1', 'fs2'], protocol='nfs')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list instantaneous nfs performance for file system with id '10314f42-020d-7080-8013-000ddt400090'
res = client.get_file_systems_performance(ids=['10314f42-020d-7080-8013-000ddt400090'],
                                          protocol='nfs')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list historical file systems nfs performance for all file systems between some
# start time and end time
res = client.get_file_systems_performance(
    start_time=START_TIME,
    end_time=END_TIME,
    protocol='nfs',
    resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list historical file systems nfs performance for file systems 'fs1' and 'fs2' between some
# start time and end time
res = client.get_file_systems_performance(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000,
    protocol='nfs',
    names=['fs1', 'fs2'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# total instantaneous performance across 2 filesystems
res = client.get_file_systems_performance(names=['fs1', 'fs2'], protocol='nfs',
                                          total_only=True)
print(res)

# Other valid fields: continuation_token, filter, ids, limit, offset, sort
# See section "Common Fields" for examples
