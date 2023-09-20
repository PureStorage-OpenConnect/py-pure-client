from pypureclient.flashblade import Eula, EulaSignature

# Update the EULA with eula body parameter
# The fields 'name', 'title', 'company' are no longer required, but are still accepted and will be ignored.

signature = EulaSignature(name="example name", title="example", company="one company")
eula_body = Eula(signature=signature)
res = client.patch_arrays_eula(eula=eula_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Update the EULA with eula empty body parameter
# eula body with empty signature are still accepted, but will be ignored.
signature = EulaSignature()
eula_body = Eula(signature=signature)
res = client.patch_arrays_eula(eula=eula_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Update the EULA with no parameter
res = client.patch_arrays_eula()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
