res = client.get_arrays_performance()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list array performance for http
res = client.get_arrays_performance(protocol='http')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list array performance for s3
res = client.get_arrays_performance(protocol='s3')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list array performance for nfs
res = client.get_arrays_performance(protocol='nfs')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list historical array performance
res = client.get_arrays_performance(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))


# Other valid fields: allow_errors, context_names
# See section "Common Fields" for examples
