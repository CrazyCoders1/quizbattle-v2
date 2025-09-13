#!/bin/sh

# Replace environment variables in built files
find /usr/share/nginx/html -name "*.js" -exec sed -i "s|REACT_APP_API_URL_PLACEHOLDER|$REACT_APP_API_URL|g" {} +

# Start nginx
exec nginx -g "daemon off;"