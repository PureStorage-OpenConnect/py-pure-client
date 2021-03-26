from pypureclient.flashblade import Alert

# unflag an alert with the given id
alert_settings = Alert(flagged=False)
res = client.patch_alerts(
    names=['1'], alerts_settings=alert_settings)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
