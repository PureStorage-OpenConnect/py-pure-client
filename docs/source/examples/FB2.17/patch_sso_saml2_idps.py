from pypureclient.flashblade.FB_2_17 import Saml2Sso, Saml2SsoIdp, Reference

# Update an SSO SAML2 configuration
idp = Saml2SsoIdp(entity_id='http://test-entity-id',
                  url='https://test-sso-url',
                  metadata_url='https://test-metadata-url',
                  metadata_url_ca_certificate=Reference(name='metadata-url-ca-cert', resource_type='certificates'),
                  metadata_url_ca_certificate_group=Reference(name='metadata-url-ca-cert-group', resource_type='certificate_groups'),
                  encrypt_assertion_enabled=True)
sso = Saml2Sso(enabled=True, array_url='https://test-array-url', idp=idp, services=['object'], binding='none')
res = client.patch_sso_saml2_idps(names=['test-sso'], idp=sso)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)

# Other valid fields: ids
# See section "Common Fields" for examples
