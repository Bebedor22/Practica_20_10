FROM node:24-alpine

RUN corepack enable

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY index.html vite.config.ts tsconfig.json tsconfig.app.json tsconfig.node.json .oxlintrc.json ./
COPY src ./src

ENV VITE_PROXY_TARGET=http://backend:8000

EXPOSE 5173

CMD ["pnpm", "run", "dev", "--host", "0.0.0.0"]
