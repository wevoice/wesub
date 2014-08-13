
$('#enterprise').click(function(event){

	event.preventDefault();
	$('#form-ondemand').css('display', 'none');
	$('#form-enterprise').css('display', 'block','height','250px');
	$('#wufooFormzcj8tl80b7vofo').css('height', '250px');
	$('.button-choose a:focus').css('outline', 'none');
	$('#ondemand').removeClass('active');
	$('#enterprise').addClass('active');
	
});

$('#ondemand').click(function(event){

	event.preventDefault();
	$('#form-enterprise').css('display', 'none');
	$('#form-ondemand').css('display', 'block','height','700px');
	$('#wufooFormm1xz667s1nhjzve').css('height', '700px');
	$('.button-choose a:focus').css('outline', 'none');
	$('#enterprise').removeClass('active');
	$('#ondemand').addClass('active');
});

$(document).ready(function() {
	function displayAnchor() {
		var url = document.location.toString();
		
		 // If URL contains #enterprise, trigger the correct box
		var location = window.location.href;
		var pattern = /enterprise/g;
		if pattern.test(location); {
			$('#form-enterprise').css('display', 'block', 'height', '250px');
			$('#form-ondemand').css('display', 'none');
		}
		else {
			$('#form-ondemand').css('display', 'block', 'height', '700px');
			$('#form-enterprise').css('display', 'none');
		}
	}


});

