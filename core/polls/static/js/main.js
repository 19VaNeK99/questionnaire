let count_choice = 1;
function add_fields() {
   var d = document.getElementById("content");

   d.innerHTML += "<br/><div class='col-lg-4'><div class='form-group'><label for='option1'>Option 1</label>" + "{% render_field form_choice.title class='form-control' %}" + "</div></div>"
}