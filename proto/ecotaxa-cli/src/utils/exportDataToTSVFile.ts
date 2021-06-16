
export function exportDataToTSVFile(results: any, title: string, projectID: string, ...headerTitles: Array<string>): void {
  let header: string = "";
  for (let i = 0; i <  headerTitles.length; i++) {
    header += headerTitles[i];
    if (i < headerTitles.length - 1) header += "\t";
  }
  header += "\r\n";
  // *USEFUL COMMENTS*
  // https://stackoverflow.com/questions/48611671/vue-js-write-json-object-to-local-file
  // https://stackoverflow.com/questions/8847766/how-to-convert-json-to-csv-format-and-store-in-a-variable
  const data: string = header + ConvertToTSV(results);
  const blob:Blob = new Blob([data], { type: "text/plain" });
  const e:MouseEvent = document.createEvent("MouseEvents");
  const a:HTMLAnchorElement = document.createElement("a");
  a.download = title + "_" + projectID + "_";
  const today:Date = new Date();
  const date:string =
    today.getFullYear() +
    "-" +
    (today.getMonth() + 1) +
    "-" +
    today.getDate();
  const time:string = today.getHours() + "-" + today.getMinutes() + "-" + today.getSeconds();
  const dateTime:string = date + "_" + time; // better with no space in filename
  a.download += dateTime + ".tsv";
  a.href = window.URL.createObjectURL(blob);
  a.dataset.downloadurl = ["text/json", a.download, a.href].join(":");
  e.initEvent("click", true, false);
  a.dispatchEvent(e);
};

function ConvertToTSV(objArray: any): string {
  let str: string = "";
  for (let i:number = 0; i < objArray.length; i++) {
    let line:string = "";
    for (const index in objArray[i]) {
      if (line !== "") line += "\t"; // would be a "," instead of tabulation for a .csv
      line += objArray[i][index];
    }
    str += line + "\r\n";
  }
  return str;
};

