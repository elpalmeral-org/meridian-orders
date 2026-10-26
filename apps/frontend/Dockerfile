# syntax=docker/dockerfile:1
# Frontend de Meridian Orders · build con Node y servido por nginx sin privilegios (puerto 8080).
# Las imágenes base se fijan por digest en F2.4 (Dependabot las mantendrá al día).

FROM node:26-alpine AS build
WORKDIR /app
# 1) Dependencias (capa cacheable mientras no cambie package-lock.json)
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
# 2) Código y build de producción
COPY . .
RUN npx ng build --configuration production

FROM nginxinc/nginx-unprivileged:1.29-alpine
LABEL org.opencontainers.image.source="https://github.com/elpalmeral-org/meridian-orders" \
      org.opencontainers.image.description="Meridian Orders · frontend (Angular)"
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
EXPOSE 8080
# La imagen base ya corre como usuario sin privilegios (uid 101).
