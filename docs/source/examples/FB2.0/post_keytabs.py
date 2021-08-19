from pypureclient.flashblade import KeytabPost, Reference

# Rotate keytabs for active directory account
account = Reference(name="test-config", resource_type="active-directory")
keytab = KeytabPost(source=account)
res = client.post_keytabs(keytab=keytab)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: name_prefixes
# See section "Common Fields" for examples
