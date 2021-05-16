// vue.config.js

/**
 * @type {import('@vue/cli-service').ProjectOptions}
 */
module.exports = {
  // options...
  devServer: {
    proxy: {
      "/api": {
        target: "https://ecotaxa.obs-vlfr.fr/",
        ws: true,
        changeOrigin: true,
        onProxyReq: (proxyReq, req) => {
          // Remove session cookies which are the session b/w client and dev web server
          if ("cookie" in req.headers) {
            proxyReq.removeHeader("cookie");
          }
        },
      },
    },
  },
};
