// from https://github.com/101arrowz/fflate/issues/48
const backpressureThreshold = 165536;
export const onBackpressure = (stream, outputStream, cb) => {
  let applyOutputBackpressure = false
  const runCb = () => {
    // Pause if either output or internal backpressure should be applied
    cb(applyOutputBackpressure || backpressureBytes > backpressureThreshold);
  }

  // Internal backpressure (for when AsyncZipDeflate is slow)

  let backpressure = [];
  let backpressureBytes = 0;
  const push = stream.push;
  stream.push = (dat, final) => {
    backpressure.push(dat.length);
    backpressureBytes += dat.length;
    runCb();
    push.call(stream, dat, final);
  }
  let ondata = stream.ondata;
  const ondataPatched = (err, dat, final) => {
    ondata.call(stream, err, dat, final);
    backpressureBytes -= backpressure.shift();
    runCb();
  }
  stream.ondata = ondataPatched;

  // Output backpressure (for when outputStream is slow)

  const write = outputStream.write;
  outputStream.write = (data) => {
    const outputNotFull = write.call(outputStream, data);
    applyOutputBackpressure = !outputNotFull;
    runCb();
  }
  stream.drain = (size) => {
    console.log('size', size)
    applyOutputBackpressure = false;
    runCb();
  }
}