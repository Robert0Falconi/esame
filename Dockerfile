# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# Copia SOLO i file del frontend
COPY frontend/package*.json ./

# Installa dipendenze
RUN npm install

# Copia tutto il frontend
COPY frontend/ .

# Copia Bootstrap Italia in public PRIMA del build
RUN mkdir -p public/bootstrap-italia && \
    cp -r node_modules/bootstrap-italia/dist public/bootstrap-italia/

# Build dell'applicazione
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Copia i file buildati
COPY --from=build /app/dist /usr/share/nginx/html

# Configurazione nginx per SPA
COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
