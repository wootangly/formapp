# Use Nginx as the base image
FROM --platform=linux/amd64 nginx:latest

# Copy static files (form) to Nginx
COPY ./index.html /usr/share/nginx/html/index.html

# Expose port 80
EXPOSE 80

