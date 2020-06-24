function getStageData(event, analysis_id, attack_name, stage_index, stage_name) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // console.log(this.responseText);
            document.getElementById("stage-details").innerHTML = this.responseText;
        }
    };
    var url = "get_stage_data/" + analysis_id + "/" + attack_name + "/" + stage_index + "/" + stage_name;
    // console.log("Using url: " + url);
    xhttp.open("GET", url, true);
    xhttp.send();

    clearStagesBackground();
    setBackground(event);

}

function setBackground(event) {
    var element;
    if ( event.target.tagName == 'SPAN' ) {
        element = event.target.parentElement;
    } else {
        element = event.target;
    }
    console.log("Element", element);
    element.style.background = '#ddd';
}

function clearStagesBackground() {
  var stages = document.querySelectorAll('td.stage');
  for (i = 0; i < stages.length; i++ ) {
    stages[i].style.background = '';
  }
}
}
