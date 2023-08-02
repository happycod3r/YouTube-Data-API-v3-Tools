# API Errors

## Errors

### Code 403 https://youtube.googleapis.com/youtube/v3/playlists?part=snippet%2Cstatus&alt=json

Terminal output:
```bash
An error occurred: <HttpError 403 when requesting https://youtube.googleapis.com/youtube/v3/playlists?part=snippet%2Cstatus&alt=json returned "Request had insufficient authentication scopes.". 
Details: "[{'message': 'Insufficient Permission', 'domain': 'global', 'reason': 'insufficientPermissions'}]">
```

Corresponding JSON` `
```json
{
  "error": {
    "code": 403,
    "message": "The request is missing a valid API key.",
    "errors": [
      {
        "message": "The request is missing a valid API key.",
        "domain": "global",
        "reason": "forbidden"
      }
    ],
    "status": "PERMISSION_DENIED"
  }
}
```
