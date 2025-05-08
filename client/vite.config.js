import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            "/api": {
                target: "http://127.0.0.1:5000",
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ""),
                secure: false,
                ws: true,
            },
        },
    },
    resolve: {
        alias: [
            {
                find: "~pages",
                replacement: path.resolve(__dirname, "src/pages"),
            },
            {
                find: "~shared",
                replacement: path.resolve(__dirname, "src/shared"),
            },
        ],
    },
});
