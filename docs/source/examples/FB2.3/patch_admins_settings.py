from pypureclient.flashblade import AdminSetting

# Configure admin settings
settings = AdminSetting(lockout_duration=60, max_login_attempts=5, min_password_length=8)
res = client.patch_admins_settings(admin_setting=settings)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
