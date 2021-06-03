// vue.config.js

/**
 * @type {import('@vue/cli-service').ProjectOptions}
 */
module.exports = {
  // options...
  publicPath: process.env.NODE_ENV === "production" ? "/front/" : "/",
  devServer: {
    // https://webpack.js.org/configuration/dev-server/#devserverhistoryapifallback
    historyApiFallback: true,
    proxy: {
      "/api": {
        target: "https://ecotaxa.obs-vlfr.fr/",
        ws: true,
        changeOrigin: true,
        onProxyReq: (proxyReq, req) => {
          // Remove session cookies which are the session b/w client and dev web server
          //if ("cookie" in req.headers) {
            proxyReq.removeHeader("cookie");
            const session_cookie =
              "eyJfZnJlc2giOmZhbHNlLCJ1c2VyX2lkIjoiMTE2NSJ9.YK9o1w.7chqkCsts-HRDBv87g-jLmp0uA8";
            proxyReq.setHeader("Authorization", "Bearer " + session_cookie);
          //}
        }
      },
    },
  },
}
