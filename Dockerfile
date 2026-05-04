FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY build/web /app/build/web
EXPOSE 3000
CMD ["serve", "-s", "build/web", "-l", "3000", "--no-clipboard"]