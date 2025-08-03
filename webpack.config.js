import path from 'path';
import nodeExternals from 'webpack-node-externals';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default {
  target: 'node',
  mode: 'production',
  entry: './dist/cli/index.js',
  output: {
    path: path.resolve(__dirname, 'bundle'),
    filename: 'cli.js',
    clean: true
  },
  externals: [
    nodeExternals({
      // Keep heavy dependencies external to enable lazy loading
      allowlist: [
        // Include small, commonly used packages
        'chalk',
        'commander',
        'ora'
      ]
    })
  ],
  optimization: {
    usedExports: true,
    sideEffects: false,
    minimize: true
  },
  resolve: {
    extensions: ['.js', '.ts', '.json']
  },
  stats: {
    modules: false,
    chunks: true,
    chunkModules: false,
    assets: true,
    assetsSort: 'size'
  }
};