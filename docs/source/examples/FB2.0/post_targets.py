from pypureclient.flashblade import TargetPost

# create a target by hostname name
name = "target"
hostname = "my.target.com"
target = TargetPost(address=hostname)
# post the target object on the array
res = client.post_targets(names=[name], target=target)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create a target by ip address
name = "target2"
address = "1.1.1.1"
target = TargetPost(address=address)
# post the target object on the array
res = client.post_targets(names=[name], target=target)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
