from pypureclient.flashblade import AlertWatcher

# An example of how to disable an alert watcher, so they stop receiving all emails about
# alerts
watcher_settings = AlertWatcher(enabled=False)
res = client.patch_alert_watchers(
    names=['person_on_vacation@mydomain.com'], alert_watcher=watcher_settings)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# An example of how to set an alert watcher to only receive emails about alerts of severity
# 'critical'. This can be useful if there's an email alias tied directly into an on-call
# paging system or if there's an email alias of people who should be contacted about issues
# that need to be escalated quickly
watcher_settings = AlertWatcher(minimum_notification_severity='critical')
res = client.patch_alert_watchers(
    names=['storage_admins_on_call@mydomain.com'], alert_watcher=watcher_settings)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples
