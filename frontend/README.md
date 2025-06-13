# Docker build

`VITE_BACKEND_URL` - backend URL configurable

```bash
docker build -t my-vite-app \
  --build-arg VITE_BACKEND_URL=http://localhost:3000 \
  --target production .

docker run -p 80:80 my-vite-app
```
