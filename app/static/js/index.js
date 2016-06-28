function displayAlertMessage(msg)
{ 
    $("#alertMessage").show();
    $("#alertMessage").jqxWindow(
        { width: 300, height: 140,theme:"darkblue",
              position: { x:600, y: 200 },cancelButton:"#alertMessageCancelButton",isModal:true});
    $("#alertMessageContent").children().first().text("");
    $("#alertMessageContent").children().first().text(msg);
    $("#alertMessage").jqxWindow('open');

    $("#alertMessage").unbind('close');
    $("#alertMessageOkButton").unbind('click');
    $("#alertMessage").on('close',function(event)
    {
        $("#alertMessage").hide();
    });
} 

