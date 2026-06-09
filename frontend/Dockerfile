# ═══════════════════════════════════════════════════════════════
# IntelAI — React Frontend
# Stage 1: Build  |  Stage 2: Serve with nginx (ultra-fast)
# ═══════════════════════════════════════════════════════════════

# ── Stage 1: Build ───────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Cache deps
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline --quiet

# Build
COPY . .
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ── Stage 2: Serve ───────────────────────────────────────────
FROM nginx:1.27-alpine AS runner

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Optimized nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:5173/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
