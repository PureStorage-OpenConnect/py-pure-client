from pypureclient.flashblade.FB_2_17 import FleetMemberPost, FleetMemberPostMembers, FleetMemberPostMembersMember

fleet_member_post_member=FleetMemberPostMembersMember(name='my-new-fleet-member')
fleet_key='$secret-fleet-key$'
fleet_member_post_members=FleetMemberPostMembers(member=fleet_member_post_member, key=fleet_key)
fleet_member_post=FleetMemberPost(members=[fleet_member_post_members])

# create fleet member based on fleet name
res = client.post_fleets_members(
    fleet_names=['my-fleet'],
    members=fleet_member_post)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create fleet member based on fleet id
res = client.post_fleets_members(
    fleet_ids=['635c0a0c-37ad-4f91-bad7-5224c284c2ad'],
    members=fleet_member_post
    )
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
