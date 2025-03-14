from pypureclient.flashblade.FB_2_14 import PublicKeyPost

key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCxlwM29F5T4V+rfKt0sxa25/WVYvNCzzIx8K4BkFDgcOMg3i0Cui4KvDRZ1uVuOxINmjIxEXWNIF/kJh0upMebvsjW11y5pIcqgIQBIDG3vT/xS/6FNCUI+d9Uv8qEyty0OBrDkqmRYxMjlVt4P7RQyRhbIKVEFVr1MeuL3besqLBmtQCIfZDa/rvcmrtMpA6eD//kfISwVUr1qvR41b3iBHwYPaU6D+hWlv1dqcGZ3eNJfGrfx2V02mnhn7y15pr7eUtUhY90gVt6YopnH8o56HC+UBxbzQx6qmKefRyoZSV2DFKYghrIpTouV3SF27db5u/umCvbrN+LDUbQkMscJpNg+FKXy7vPA03rzeXu02+F1B9mLGTDB/eNwbNGyREWndV5gdMexPidffG099/DUPs1f+t5PhnURPoN9GaOjb18mkWDeystxmfaQZs5DMFNwj5aerqZZsucaKuFixsaCh+D+SczjFAjzbq8HG7zwLGnYMx0Tqe09bPbSGrmC5s= example2@purestorage.com'
key_body = PublicKeyPost(public_key=key)
res = client.post_public_keys(names=['rsa-key'], public_key=key_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
