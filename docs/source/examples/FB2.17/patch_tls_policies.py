from pypureclient.flashblade.FB_2_17 import TlsPolicy, Reference

# update a TLS policy object with the desired settings
# note that name field is NOT specified during creation
# the policy is enabled by default. specifying an appliance certificate is mandatory,
# but other fields are optional and have default values
appliance_certificate = Reference(name='new-identity-to-clients')
tls_policy = TlsPolicy(
    appliance_certificate=appliance_certificate,
    min_tls_version='1.2',
    enabled_tls_ciphers=['TLS_CHACHA20_POLY1305_SHA256', 'AESGCM'],
    disabled_tls_ciphers=['SHA'],
    enabled=True
)
tls_policy_name = 'example_policy'
res = client.patch_tls_policies(names=[tls_policy_name], policy=tls_policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# policies can also be updated by id
tls_policy_id = '10314f42-020d-7080-8013-000ddt400013'
res = client.patch_tls_policies(ids=[tls_policy_id], policy=tls_policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
