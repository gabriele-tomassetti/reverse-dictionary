function getWords(definition) {
    return definition;
}

function sendData() {
    $.post( "/", {definition: getWords($("#definition").val())}, function( data ) {        
        var words = "<ul>";
        data.forEach(element => {
            words += "<li>"+element+"</li>"
        });
        words += "</ul>"
        $( "#words" ).html( words );
      });
  }

$("#find").click(sendData);
$("#definition").keyup(function(event) {
    if (event.keyCode === 13) {
        $("#find").click();
    }
});  