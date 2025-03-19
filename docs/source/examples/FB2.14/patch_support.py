from pypureclient.flashblade import Support

# update support settings to enable phonehome and set a proxy
proxy = 'http://proxy.example.com:8080'
phonehome_enabled = True
support_settings_updates = Support(proxy=proxy, phonehome_enabled=phonehome_enabled)
res = client.patch_support(support=support_settings_updates)
# print our response containing our updates
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# open a remote assist session
remote_assist_active = True
remote_assist_duration = 24 * 60 * 60 * 1000  # 24 hours in milliseconds
open_ra_settings = Support(remote_assist_active=remote_assist_active, remote_assist_duration=remote_assist_duration)
res = client.patch_support(support=open_ra_settings)
# print our response, which will now have the time that our remote assist session was opened
# and when it will expire
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
