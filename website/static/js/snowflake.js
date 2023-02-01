function callService() {
  var json;
  uri = "https://kbazfunction.azurewebsites.net/api/getsnowflakedatasets";

  var xhr = new XMLHttpRequest();
  xhr.responseType = "json";
  xhr.onreadystatechange = function () {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      json = xhr.response;
      //console.log(xhr.responseText);
      loadData(json);
    }
  };

  xhr.open("GET", uri, true);

  xhr.send(null);
}

async function loadData(json) {
  var selector = "results";

  //call the jsonToTable Function
  jsonToTable(json, selector);

  function jsonToTable(json, selector) {
    //begin function

    //array to hold the html for the table
    var html = [];

    //add the opening table and tablebody tags
    html.push('<table class="table table-striped">\n');

    //begin adding the table headers
    html.push('<thead class="text-secondary"><tr>');

    html.push('<th scope="col">' + "#" + "</th>");
    html.push('<th scope="col">' + "Last update" + "</th>");
    html.push('<th scope="col">' + "Table Name" + "</th>");
    html.push('<th scope="col">' + "Database " + "</th>");
    html.push('<th scope="col">' + "Source System" + "</th>");

    html.push("</tr></thead><tbody>");

    console.log(json); //add the closing table and table body tags

    // Add a counter to the rows.
    var counter = 1;

    //loop through the array of objects
    json.forEach(function (item) {
      //begin forEach

      //add the opening table row tag
      html.push("<tr>");
      html.push('<td scope="row">' + counter++ + "</td>");

      //loop though each of the objects properties
      for (var key in item) {
        //begin for in loop

            if( ['database_name', 'schema_name', 'name', 'created_on'].includes(key) ) {

              if( key == 'created_on' ) {
                item[key] = new Date(item[key]).toLocaleString();
              }

              //append the table data containing the objects property value
              html.push("<td>" + item[key] + "</td>");
        }
      } //end for in loop

      //add the closing table row tag
      html.push("</tr>");
    }); //end forEach

    html.push("<table>\n</tbody>");

    //testing display of results
    document.getElementById(selector).innerHTML = html.join("");
  } //end function
}