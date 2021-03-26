from pypureclient.flashblade import QuotaSetting

# set our contact info to a person and their email, and enable direct notification of
# users and groups regarding their quotas
new_contact = 'John Doe - j.doe@mycompany.com'
update_settings = QuotaSetting(contact=new_contact, direct_notifications_enabled=True)
res = client.patch_quotas_settings(quota_setting=update_settings)
# print the result of our update for record keeping
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
