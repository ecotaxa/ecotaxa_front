function PostDynForm(url, data) {
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
    var formArray = $("#" + formid).serializeArray();
    var returnArray = {};
    for (var i = 0; i < formArray.length; i++) {
        returnArray[formArray[i]['name']] = formArray[i]['value'];
    }
    return returnArray;
}


function AtdSetWaitingMessage(Target, Message) {
    if (Message === undefined)
        Message = 'Loading ...';
    return $(Target).html("<div style='width:300px;border-radius: 4px;border: 1px solid #888; margin: auto;'><i class='fa fa-spinner fa-spin fa-3x fa-fw' style='vertical-align: middle;'></i> " + Message + "</div>");
}

function AtdSetWaitAndLoad(Target, url, loadparam, Message) {
    AtdSetWaitingMessage(Target, Message);
    $(Target).load(url, loadparam);
}

function At2PopupIsTop(zindex) {
    var intzindex = 1001 + parseInt(zindex) * 10;
    var Lst = $('.At2PopupWindowContainer');
    for (var k = 0; k < Lst.length; k++) {
        if (parseInt($(Lst[k]).css('z-index')) > intzindex)
            if ($(Lst[k]).css('display') !== "none")
                return false;
    }
    return true;
}

function At2PopupOpen(index, titre, contenu) {
    var zindex = (index).toString();
    At2PopupCreateIfNeeded(index);
    if (titre !== undefined)
        $("#At2PopupWindow" + zindex + " .At2PopupHeader").html(titre);
    if (contenu !== undefined)
        $("#At2PopupWindow" + zindex + " .At2PopupContent").html(contenu);
    document.documentElement.scrollTop = 0;
    $('.At2PopupMask').css('height', '');
    var winHeight = Math.max($(window).height(), $('body').height());
    $('.At2PopupMask').css('height', winHeight);
    $('#At2PopupMask' + zindex + ',#At2PopupWindow' + zindex).show();
    $(document).on('keydown.At2PopupWindow' + zindex, function (e) {
        if (e.which === 27) {
            if (At2PopupIsTop(zindex)) {
                At2PopupClose(index);
                e.stopImmediatePropagation();
            }
        }
    });
}

function At2PopupClose(index) {
    var zindex = (index).toString();
    $('#At2PopupMask' + zindex + ',#At2PopupWindow' + zindex).hide();
    $(document).off('keydown.At2PopupWindow' + zindex);
}

function At2PopupWaitOpenLoad(index, url, titre, loadparam) {
    var zindex = (index).toString();
    At2PopupCreateIfNeeded(index);
    if (titre !== undefined)
        $("#At2PopupWindow" + zindex + " .At2PopupHeader").html(titre);
    AtdSetWaitingMessage("#At2PopupWindow" + zindex + " .At2PopupContent");
    At2PopupOpen(zindex);
    $("#At2PopupWindow" + zindex + " .At2PopupContent").load(url, loadparam,
        function (response, status, xhr) {
            if (status == "error") {
                $("#At2PopupWindow" + zindex + " .At2PopupContent").html(xhr.status + " " + xhr.statusText);
            }
        });
}

function At2PopupCreateIfNeeded(index) {
    if ($('#At2PopupWindow' + index.toString()).length > 0) return;
    var zindex = 1000 + index * 10;
    var zindex_1 = zindex + 1;
    var txt = '<div id="At2PopupMask' + index.toString() + '" style="z-index:' + zindex.toString() + ';" class="At2PopupMask"></div> '
        + '<div id="At2PopupWindow' + index.toString() + '" class="At2PopupWindowContainer" style="z-index:' + zindex_1.toString() + ';">'
        + '<div class="At2PopupWindow">  <button class="close" style="margin: 6px 10px;" onclick="At2PopupClose(' + index.toString() + ')">X</button>'
        + '<div class="At2PopupHeader">  </div> <div class="At2PopupContent">  </div> </div> </div>';
    $('body').append(txt);
}

function At2Confirm(titre, content, parameter) {
    var okText = 'OK';
    var okClass = 'primary';
    var ok2Text = '';
    var ok2Class = 'primary';
    var cancelText = 'Annuler';
    var cancelClass = 'default';
    var headerColor = '#337ab7';
    var At2ConfirmActionOnOKHandler = null;
    var At2ConfirmActionOnOK2Handler = null;
    if ((typeof parameter === 'function'))
        At2ConfirmActionOnOKHandler = parameter;
    else {
        At2ConfirmActionOnOKHandler = parameter.onok;
        if ('okText' in parameter) okText = parameter.okText;
        if ('okClass' in parameter) okClass = parameter.okClass;
        if ('ok2Text' in parameter) ok2Text = parameter.ok2Text;
        if ('ok2Class' in parameter) ok2Class = parameter.ok2Class;
        if ('onok2' in parameter) At2ConfirmActionOnOK2Handler = parameter.onok2;
        if ('cancelText' in parameter) cancelText = parameter.cancelText;
        if ('cancelClass' in parameter) cancelClass = parameter.cancelClass;
        if ('headerColor' in parameter) headerColor = parameter.headerColor;
    }

    var jFooter = $("<div id=BtnConfirmFooter class='modal-footer'/>");


    jFooter.append($('<button id=At2ConfirmBtnOK type="button" class="btn btn-' + okClass + '" >' + okText + '</button>').click(function () {
        At2PopupClose(80);
        At2ConfirmActionOnOKHandler()
    }));

    if (ok2Text)
        jFooter.append($('<button id=At2ConfirmBtnOK2 type="button" class="btn btn-' + ok2Class + '" >' + ok2Text + '</button>').click(function () {
            At2PopupClose(80);
            At2ConfirmActionOnOK2Handler()
        }));
    jFooter.append('<button id=At2ConfirmBtnCancel type="button" class="btn btn-' + cancelClass + '" onclick="At2PopupClose(80);">' + cancelText + '</button>');

    var jContent = $('<div/>').html(content).append(jFooter);
    At2PopupOpen(80, titre, jContent);
    $('#At2PopupWindow80 .At2PopupHeader').css('background-color', headerColor).css('border-color', headerColor);
}

function XSSStrEscape(str) {
    if (str)
        return str.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/'/g, "&apos;")
    else
        return '';
}