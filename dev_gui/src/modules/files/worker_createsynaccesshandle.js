onmessage = async (e) => {
  // Retrieve message sent to work from main script
  const message = e.data;
  const filestream = e.data.filestream;



  streamhandle.close();
};
function createStreamHandle(filestream) {
  const streamhandle = await filestream.createSyncAccessHandle();
}