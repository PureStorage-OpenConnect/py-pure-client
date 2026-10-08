# API Changelog 2.57 vs. 2.58

## GET /antivirus/targets
-  endpoint added


## DELETE /antivirus/targets/icap
-  endpoint added


## GET /antivirus/targets/icap
-  endpoint added


## PATCH /antivirus/targets/icap
-  endpoint added


## POST /antivirus/targets/icap
-  endpoint added


## DELETE /antivirus/targets/icap/scanners
-  endpoint added


## GET /antivirus/targets/icap/scanners
-  endpoint added


## PATCH /antivirus/targets/icap/scanners
-  endpoint added


## POST /antivirus/targets/icap/scanners
-  endpoint added


## POST /array-connections/connection-keys
-  endpoint added


## GET /buckets
-  added the new optional 'query' request parameter 'workload_ids'
-  added the new optional 'query' request parameter 'workload_names'
-  added the optional property 'items/workload' to the response with the '200' status
-  added the optional property 'items/workload' to the response with the '207' status
-  added the optional property 'total/workload' to the response with the '200' status
-  added the optional property 'total/workload' to the response with the '207' status


## PATCH /buckets
-  added the new optional request property 'workload'
-  added the optional property 'items/workload' to the response with the '200' status


## POST /buckets
-  added the new optional request property 'workload'
-  the 'query' request parameter 'names' became optional
-  added the optional property 'items/workload' to the response with the '200' status


## DELETE /directories/policies/antivirus
-  endpoint added


## GET /directories/policies/antivirus
-  endpoint added


## POST /directories/policies/antivirus
-  endpoint added


## GET /files/antivirus
-  endpoint added


## PATCH /files/antivirus
-  endpoint added


## DELETE /policies/antivirus
-  endpoint added


## GET /policies/antivirus
-  endpoint added


## PATCH /policies/antivirus
-  endpoint added


## POST /policies/antivirus
-  endpoint added


## DELETE /policies/antivirus/members
-  endpoint added


## GET /policies/antivirus/members
-  endpoint added


## POST /policies/antivirus/members
-  endpoint added


## DELETE /policies/antivirus/rules
-  endpoint added


## GET /policies/antivirus/rules
-  endpoint added


## PATCH /policies/antivirus/rules
-  endpoint added


## POST /policies/antivirus/rules
-  endpoint added


## GET /presets/workload
-  added the optional property 'items/bucket_configurations' to the response with the '200' status
-  added the optional property 'items/lifecycle_configurations' to the response with the '200' status


## PATCH /presets/workload
-  added the optional property 'items/bucket_configurations' to the response with the '200' status
-  added the optional property 'items/lifecycle_configurations' to the response with the '200' status


## POST /presets/workload
-  added the new optional request property 'bucket_configurations'
-  added the new optional request property 'lifecycle_configurations'
-  added the optional property 'items/bucket_configurations' to the response with the '200' status
-  added the optional property 'items/lifecycle_configurations' to the response with the '200' status


## PUT /presets/workload
-  added the new optional request property 'bucket_configurations'
-  added the new optional request property 'lifecycle_configurations'
-  added the optional property 'items/bucket_configurations' to the response with the '200' status
-  added the optional property 'items/lifecycle_configurations' to the response with the '200' status


