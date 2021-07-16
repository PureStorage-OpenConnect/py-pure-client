from pypureclient.flashblade import ApiClientsPost

CLIENT_NAME = 'my_api_client'
CLIENT_TTL_IN_MS = 1000 * 60 * 60       # 1 hour in milliseconds
CLIENT_PUB_KEY = ("\n"
                  "-----BEGIN PUBLIC KEY-----\n"
                  "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArSe6chh1JzME9svOKjU0\n"
                  "eKTm8S23Ok3Vr2bWuPri/YHfLrlnRwWoCt+st0/BebKSJ+fQUWOaLlqpZQKpI8oR\n"
                  "gJ9sWmwGibVG8cTuz7XMkskx9bsm/bjIenuB4W+s3g0BCsi9930mfdKgJgFzY69O\n"
                  "nLh7d7hAFcmhSJa945PryQZpvJ/U4Ue5F4d+WXgEJ0SoSRaZ6bbeMPhcbMHTzTum\n"
                  "2ZrPBkK5cqPYitaso6BXeAlqNQPw4Kbu4Ugm0CTogrtImkwoonWDDP34XMOq+u7q\n"
                  "sNTbJSvDKMTM1RPPrTWCaLiuZkdLVEVesZ9/8+XUMIgBTElwQJDCAQer03MJzqRr\n"
                  "1eCZGgLfDuYqwMG2MFaAX7kgqBwwyqRTd6MxaQxt2nkdfwiXSY71llzEQ23g3T+1\n"
                  "64zjwAL5f+dtu8PkGF7IdU2T8P2Qk9bG9pckwZHWYkBK77BAk5jbmSzsKGZgRb2R\n"
                  "1E+TWDKIaveFhQp251j/C5wkZwMXgjOzN+BOPo+OiLBGUl+jRybWA9f7Vq1MEdf6\n"
                  "SEdLiqYrXcZERkYBMieLXAfdtaztAIb96cUu+OKMSLDk+D0GHkUfm7lEbDK3ew1+\n"
                  "D6z+BnxDyH6oqZzz4lS2kPLBLsc+6pdTGuKLf0S9YuLiqJe659AdwU8+X/3KtwNd\n"
                  "FVJSaxdFbWx0nj3hJqFkIO8CAwEAAQ==\n"
                  "-----END PUBLIC KEY-----\n")

# Create a new api client with a max_role of storage_admin who has permissions to
# perform storage related operations such as administering volumes, hosts and host groups.
# Note that this created api client will have the lesser of the permissions granted by max_role
# in the api_client and the max role of the associated oauth login.
# The public_key will be the key provided by your oauth login provider.
attr = ApiClientsPost(max_role={'name': 'storage_admin'},
                      public_key=CLIENT_PUB_KEY,
                      issuer=CLIENT_NAME,
                      access_token_ttl_in_ms=CLIENT_TTL_IN_MS)
res = client.post_api_clients(names=[CLIENT_NAME], api_client=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
