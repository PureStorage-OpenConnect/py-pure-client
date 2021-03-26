res = client.get_arrays_s3_specific_performance()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list historical s3 performance
res = client.get_arrays_s3_specific_performance(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Valid fields: ids
# See section "Common Fields" for examples
