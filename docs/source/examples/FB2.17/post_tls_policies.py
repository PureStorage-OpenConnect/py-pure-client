from pypureclient.flashblade.FB_2_17 import TlsPolicy, Reference

# create a TLS policy object with the desired settings
# note that name field is NOT specified during creation
# the policy is enabled by default. specifying an appliance certificate is mandatory,
# but other fields are optional and have default values
appliance_certificate = Reference(name='identity-to-clients')
tls_policy = TlsPolicy(
    appliance_certificate=appliance_certificate,
    min_tls_version='1.2',
    enabled_tls_ciphers=['default'],
    disabled_tls_ciphers=['TLS_CHACHA20_POLY1305_SHA256', 'SHA']
)
tls_policy_name = 'example_policy'
res = client.post_tls_policies(names=[tls_policy_name], policy=tls_policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
