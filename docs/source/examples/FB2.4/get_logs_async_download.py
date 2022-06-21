res = client.get_logs_async_download(names=['array-name_logs_2022-01-02.03_1643259782296.zip'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
