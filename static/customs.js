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
        var start = 0;
        var inputs;
        inputs = $(container).find('input');
        var input;
        for (input = 0; input<inputs.length; input++){
            if (typeof inputs[input] === "undefined"){continue;}

            var name = $(inputs[input]).attr("name");
 
            name = name.split(':')[1];
            nr = parseInt(name);
    
            if (nr>start){
                start = nr;
            }
        }
        start = start+1;
        var _str = "\".input-group\""
        container.append(
                    '<div class="form-group" id="group:'+start+'">'+
                        '<input class="form-control" placeholder="Please enter a property..."'+
                        'id="input:'+start+'" name="input:'+start+'">'+
                    '</div>'
        )
    }


function remove_input(div){
  console.log("remove_input was called");
  $(div).remove();
}
// end of flexible inputs on PartType