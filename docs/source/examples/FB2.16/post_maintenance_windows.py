from pypureclient.flashblade import MaintenanceWindowPost

# post the maintenance window on the array
duration = 60 * 60 * 1000  # 1 hour in milliseconds
body = MaintenanceWindowPost(timeout=duration)
res = client.post_maintenance_windows(names=["array"], maintenance_window=body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
