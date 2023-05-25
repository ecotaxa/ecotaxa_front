const webpack = require("webpack");
const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const ESLintPlugin = require('eslint-webpack-plugin');
const CopyPlugin = require("copy-webpack-plugin");
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const dirRoot = "dev_gui/";
const destRoot = 'appli/';
let config = {
  entry: "./src/index.js",
  mode: 'development',
  output: {
    path: path.resolve(__dirname, dirRoot + "static/gui/"),
    publicPath: '/static/gui/',
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
        test: /\.(scss)$/i,
        use: [MiniCssExtractPlugin.loader,
          {
            loader: "css-loader"
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
      "fs": false,
      "os": false,
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
    new MiniCssExtractPlugin({
      linkType: "text/css",
      filename: "./css/[name].css"
    }),
    new BundleAnalyzerPlugin(),
    new CopyPlugin({
      patterns: [{
          from: dirRoot + "../src/templates/v2",
          to: destRoot + "templates/v2"
        },
        {
          from: dirRoot + "static/gui",
          to: destRoot + "static/gui"
        },
        {
          from: dirRoot + "../src/gui",
          to: destRoot + "gui"
        },
        {
          from: dirRoot + "../src/images",
          to: destRoot + "static/gui/images"
        },
        {
          from: dirRoot + "../src/css/icons",
          to: destRoot + "static/gui/css/icons"
        }, {
          from: dirRoot + "../src/css/fonts",
          to: destRoot + "static/gui/css/fonts"
        },
      ],
    }),
  ],
  devServer: {
    port: 3000,
    hot: true,
  },
  devtool: 'eval-source-map'
}

module.exports = config;