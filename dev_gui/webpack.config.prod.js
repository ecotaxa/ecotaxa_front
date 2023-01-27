const webpack = require("webpack");
const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const ESLintPlugin = require('eslint-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const dirRoot = "../appli/";
let config = {
  entry: "./src/index.js",
  mode: 'production',
  output: {
    path: path.resolve(__dirname, dirRoot + "static/gui/"),
    publicPath: '',
    filename: './js/main.js',
    clean: true,
  },
  module: {
    rules: [{
        test: /\.(mjs|js)$/,
        //loader: "babel-loader",
        exclude: [/\.min\.js$/, /node_modules/, /babel-helpers/],
      },
      {
        test: /\.scss$/i,
        use: [MiniCssExtractPlugin.loader,
          {
            loader: "css-loader",
            options: {

              sourceMap: true
            }
          },
        ],
      },
      {
        test: /\.css$/i,
        include: path.resolve(__dirname, 'src'),
        exclude: /node_modules/,
        use: [
          'style-loader',
          {
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
      new CssMinimizerPlugin(),
    ],
    minimize: true
  },
  plugins: [
    new MiniCssExtractPlugin({
      linkType: "text/css",
      filename: "./css/[name].css"
    }),
  ],
}

module.exports = config;