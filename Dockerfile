FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY build/web /app/build/web

# Custom serve config to fix MIME types for pygbag
RUN echo '{ \
  "headers": [ \
    { "source": "**/*.tar.gz", "headers": [{ "key": "Content-Type", "value": "application/gzip" }, { "key": "Content-Disposition", "value": "attachment" }] }, \
    { "source": "**/*.apk", "headers": [{ "key": "Content-Type", "value": "application/octet-stream" }, { "key": "Content-Disposition", "value": "attachment" }] }, \
    { "source": "**/*.js", "headers": [{ "key": "Content-Type", "value": "application/javascript" }, { "key": "Cross-Origin-Embedder-Policy", "value": "require-corp" }, { "key": "Cross-Origin-Opener-Policy", "value": "same-origin" }] }, \
    { "source": "**/*.wasm", "headers": [{ "key": "Content-Type", "value": "application/wasm" }, { "key": "Cross-Origin-Embedder-Policy", "value": "require-corp" }] }, \
    { "source": "**/*.data", "headers": [{ "key": "Content-Type", "value": "application/octet-stream" }] }, \
    { "source": "/", "headers": [{ "key": "Cross-Origin-Embedder-Policy", "value": "require-corp" }, { "key": "Cross-Origin-Opener-Policy", "value": "same-origin" }] } \
  ] \
}' > /app/serve.json

EXPOSE 3000
CMD ["serve", "-s", "build/web", "-l", "3000", "--no-clipboard", "-c", "serve.json"]