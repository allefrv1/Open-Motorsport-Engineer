FROM node:24.21.0-slim

RUN npm install --global pnpm@11.27.1 \
    && mkdir -p /workspace \
    && chown node:node /workspace

WORKDIR /workspace

USER node

COPY --chown=node:node package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY --chown=node:node frontend/package.json frontend/package.json

RUN pnpm install --frozen-lockfile

COPY --chown=node:node frontend ./frontend

EXPOSE 5173

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
    CMD node -e "fetch('http://127.0.0.1:5173').then((response) => process.exit(response.ok ? 0 : 1)).catch(() => process.exit(1))"

CMD ["pnpm", "--dir", "frontend", "exec", "vite", "--host", "0.0.0.0", "--port", "5173", "--strictPort"]
