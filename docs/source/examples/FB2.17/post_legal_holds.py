from pypureclient.flashblade.FB_2_17 import LegalHold

# create a legal hold
post_body = LegalHold(description="legal_hold_description")

res = client.post_legal_holds(names=['test_legal_hold'],
                              hold=post_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)
