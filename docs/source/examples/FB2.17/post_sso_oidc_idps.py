from pypureclient.flashblade.FB_2_17 import OidcSso, OidcSsoPostIdp, Reference

# create a SSO OIDC configuration
provider_url_ca_certificate = Reference(name='test-ca-certificate')
provider_url_ca_certificate_group = Reference(name='test-ca-certificate-group')
idp = OidcSsoPostIdp(provider_url='https://test-provider-url',
                  provider_url_ca_certificate=provider_url_ca_certificate,
                  provider_url_ca_certificate_group=provider_url_ca_certificate_group)
oidc = OidcSso(enabled=True, services=['object'], idp=idp)
res = client.post_sso_oidc_idps(names=['test-oidc'], idp=oidc)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)
