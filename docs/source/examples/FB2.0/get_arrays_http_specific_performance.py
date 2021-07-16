res = client.get_arrays_http_specific_performance()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list historical http performance
res = client.get_arrays_http_specific_performance(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
