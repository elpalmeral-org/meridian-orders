# syntax=docker/dockerfile:1
# Frontend de Meridian Orders · build con Node y servido por nginx sin privilegios (puerto 8080).
# Las imágenes base se fijan por digest en F2.4 (Dependabot las mantendrá al día).

FROM node:24-alpine AS build
WORKDIR /app
# 1) Dependencias (capa cacheable mientras no cambie package-lock.json)
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
# 2) Código y build de producción
COPY . .
RUN npx ng build --configuration production

FROM nginxinc/nginx-unprivileged:1.31-alpine
LABEL org.opencontainers.image.source="https://github.com/elpalmeral-org/meridian-orders" \
      org.opencontainers.image.description="Meridian Orders · frontend (Angular)"
# La imagen base se publica cada cierto tiempo y sus paquetes de Alpine van por detrás de los
# parches de seguridad: se aplican al construir. curl no se usa (el healthcheck lo hace
# Kubernetes por HTTP), así que se elimina junto con sus librerías.
USER 0
RUN apk upgrade --no-cache \
 && apk del --no-cache curl
USER 101
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
EXPOSE 8080
