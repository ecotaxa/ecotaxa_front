const webpack = require("webpack");
const path = require("path");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const ESLintPlugin = require('eslint-webpack-plugin');
const CopyPlugin = require("copy-webpack-plugin");
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const dirRoot = "/home/imev/ecotaxa/ecotaxa_dev_current/ecotaxa_front/dev_gui/src/";
const destRoot = '/home/imev/ecotaxa/ecotaxa_dev_current/ecotaxa_front/appli/';
let config = {
  entry: "./src/index.js",
  mode: 'development',
  output: {
    path: path.resolve(__dirname, destRoot + "static/gui/src/"),
    publicPath: '/static/gui/src/',
    filename: (pathData) => {
      return pathData.chunk.name === 'main' ? '[name].js' : 'modules/[name].js';
    },
    clean: true,
    //  asyncChunks: true,
  },
  module: {
    rules: [{
        test: /\.(mjs|js)$/,
        //loader: "babel-loader",
        exclude: [/\.min\.js$/, /node_modules/, /babel-helpers/],
      },
      {
        test: /\.css$/i,
        include: path.resolve(__dirname, 'src'),
        exclude: /node_modules/,
        use: [
          "style-loader",
          'css-loader',

          'postcss-loader'
        ]
      },
      {
        test: /\.html$/i,
        use: ["html-loader"],
      },
    ],
  },
  resolve: {
    fallback: {
      "fs": false,
      "os": false,
      "assert": false
    },
    alias: {
      "request$": "xhr",
    }
  },
  stats: {
    errorDetails: true
  },
  optimization: {
    minimizer: [
      new TerserPlugin(), `...`,
      new CssMinimizerPlugin(),
    ],
    minimize: true,
    //  runtimeChunk: 'single',
    /*splitChunks: {
      chunks: 'async',
      cacheGroups: {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          reuseExistingChunk: true,
        },
        modules: {
          test: /[\\/]src[\\/]js[\\/]modules[\\/]/,
          name: 'modules',
          reuseExistingChunk: true,

        }
      },

    },
*/
    /*  splitChunks: {
          chunks: 'async',
          minSize: 20000,
          minRemainingSize: 0,
          minChunks: 1,
          maxAsyncRequests: 30,
          maxInitialRequests: 30,
          enforceSizeThreshold: 50000,
          cacheGroups: {
            defaultVendors: {
              test: /[\\/]node_modules[\\/]/,
              priority: -10,
              reuseExistingChunk: true,
            },
            default: {
              minChunks: 2,
              priority: -20,
              reuseExistingChunk: true,
            },
          },
        },*/
  },
  plugins: [
    new BundleAnalyzerPlugin(),
  ],
  devtool: 'eval-source-map'
}

module.exports = config;