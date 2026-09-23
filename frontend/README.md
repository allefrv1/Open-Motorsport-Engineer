# OME frontend

The frontend is the local React/TypeScript investigation interface accepted by ADR-0008.

## Toolchain

Plan 018 introduces:

- React 19;
- TypeScript 7;
- Vite 8;
- Vitest + jsdom;
- React Testing Library.

All package versions are resolved through the root `pnpm-lock.yaml`.

## Commands

From the repository root:

```text
pnpm --dir frontend test
pnpm --dir frontend typecheck
pnpm --dir frontend build
pnpm --dir frontend dev
```

During development, Vite proxies `/api` requests to the loopback FastAPI process at
`http://127.0.0.1:8000`. Run the API and frontend in separate terminals.

The canonical repository harness runs frontend test, typecheck and build before a substantial change is considered complete.

## Product scope

Current active plan:

`docs/plans/active/018-mvp-investigation-frontend-foundation.md`

The first product UI consumes the OME CSV comparison upload HTTP workflow.

Do not move deterministic engineering calculations into frontend code.
