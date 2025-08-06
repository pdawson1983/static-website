# Fixed Dockerfile for Python static site generator
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements if it exists
COPY requirements.txt* ./

# Install Python dependencies
RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    else \
        echo "No requirements.txt found, skipping pip install"; \
    fi

# Copy source code
COPY . .

# Generate static site
RUN echo "Running Python static site generator..." && \
    ls -la && \
    ./build.sh && \
    echo "Generation complete. Contents:" && ls -la

# Production stage with nginx
FROM nginx:alpine

# Create custom nginx config
RUN echo 'server {' > /etc/nginx/conf.d/default.conf && \
    echo '    listen 80;' >> /etc/nginx/conf.d/default.conf && \
    echo '    server_name _;' >> /etc/nginx/conf.d/default.conf && \
    echo '    port_in_redirect on;' >> /etc/nginx/conf.d/default.conf && \
    echo '    root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    index index.html index.htm;' >> /etc/nginx/conf.d/default.conf && \
    echo '    gzip on;' >> /etc/nginx/conf.d/default.conf && \
    echo '    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;' >> /etc/nginx/conf.d/default.conf && \
    echo '    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {' >> /etc/nginx/conf.d/default.conf && \
    echo '        expires 1y;' >> /etc/nginx/conf.d/default.conf && \
    echo '        add_header Cache-Control "public, immutable";' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '    location / {' >> /etc/nginx/conf.d/default.conf && \
    echo '        if ($request_uri !~ "/$") {' >> /etc/nginx/conf.d/default.conf && \
    echo '            rewrite ^(.*[^/])$ $scheme://$http_host$1/ permanent;' >> /etc/nginx/conf.d/default.conf && \
    echo '        }' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '}' >> /etc/nginx/conf.d/default.conf

# Copy files from builder
COPY --from=builder /app /tmp/app

# Organize web files and create fallback
RUN echo "Organizing web files..." && \
    mkdir -p /usr/share/nginx/html && \
    if [ -d /tmp/app/dist ] && [ "$(ls -A /tmp/app/dist 2>/dev/null)" ]; then \
        echo "Found dist/ directory" && \
        cp -r /tmp/app/dist/* /usr/share/nginx/html/; \
    elif [ -d /tmp/app/build ] && [ "$(ls -A /tmp/app/build 2>/dev/null)" ]; then \
        echo "Found build/ directory" && \
        cp -r /tmp/app/build/* /usr/share/nginx/html/; \
    elif [ -d /tmp/app/output ] && [ "$(ls -A /tmp/app/output 2>/dev/null)" ]; then \
        echo "Found output/ directory" && \
        cp -r /tmp/app/output/* /usr/share/nginx/html/; \
    elif [ -d /tmp/app/public ] && [ "$(ls -A /tmp/app/public 2>/dev/null)" ]; then \
        echo "Found public/ directory" && \
        cp -r /tmp/app/public/* /usr/share/nginx/html/; \
    elif [ -d /tmp/app/_site ] && [ "$(ls -A /tmp/app/_site 2>/dev/null)" ]; then \
        echo "Found _site/ directory" && \
        cp -r /tmp/app/_site/* /usr/share/nginx/html/; \
    elif [ -d /tmp/app/site ] && [ "$(ls -A /tmp/app/site 2>/dev/null)" ]; then \
        echo "Found site/ directory" && \
        cp -r /tmp/app/site/* /usr/share/nginx/html/; \
    else \
        echo "No standard output directory found, copying relevant files from root" && \
        find /tmp/app -maxdepth 1 -name "*.html" -exec cp {} /usr/share/nginx/html/ \; && \
        find /tmp/app -maxdepth 1 -name "*.css" -exec cp {} /usr/share/nginx/html/ \; && \
        find /tmp/app -maxdepth 1 -name "*.js" -exec cp {} /usr/share/nginx/html/ \; && \
        find /tmp/app -maxdepth 1 -type d -name "css" -exec cp -r {} /usr/share/nginx/html/ \; && \
        find /tmp/app -maxdepth 1 -type d -name "js" -exec cp -r {} /usr/share/nginx/html/ \; && \
        find /tmp/app -maxdepth 1 -type d -name "images" -exec cp -r {} /usr/share/nginx/html/ \; && \
        find /tmp/app -maxdepth 1 -type d -name "img" -exec cp -r {} /usr/share/nginx/html/ \;; \
    fi

# Clean up Python files and create fallback index.html
RUN rm -rf /tmp/app && \
    find /usr/share/nginx/html -name "*.py" -delete 2>/dev/null || true && \
    find /usr/share/nginx/html -name "*.pyc" -delete 2>/dev/null || true && \
    find /usr/share/nginx/html -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/share/nginx/html -name "requirements.txt" -delete 2>/dev/null || true && \
    if [ ! -f /usr/share/nginx/html/index.html ]; then \
        echo "Creating default index.html..." && \
        echo '<!DOCTYPE html>' > /usr/share/nginx/html/index.html && \
        echo '<html lang="en">' >> /usr/share/nginx/html/index.html && \
        echo '<head>' >> /usr/share/nginx/html/index.html && \
        echo '    <meta charset="UTF-8">' >> /usr/share/nginx/html/index.html && \
        echo '    <meta name="viewport" content="width=device-width, initial-scale=1.0">' >> /usr/share/nginx/html/index.html && \
        echo '    <title>Static Website</title>' >> /usr/share/nginx/html/index.html && \
        echo '    <style>' >> /usr/share/nginx/html/index.html && \
        echo '        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }' >> /usr/share/nginx/html/index.html && \
        echo '        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }' >> /usr/share/nginx/html/index.html && \
        echo '        h1 { color: #333; border-bottom: 3px solid #007acc; padding-bottom: 10px; }' >> /usr/share/nginx/html/index.html && \
        echo '        p { color: #666; line-height: 1.6; }' >> /usr/share/nginx/html/index.html && \
        echo '        .info { background: #e7f3ff; padding: 15px; border-left: 4px solid #007acc; margin: 20px 0; }' >> /usr/share/nginx/html/index.html && \
        echo '    </style>' >> /usr/share/nginx/html/index.html && \
        echo '</head>' >> /usr/share/nginx/html/index.html && \
        echo '<body>' >> /usr/share/nginx/html/index.html && \
        echo '    <div class="container">' >> /usr/share/nginx/html/index.html && \
        echo '        <h1>Welcome to Your Static Website! 🚀</h1>' >> /usr/share/nginx/html/index.html && \
        echo '        <div class="info">' >> /usr/share/nginx/html/index.html && \
        echo '            <strong>Success!</strong> Your Python static site generator has been containerized and is running with Nginx.' >> /usr/share/nginx/html/index.html && \
        echo '        </div>' >> /usr/share/nginx/html/index.html && \
        echo '        <p>This default page appears because no index.html was found in your generated output.</p>' >> /usr/share/nginx/html/index.html && \
        echo '        <p>Your Python generator may have created files in a different location or with a different name.</p>' >> /usr/share/nginx/html/index.html && \
        echo '        <p>Generated by Jenkins Pipeline</p>' >> /usr/share/nginx/html/index.html && \
        echo '    </div>' >> /usr/share/nginx/html/index.html && \
        echo '</body>' >> /usr/share/nginx/html/index.html && \
        echo '</html>' >> /usr/share/nginx/html/index.html; \
    fi && \
    echo "Final web files:" && \
    ls -la /usr/share/nginx/html/

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]