/*! For license information please see src_modules_files_js-scandir_js.js.LICENSE.txt */
"use strict";(self.webpackChunk=self.webpackChunk||[]).push([["src_modules_files_js-scandir_js"],{"./src/modules/files/js-scandir.js":(__unused_webpack_module,__webpack_exports__,__webpack_require__)=>{eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   JsScanDir: () => (/* binding */ JsScanDir)\n/* harmony export */ });\nfunction JsScanDir(process_file = null) {\n  async function processFile(entry, callback = null) {\n    if (process_file) process_file(entry, callback);\n    else if (callback) await callback();\n  }\n\n  function stopOnError(err) {\n    console.log('err', err);\n  }\n\n  function fileType(data) {\n    const mime_type = (signature) => {\n      switch (signature) {\n        case '89504E47':\n          return 'image/png';\n        case '47494638':\n          return 'image/gif';\n        case '25504446':\n          return 'application/pdf';\n        case 'FFD8FFDB':\n        case 'FFD8FFE0':\n        case 'FFD8FFE1':\n          return 'image/jpeg';\n        case '504B0304':\n          return 'application/zip';\n        case 'EFBBBF22':\n          return 'text/tsv'; //'text/tab-separated-values';\n        default:\n          console.log('unknownsign', signature)\n          return 'unknown';\n      }\n    }\n    const uint = new Uint8Array(data);\n    let bytes = []\n    for (let i = 0; i < 4; i++) {\n      bytes.push(uint[i].toString(16))\n    }\n    data = bytes.join('').toUpperCase();\n    return {\n      input: uint,\n      mimetype: mime_type(data)\n    };\n  }\n\n\n  async function readDirectory(dir, oncomplete) {\n    let errored = false;\n    let direntries = [];\n    const on_error = onerror ? onerror : (err) => {\n      console.log('on_error', err)\n      if (!errored) {\n        errored = true;\n      }\n    };\n    const reader = dir.createReader();\n    const on_read = async function(ents) {\n      if (ents.length && !errored) {\n        direntries = [...direntries, ...ents];\n        await reader.readEntries(on_read, on_error);\n      } else if (!errored) {\n        const complete = async function() {\n          if (oncomplete && direntries.length === 0) {\n            oncomplete();\n          } else {\n            const entry = direntries.shift();\n            if (entry.isDirectory) await readDirectory(entry, complete);\n            else await processFile(entry, complete);\n          }\n        }\n        await complete();\n      } else {\n        console.log('treat error readdir');\n      }\n    }\n    await reader.readEntries(on_read, on_error);\n  }\n\n  async function processEntries(entries, path, oncomplete) {\n    // showDirectoryPicker\n    const complete = async () => {\n      if (entries.length) {\n        const entry = await entries.shift();\n        const nestedpath = `${path}/${entry.name}`;\n        const kind = (entry.kind) ? entry.kind : (entry instanceof File) ? \"file\" : \"directory\";\n        if (kind === \"file\") {\n          if (!entry.webkitRelativePath) Object.defineProperty(entry, \"webkitRelativePath\", {\n            configurable: true,\n            enumerable: true,\n            get: () => nestedpath,\n          });\n          if (entry instanceof File) entry.file = async (func) => {\n            await func(entry, nestedpath);\n          }\n          else entry.file = async (func) => {\n            entry.getFile().then(async file => {\n              await func(file, nestedpath);\n            });\n          }\n          await processFile(entry, complete);\n        } else if (kind === \"directory\") {\n          const direntries = await Array.fromAsync(entry.values());\n          await processEntries(direntries, nestedpath, complete);\n        }\n      } else if (oncomplete) oncomplete();\n    }\n    await complete();\n  }\n  return {\n    processFile,\n    processEntries,\n    readDirectory\n  }\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvbW9kdWxlcy9maWxlcy9qcy1zY2FuZGlyLmpzIiwibWFwcGluZ3MiOiI7Ozs7QUFBTztBQUNQO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLDZCQUE2QjtBQUM3QjtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLG9CQUFvQixPQUFPO0FBQzNCO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7OztBQUdBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxRQUFRO0FBQ1I7QUFDQTtBQUNBO0FBQ0EsWUFBWTtBQUNaO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLFFBQVE7QUFDUjtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSw4QkFBOEIsS0FBSyxHQUFHLFdBQVc7QUFDakQ7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EsV0FBVztBQUNYO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLGFBQWE7QUFDYjtBQUNBO0FBQ0EsVUFBVTtBQUNWO0FBQ0E7QUFDQTtBQUNBLFFBQVE7QUFDUjtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9zcmMvbW9kdWxlcy9maWxlcy9qcy1zY2FuZGlyLmpzPzkyMjYiXSwic291cmNlc0NvbnRlbnQiOlsiZXhwb3J0IGZ1bmN0aW9uIEpzU2NhbkRpcihwcm9jZXNzX2ZpbGUgPSBudWxsKSB7XG4gIGFzeW5jIGZ1bmN0aW9uIHByb2Nlc3NGaWxlKGVudHJ5LCBjYWxsYmFjayA9IG51bGwpIHtcbiAgICBpZiAocHJvY2Vzc19maWxlKSBwcm9jZXNzX2ZpbGUoZW50cnksIGNhbGxiYWNrKTtcbiAgICBlbHNlIGlmIChjYWxsYmFjaykgYXdhaXQgY2FsbGJhY2soKTtcbiAgfVxuXG4gIGZ1bmN0aW9uIHN0b3BPbkVycm9yKGVycikge1xuICAgIGNvbnNvbGUubG9nKCdlcnInLCBlcnIpO1xuICB9XG5cbiAgZnVuY3Rpb24gZmlsZVR5cGUoZGF0YSkge1xuICAgIGNvbnN0IG1pbWVfdHlwZSA9IChzaWduYXR1cmUpID0+IHtcbiAgICAgIHN3aXRjaCAoc2lnbmF0dXJlKSB7XG4gICAgICAgIGNhc2UgJzg5NTA0RTQ3JzpcbiAgICAgICAgICByZXR1cm4gJ2ltYWdlL3BuZyc7XG4gICAgICAgIGNhc2UgJzQ3NDk0NjM4JzpcbiAgICAgICAgICByZXR1cm4gJ2ltYWdlL2dpZic7XG4gICAgICAgIGNhc2UgJzI1NTA0NDQ2JzpcbiAgICAgICAgICByZXR1cm4gJ2FwcGxpY2F0aW9uL3BkZic7XG4gICAgICAgIGNhc2UgJ0ZGRDhGRkRCJzpcbiAgICAgICAgY2FzZSAnRkZEOEZGRTAnOlxuICAgICAgICBjYXNlICdGRkQ4RkZFMSc6XG4gICAgICAgICAgcmV0dXJuICdpbWFnZS9qcGVnJztcbiAgICAgICAgY2FzZSAnNTA0QjAzMDQnOlxuICAgICAgICAgIHJldHVybiAnYXBwbGljYXRpb24vemlwJztcbiAgICAgICAgY2FzZSAnRUZCQkJGMjInOlxuICAgICAgICAgIHJldHVybiAndGV4dC90c3YnOyAvLyd0ZXh0L3RhYi1zZXBhcmF0ZWQtdmFsdWVzJztcbiAgICAgICAgZGVmYXVsdDpcbiAgICAgICAgICBjb25zb2xlLmxvZygndW5rbm93bnNpZ24nLCBzaWduYXR1cmUpXG4gICAgICAgICAgcmV0dXJuICd1bmtub3duJztcbiAgICAgIH1cbiAgICB9XG4gICAgY29uc3QgdWludCA9IG5ldyBVaW50OEFycmF5KGRhdGEpO1xuICAgIGxldCBieXRlcyA9IFtdXG4gICAgZm9yIChsZXQgaSA9IDA7IGkgPCA0OyBpKyspIHtcbiAgICAgIGJ5dGVzLnB1c2godWludFtpXS50b1N0cmluZygxNikpXG4gICAgfVxuICAgIGRhdGEgPSBieXRlcy5qb2luKCcnKS50b1VwcGVyQ2FzZSgpO1xuICAgIHJldHVybiB7XG4gICAgICBpbnB1dDogdWludCxcbiAgICAgIG1pbWV0eXBlOiBtaW1lX3R5cGUoZGF0YSlcbiAgICB9O1xuICB9XG5cblxuICBhc3luYyBmdW5jdGlvbiByZWFkRGlyZWN0b3J5KGRpciwgb25jb21wbGV0ZSkge1xuICAgIGxldCBlcnJvcmVkID0gZmFsc2U7XG4gICAgbGV0IGRpcmVudHJpZXMgPSBbXTtcbiAgICBjb25zdCBvbl9lcnJvciA9IG9uZXJyb3IgPyBvbmVycm9yIDogKGVycikgPT4ge1xuICAgICAgY29uc29sZS5sb2coJ29uX2Vycm9yJywgZXJyKVxuICAgICAgaWYgKCFlcnJvcmVkKSB7XG4gICAgICAgIGVycm9yZWQgPSB0cnVlO1xuICAgICAgfVxuICAgIH07XG4gICAgY29uc3QgcmVhZGVyID0gZGlyLmNyZWF0ZVJlYWRlcigpO1xuICAgIGNvbnN0IG9uX3JlYWQgPSBhc3luYyBmdW5jdGlvbihlbnRzKSB7XG4gICAgICBpZiAoZW50cy5sZW5ndGggJiYgIWVycm9yZWQpIHtcbiAgICAgICAgZGlyZW50cmllcyA9IFsuLi5kaXJlbnRyaWVzLCAuLi5lbnRzXTtcbiAgICAgICAgYXdhaXQgcmVhZGVyLnJlYWRFbnRyaWVzKG9uX3JlYWQsIG9uX2Vycm9yKTtcbiAgICAgIH0gZWxzZSBpZiAoIWVycm9yZWQpIHtcbiAgICAgICAgY29uc3QgY29tcGxldGUgPSBhc3luYyBmdW5jdGlvbigpIHtcbiAgICAgICAgICBpZiAob25jb21wbGV0ZSAmJiBkaXJlbnRyaWVzLmxlbmd0aCA9PT0gMCkge1xuICAgICAgICAgICAgb25jb21wbGV0ZSgpO1xuICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICBjb25zdCBlbnRyeSA9IGRpcmVudHJpZXMuc2hpZnQoKTtcbiAgICAgICAgICAgIGlmIChlbnRyeS5pc0RpcmVjdG9yeSkgYXdhaXQgcmVhZERpcmVjdG9yeShlbnRyeSwgY29tcGxldGUpO1xuICAgICAgICAgICAgZWxzZSBhd2FpdCBwcm9jZXNzRmlsZShlbnRyeSwgY29tcGxldGUpO1xuICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICBhd2FpdCBjb21wbGV0ZSgpO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgY29uc29sZS5sb2coJ3RyZWF0IGVycm9yIHJlYWRkaXInKTtcbiAgICAgIH1cbiAgICB9XG4gICAgYXdhaXQgcmVhZGVyLnJlYWRFbnRyaWVzKG9uX3JlYWQsIG9uX2Vycm9yKTtcbiAgfVxuXG4gIGFzeW5jIGZ1bmN0aW9uIHByb2Nlc3NFbnRyaWVzKGVudHJpZXMsIHBhdGgsIG9uY29tcGxldGUpIHtcbiAgICAvLyBzaG93RGlyZWN0b3J5UGlja2VyXG4gICAgY29uc3QgY29tcGxldGUgPSBhc3luYyAoKSA9PiB7XG4gICAgICBpZiAoZW50cmllcy5sZW5ndGgpIHtcbiAgICAgICAgY29uc3QgZW50cnkgPSBhd2FpdCBlbnRyaWVzLnNoaWZ0KCk7XG4gICAgICAgIGNvbnN0IG5lc3RlZHBhdGggPSBgJHtwYXRofS8ke2VudHJ5Lm5hbWV9YDtcbiAgICAgICAgY29uc3Qga2luZCA9IChlbnRyeS5raW5kKSA/IGVudHJ5LmtpbmQgOiAoZW50cnkgaW5zdGFuY2VvZiBGaWxlKSA/IFwiZmlsZVwiIDogXCJkaXJlY3RvcnlcIjtcbiAgICAgICAgaWYgKGtpbmQgPT09IFwiZmlsZVwiKSB7XG4gICAgICAgICAgaWYgKCFlbnRyeS53ZWJraXRSZWxhdGl2ZVBhdGgpIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShlbnRyeSwgXCJ3ZWJraXRSZWxhdGl2ZVBhdGhcIiwge1xuICAgICAgICAgICAgY29uZmlndXJhYmxlOiB0cnVlLFxuICAgICAgICAgICAgZW51bWVyYWJsZTogdHJ1ZSxcbiAgICAgICAgICAgIGdldDogKCkgPT4gbmVzdGVkcGF0aCxcbiAgICAgICAgICB9KTtcbiAgICAgICAgICBpZiAoZW50cnkgaW5zdGFuY2VvZiBGaWxlKSBlbnRyeS5maWxlID0gYXN5bmMgKGZ1bmMpID0+IHtcbiAgICAgICAgICAgIGF3YWl0IGZ1bmMoZW50cnksIG5lc3RlZHBhdGgpO1xuICAgICAgICAgIH1cbiAgICAgICAgICBlbHNlIGVudHJ5LmZpbGUgPSBhc3luYyAoZnVuYykgPT4ge1xuICAgICAgICAgICAgZW50cnkuZ2V0RmlsZSgpLnRoZW4oYXN5bmMgZmlsZSA9PiB7XG4gICAgICAgICAgICAgIGF3YWl0IGZ1bmMoZmlsZSwgbmVzdGVkcGF0aCk7XG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICB9XG4gICAgICAgICAgYXdhaXQgcHJvY2Vzc0ZpbGUoZW50cnksIGNvbXBsZXRlKTtcbiAgICAgICAgfSBlbHNlIGlmIChraW5kID09PSBcImRpcmVjdG9yeVwiKSB7XG4gICAgICAgICAgY29uc3QgZGlyZW50cmllcyA9IGF3YWl0IEFycmF5LmZyb21Bc3luYyhlbnRyeS52YWx1ZXMoKSk7XG4gICAgICAgICAgYXdhaXQgcHJvY2Vzc0VudHJpZXMoZGlyZW50cmllcywgbmVzdGVkcGF0aCwgY29tcGxldGUpO1xuICAgICAgICB9XG4gICAgICB9IGVsc2UgaWYgKG9uY29tcGxldGUpIG9uY29tcGxldGUoKTtcbiAgICB9XG4gICAgYXdhaXQgY29tcGxldGUoKTtcbiAgfVxuICByZXR1cm4ge1xuICAgIHByb2Nlc3NGaWxlLFxuICAgIHByb2Nlc3NFbnRyaWVzLFxuICAgIHJlYWREaXJlY3RvcnlcbiAgfVxufSJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/modules/files/js-scandir.js\n")}}]);