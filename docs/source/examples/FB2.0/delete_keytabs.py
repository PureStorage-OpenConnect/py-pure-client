# delete the keytab with the name 'oldkeytab.1'
client.delete_keytabs(names=['oldkeytab.1'])

# delete the keytab with id '10314f42-020d-7080-8013-000ddt400090'
client.delete_keytabs(ids=['10314f42-020d-7080-8013-000ddt400090'])

# delete all keytabs that were encrypted with older aes128 ciphers
res = client.get_keytabs(filter='contains(encryption_type, "aes256")')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    items = list(res.items)
    print(items)
    for keytab in items:
        name_to_delete = keytab.name
        client.delete_keytabs(names=[name_to_delete])
