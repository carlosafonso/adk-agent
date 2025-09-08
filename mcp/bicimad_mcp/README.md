```bash
gcloud run \
    deploy \
    --env-vars-file=run.env.yaml \
    --region=<REGION> \
    --image=<REGION>-docker.pkg.dev/<PROJECT_ID>/bicimad-mcp/bicimad-mcp:latest \
    mcp-bicimad
```
