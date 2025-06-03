# Environment Configuration
 
## Development Environment
**Caracteristici:**
- Ruleaza local pe masina dezvoltatorului
- `uvicorn app:app --reload --port=<ORICE_PORT>`
- File storage in director local
- Hot reload pentru dezvoltare rapida

 
## Production Environment
**Caracteristici:**
- Deployed in Kubernetes cluster
- HTTPS enabled
- Persistent Volume pentru storage
- Replici pentru availability
- Resource limits definite

 
## Diferente Cheie
1. **Security:**
   - Dev: Local-stored information
   - Prod: Server-stored information, HTTPS
 
2. **Storage:**
   - Dev: Local filesystem
   - Prod: Kubernetes Persistent Volume
 
3. **Scalability:**
   - Dev: Single instance
   - Prod: Multiple replicas
