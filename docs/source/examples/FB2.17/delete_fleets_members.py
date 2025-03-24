# delete fleet member by name
res = client.delete_fleets_members(member_names=['my-fleet-member'])
print(res)

# delete fleet member by id
res = client.delete_fleets_members(member_ids=['635c0a0c-37ad-4f91-bad7-5224c284c2ad'])
print(res)

# delete fleet member by name unilaterally
res = client.delete_fleets_members(member_names=['my-fleet-member'], unreachable=True)
