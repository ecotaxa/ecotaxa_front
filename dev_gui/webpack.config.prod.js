const webpack = require("webpack");
const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
//const ESLintPlugin = require('eslint-webpack-plugin');
//const CopyPlugin = require("copy-webpack-plugin");
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const dirRoot = "/home/imev/ecotaxa/ecotaxa_dev_current/ecotaxa_front/dev_gui/src/";
const destRoot = '/home/imev/ecotaxa/ecotaxa_dev_current/ecotaxa_front/appli/';
let config = {
  entry: "./src/index.js",
  mode: 'production',
  output: {
    path: path.resolve(__dirname, destRoot + "static/gui/dist/"),
    publicPath: '/static/gui/dist/',
    filename: (pathData) => {
      return pathData.chunk.name === 'main' ? '[name].[contenthash].js' : 'modules/[name].[contenthash].js';
    },
    clean: true,
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
        use: [{
            loader: MiniCssExtractPlugin.loader,
            options: {
              esModule: false,
            },
          },
          {
            loader: 'css-loader',
            options: {
              importLoaders: 1
            }
          },
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
      fs: false,
      os: false, // the solution
      "assert": false
    },

    alias: {
      "request$": "xhr"
    }
  },
  stats: {
    errorDetails: true
  },
  optimization: {
    minimizer: [
      new TerserPlugin(), `...`,
      new CssMinimizerPlugin({
        test: /\.css$/i,
      }),
    ],
    minimize: true,

  },
  devtool: 'source-map',
  plugins: [
    new MiniCssExtractPlugin({
      linkType: "text/css",
      filename: "./css/[name].[contenthash].css"
    }),

  ],
}

module.exports = config;