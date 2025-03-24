res = client.get_arrays_nfs_specific_performance()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list historical nfs performance
res = client.get_arrays_nfs_specific_performance(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000)

# Other valid fields: allow_errors, context_names
# See section "Common Fields" for examples
