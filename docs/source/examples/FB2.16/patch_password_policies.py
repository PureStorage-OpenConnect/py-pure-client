from pypureclient.flashblade.FB_2_16 import PasswordPolicy

# update a password policy
policy_body = PasswordPolicy(
            enabled=True,
            lockout_duration=0,
            max_login_attempts=0,
            min_password_length=0,
            password_history=0,
            min_password_age=0,
            enforce_username_check=False,
            min_character_groups=0,
            min_characters_per_group=0,
            enforce_dictionary_check=False,
)

res = client.patch_password_policies(names='management',
                                      policy=policy_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)

# Other valid fields: ids
# See section "Common Fields" for examples
