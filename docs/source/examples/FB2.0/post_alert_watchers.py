from pypureclient.flashblade import AlertWatcherPost

# create an alert watcher with a given email address such that they'll receive emails
# about all system alerts
res = client.post_alert_watchers(names=['i_get_everything@example.com'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create an alert watcher with a given email address such that they'll only receive emails
# about alerts of severity 'warning' and above
watcher_create_settings = AlertWatcherPost(minimum_notification_severity='warning')
res = client.post_alert_watchers(names=['rack_monitor@example.com'],
                                 alert_watcher=watcher_create_settings)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
