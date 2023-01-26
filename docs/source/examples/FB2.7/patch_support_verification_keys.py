from pypureclient.flashblade import VerificationKeyPatch

# Update the signed Verification Key for the array
signed_public_key_text = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArSe6chh1JzME9svOKjU0
eKTm8S23Ok3Vr2bWuPri/YHfLrlnRwWoCt+st0/BebKSJ+fQUWOaLlqpZQKpI8oR
gJ9sWmwGibVG8cTuz7XMkskx9bsm/bjIenuB4W+s3g0BCsi9930mfdKgJgFzY69O
nLh7d7hAFcmhSJa945PryQZpvJ/U4Ue5F4d+WXgEJ0SoSRaZ6bbeMPhcbMHTzTum
2ZrPBkK5cqPYitaso6BXeAlqNQPw4Kbu4Ugm0CTogrtImkwoonWDDP34XMOq+u7q
sNTbJSvDKMTM1RPPrTWCaLiuZkdLVEVesZ9/8+XUMIgBTElwQJDCAQer03MJzqRr
1eCZGgLfDuYqwMG2MFaAX7kgqBwwyqRTd6MxaQxt2nkdfwiXSY71llzEQ23g3T+1
64zjwAL5f+dtu8PkGF7IdU2T8P2Qk9bG9pckwZHWYkBK77BAk5jbmSzsKGZgRb2R
1E+TWDKIaveFhQp251j/C5wkZwMXgjOzN+BOPo+OiLBGUl+jRybWA9f7Vq1MEdf6
SEdLiqYrXcZERkYBMieLXAfdtaztAIb96cUu+OKMSLDk+D0GHkUfm7lEbDK3ew1+
D6z+BnxDyH6oqZzz4lS2kPLBLsc+6pdTGuKLf0S9YuLiqJe659AdwU8+X/3KtwNd
FVJSaxdFbWx0nj3hJqFkIO8CAwEAAQ==
-----END PUBLIC KEY-----"""
res = client.patch_support_verification_keys(key=VerificationKeyPatch(signed_verification_key=signed_public_key_text))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

