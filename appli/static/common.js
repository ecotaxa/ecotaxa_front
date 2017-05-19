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

