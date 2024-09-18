const webpack = require("webpack");
const path = require("path");
const {
  WebpackManifestPlugin
} = require('webpack-manifest-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const ESLintPlugin = require('eslint-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
let destDir = 'src';
let config = {
  mode: 'none',
  entry: "./src/index.js",
  output: {
    pathinfo: true,
    path: path.resolve(__dirname, `../appli/static/gui/${destDir}/`),
    publicPath: `/static/gui/${destDir}/`,
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
    }, ],
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
  },
  plugins: [
    new BundleAnalyzerPlugin(),
    new WebpackManifestPlugin(),
    new HtmlWebpackPlugin({
      filename: path.resolve(__dirname, '../appli/templates/v2/partials/_head.html'),
      template: path.resolve(__dirname, '../appli/templates/v2/partials/_head_template.html'),
      contenthash: true,
      inject: 'head',
    })

  ],
  devtool: 'eval-source-map'
}
module.exports = (env, argv) => {
  const rulecss = {
    test: /\.css$/i,
    include: path.resolve(__dirname, 'src'),
    exclude: /node_modules/,
    use: []
  };
  let templatecontent;
  if (argv.mode === 'production') {
    delete config.devtool;
    config.mode = argv.mode;
    config.output.filename = (pathData) => {
        return '[name].[contenthash].js';
      },
      destDir = 'dist/';
    config.output.chunkFilename = (pathData) => {
        return "[name].[contenthash].js";
      },
      destDir = 'dist/';
    /*config.output.assetModuleFilename = (pathData) => {
        return "[contenthash][ext][query]";
      },
      destDir = 'dist/';*/
    rulecss.use = [{
      loader: MiniCssExtractPlugin.loader,
      /*  options: {
          esModule: false,
        },*/
    }, {
      loader: 'css-loader',
      options: {
        importLoaders: 1,

      }
    }, "postcss-loader"];
    config.plugins.push(new MiniCssExtractPlugin({
      linkType: "text/css",
      filename: "[name].[contenthash].css"
    }));
  } else {
    config.mode = 'development';
    config.devtool = 'eval-source-map';
    destDir = 'src/';
    rulecss.use = ["style-loader",
      {
        loader: 'css-loader',
        options: {
          importLoaders: 1,

        }
      },
      'postcss-loader'
    ];
  };
  config.output.path = path.resolve(__dirname, '../appli/static/gui/' + destDir);
  config.output.publicPath = '/static/gui/' + destDir;
  config.module.rules.unshift(rulecss);
  return config;
}
//module.exports = config;