# post the support diagnostics
res = client.post_support_diagnostics(analysis_period_start_time=0, analysis_period_end_time=0)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# See section "Common Fields" for examples
