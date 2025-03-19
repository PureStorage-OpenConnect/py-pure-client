from pypureclient.flashblade.FB_2_15 import Saml2SsoPost, Saml2SsoIdp, Saml2SsoSp, Reference

# Create an SSO SAML2 configuration
verification_cert = Reference(name='verification-cert', resource_type='certificates')
signing_cert = Reference(name='signing-cert', resource_type='certificates')
decryption_cert = Reference(name='decryption-cert', resource_type='certificates')
idp = Saml2SsoIdp(entity_id='http://test-entity-id',
                  url='https://test-sso-url',
                  metadata_url='https://test-metadata-url',
                  sign_request_enabled=True,
                  encrypt_assertion_enabled=True,
                  verification_certificate=verification_cert)
sp = Saml2SsoSp(signing_credential=signing_cert,
                decryption_credential=decryption_cert)
sso = Saml2SsoPost(enabled=True, array_url='https://test-array-url', idp=idp, sp=sp)
res = client.post_sso_saml2_idps(names=['test-sso'], idp=sso)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)
