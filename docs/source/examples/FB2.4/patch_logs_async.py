from pypureclient.flashblade import LogsAsync, Reference

logs_async_attr = LogsAsync(start_time=1643664575040, end_time=1643668175040, hardware_components=[Reference(name='CH1')])
res = client.patch_logs_async(logs_async=logs_async_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
