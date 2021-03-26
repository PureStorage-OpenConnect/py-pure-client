from pypureclient.flashblade import Eula, EulaSignature

# Update the Eula signature
signature = EulaSignature(name="example name", title="example", company="one company")
eula_body = Eula(signature=signature)
res = client.patch_arrays_eula(eula=eula_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
