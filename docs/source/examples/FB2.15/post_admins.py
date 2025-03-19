from pypureclient.flashblade.FB_2_15 import AdminPost, ReferenceWritable

password = 'FAKEnewpaSsword'
public_key = ('ssh-rsa EXAMPLEzaC1yc2EAAAADAQABAAABAQDN1fshdvABLD/f2mkAUqkcUMKPsS+Os3omYFwe3G2Adxc'
              'enBY+kLmbPXjiC9t4UDob3RiYu6HkDC2xvu8yLhlQTtsjCac2BkePJa/OTxttwY5G6OyYqWjmSmX9D6GZ13'
              'CRr/rSxjXYo/2GE/0xyv27/Z+ikxjs6rzXXOhdxJ6hY1jD1D8+fHVxhr8+n6Zbod8and0rlgmarfRoRYlLh'
              'GoRSCxNyOi6bG5ugrlIEXi8JZr8CpztGp/8WTa82XCSClFJPteC/5vLvwPGxwOraZ/BJngBPbmeeloN5lBl'
              'W0KAndRqwNZcDBt8JnGioPd0Kv+SNufwR4nHCv8NgEXAMPLE')
NEW_ROLE_NAME = 'array_admin'
role_reference = ReferenceWritable(name=NEW_ROLE_NAME)
myAdmin = AdminPost(password=password, role=role_reference)
res = client.post_admins(names=['new-admin-1'], admin=myAdmin)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

myAdmin = AdminPost(password=password, public_key=public_key, role=role_reference)
res = client.post_admins(names=['new-admin-2'], admin=myAdmin)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields:
# See section "Common Fields" for examples
