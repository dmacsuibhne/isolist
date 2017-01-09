function save_tag(tag_id) {
  var element = document.getElementById(tag_id);
  var parent = element.parentElement

  // Change cell colour
  colour_cell(element)

  // Make JIRA links clickable
  editable_jira_links(false)

  // Send updated value to server
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST","/save_tag", true);
  xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
  xhttp.send("file_name=" + parent.className + "&tag=" + element.className + "&value=" + element.innerText);

}

function colour_all() {
  var cell_list = document.getElementsByTagName("td");
  for (i = 0; i < cell_list.length; i++) {
    colour_cell(cell_list[i])
  }
}

function colour_cell(element) {
  
  if(element.innerText.includes("NOK") || element.innerText.includes("NO")) {
    element.style.background = "#FFD9D9";
  } else if (element.innerText.includes("OK") || element.innerText.includes("YES")) {
    element.style.background = "#D9FFD9";
  }
}

function editable_jira_links(bool) {
  var jira_link_list = document.getElementsByClassName("jira_link")
  for (i = 0; i < jira_link_list.length; i++) {
    jira_link_list[i].setAttribute("contentEditable", bool);
  }
}