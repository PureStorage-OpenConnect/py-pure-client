from pypureclient.flashblade import AdminPatch

# change password
myAdmin = AdminPatch(old_password='thisWASanOLDpasSwOrD', password='FAKEnewpaSsword')
res = client.patch_admins(names=['pureuser'], admin=myAdmin)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Set a public key for login via SSH
myAdmin = AdminPatch(public_key='ssh-rsa EXAMPLEzaC1yc2EAAAADAQABAAABAQDN1fshdvABLD/f2mkAUqkcUMKPsS+Os3omYFwe3G2Adxc'
                           'enBY+kLmbPXjiC9t4UDob3RiYu6HkDC2xvu8yLhlQTtsjCac2BkePJa/OTxttwY5G6OyYqWjmSmX9D6GZ13'
                           'CRr/rSxjXYo/2GE/0xyv27/Z+ikxjs6rzXXOhdxJ6hY1jD1D8+fHVxhr8+n6Zbod8and0rlgmarfRoRYlLh'
                           'GoRSCxNyOi6bG5ugrlIEXi8JZr8CpztGp/8WTa82XCSClFJPteC/5vLvwPGxwOraZ/BJngBPbmeeloN5lBl'
                           'W0KAndRqwNZcDBt8JnGioPd0Kv+SNufwR4nHCv8NgEXAMPLE')
res = client.patch_admins(names=['pureuser'], admin=myAdmin)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
