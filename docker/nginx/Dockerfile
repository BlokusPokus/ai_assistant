# Multi-stage build for optimization
FROM nginx:alpine AS base

# Install required packages
RUN apk add --no-cache openssl curl

# Copy configurations
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/
COPY mime.types /etc/nginx/mime.types

# Create necessary directories and set permissions
RUN mkdir -p /var/cache/nginx /var/log/nginx /etc/nginx/ssl /run && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /etc/nginx/ssl /run && \
    chmod -R 755 /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /etc/nginx/ssl /run

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1 