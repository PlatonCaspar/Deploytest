//here i will define every js function used by custom elements of the website

//document slider
var slideIndex = 1;
// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  var i;
  var slides = $(".mySlide");
  var dots = $(".dot");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
      dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";
  dots[slideIndex-1].className += " active";
} 

//end document slider

// flexible inputs on PartType
function add_input(container){
        console.log("add_input was called")
        var start = 0;
        var inputs;
        inputs = $(container).find('input');
        console.log(inputs)
        var input;
        for (input = 0; input<inputs.length; input++){
            if (typeof inputs[input] === "undefined"){continue;}
            console.log(inputs[input]);
            var name = $(inputs[input]).attr("name");
            console.log(name);
            name = name.split(':')[1];
            nr = parseInt(name);
            console.log("Parse Int: "+nr)
            if (nr>start){
                start = nr;
            }
        }
        start = start+1;
        var _str = "\".input-group\""
        container.append(
                    '<div class="input-group" id="group:'+start+'">'+
                        '<input class="form-control" placeholder="Please enter a property..."'+
                        'id="input:'+start+'" name="input:'+start+'">'+
                        '<div class="input-group-btn">'+
                            '<button class="btn btn-default" type="button" oncklick="$(this).parent().find('+_str+').remove()">'+
                                '<i class="glyphicon glyphicon-remove"></i>'+
                            '</button>'+
                        '</div>'+
                    '</div>'
        )
    }

function remove_input(div){
  div.remove()
}
// end of flexible inputs on PartType