# Frontend Dockerfile: build SvelteKit app and serve static assets with nginx
# Use node to build the app
FROM node:20-alpine AS build
WORKDIR /app

# copy package metadata and install deps
COPY package.json package-lock.json ./
RUN npm ci --silent

# copy source and build
COPY . .

RUN npm run build

# Use nginx to serve the built static site
FROM nginx:stable-alpine
# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy the built static output produced by adapter-static into nginx
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
