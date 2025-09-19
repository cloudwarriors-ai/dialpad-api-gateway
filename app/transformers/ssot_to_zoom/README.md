# SSOT to Zoom Transformers

This directory will contain the transformers for converting SSOT format to Zoom format.

For the Dialpad microservice, these transformers should be copied from the Zoom microservice as they use identical logic.

## Files to Copy from Zoom Microservice

- `users_transformer.py` - SSOT Person → Zoom Users transformation
- `sites_transformer.py` - SSOT Location → Zoom Sites transformation
- `call_queues_transformer.py` - SSOT CallGroup → Zoom Call Queues transformation
- `auto_receptionists_transformer.py` - SSOT AutoAttendant → Zoom Auto Receptionists transformation

The implementation should leverage the existing transformation logic in the Zoom microservice.