/// <reference types="vite/client" />

// Augment Vite env types to ensure `import.meta.env` is always typed,
// even if the IDE/TS server fails to load vite/client for some reason.
declare interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  // add other public envs here if needed, all must be prefixed with VITE_
}

declare interface ImportMeta {
  readonly env: ImportMetaEnv;
}
