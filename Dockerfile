FROM node:20-alpine AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN npm i -g pnpm@10 && pnpm install --frozen-lockfile
COPY . .
ENV VITE_MODE=ai
ARG VITE_AI_API=http://localhost:8000
ENV VITE_AI_API=$VITE_AI_API
RUN pnpm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
