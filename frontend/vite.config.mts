import {
  defineConfig,
  loadEnv
} from "vite";
import path from "node:path";


function req(name: string, v?: string) {
  if (!v) throw new Error(`[vite] Env var "${name}" is required`);
  return v;
}


function normBase(s: string) {
  return s.replace(/\/+$/, "") + "/";
}


export default defineConfig(({ mode }) => {
  const ENV_DIR = path.resolve(__dirname, "..");
  const env = loadEnv(mode, ENV_DIR, "");

  const DEV_HOST = env.VITE_DEV_HOST || "127.0.0.1";
  const DEV_PORT = Number(env.VITE_DEV_PORT || 5500);

  const N_HOST = req("NGINX_HOST", env.NGINX_HOST);
  const N_PORT = req("NGINX_PORT", env.NGINX_PORT);
  const API_BASE = normBase(`http://${N_HOST}:${N_PORT}/`);

  return {
    resolve: {
      alias: { "@": path.resolve(__dirname, "src") },
    },

    server: {
      host: DEV_HOST,
      port: DEV_PORT,
      strictPort: true,
      proxy: undefined,
    },

    define: {
      "import.meta.env.VITE_API_BASE": JSON.stringify(API_BASE),
    },

    preview: {
      host: env.VITE_HOST || "127.0.0.1",
      port: Number(env.VITE_PORT || 4173),
      strictPort: true,
    },
  };
});