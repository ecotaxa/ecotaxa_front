function PostDynForm(url,data) {
  if (data == null) data = {};
  var form = $('<form>').attr({
            method: 'POST',
            action: url
         }).css({
            display: 'none'
         });
  for (var key in data) {
    if (data.hasOwnProperty(key)) {
      form.append($('<input>').attr({
                  type: 'hidden',
                  name: String(key),
                  value: String(data[key])
                }));
    }
  }
  form.appendTo('body').submit();
}

function objectifyForm(formid) {
  var formArray=$("#"+formid).serializeArray();
  var returnArray = {};
  for (var i = 0; i < formArray.length; i++){
    returnArray[formArray[i]['name']] = formArray[i]['value'];
  }
  return returnArray;
}

