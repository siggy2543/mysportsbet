# =============================================================================
# SIMPLIFIED MULTI-STAGE DOCKERFILE FOR FRONTEND
# =============================================================================

# Stage 1: Build the React application
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application with optimizations
ENV GENERATE_SOURCEMAP=false
ENV CI=true
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy the built app from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx config if it exists, otherwise use default
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (nginx default)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]