import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [
      vue(),
      AutoImport({
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
        directoryAsNamespace: true,
        collapseSamePrefixes: true,
      }),
    ],

    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },

    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "@/styles/variables.scss" as *;`,
          sassOptions: {
            outputStyle: 'expanded',
            sourceMap: true
          }
        },
      },
    },

    server: {
      host: '0.0.0.0',  // 允许外部访问
      port: Number(env.VITE_PORT) || 3000,
      open: false,
      proxy: {
        '/api/v1': {
          target: env.VITE_API_TARGET || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/v1/, ''),
        }
      }
    },

    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: command === 'serve',
      // 生产环境移除console
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: command !== 'serve',
          drop_debugger: command !== 'serve'
        }
      }
    }
  }
})