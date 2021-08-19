res = client.get_logs(start_time=1527415200000, end_time=1527415200000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
