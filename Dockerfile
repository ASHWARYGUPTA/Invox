# ============================================================
# Invox Frontend - Next.js Dockerfile
# ============================================================

FROM node:20-slim AS base

# Install pnpm
RUN npm install -g pnpm

WORKDIR /app

# ---- Dependencies Stage ----
FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# ---- Builder Stage ----
FROM base AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the Next.js app
# Pass build-time env vars that Next.js needs at build time
ARG NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL

RUN pnpm build

# ---- Runner Stage (Production) ----
FROM node:20-slim AS runner
WORKDIR /app

ENV NODE_ENV=production

# Add non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["node", "server.js"]
