curl http://localhost:4000/v1/files \
  -H "Authorization: Bearer sk-1234" \
  -F purpose="batch" \
  -F file="@batch_requests.jsonl"