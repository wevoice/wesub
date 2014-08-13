
$('#enterprise').click(function(event){

	event.preventDefault();
	$('#form-ondemand').css('display', 'none');
	$('#form-enterprise').css('display', 'block','height','300px');
	$('#wufooFormzcj8tl80b7vofo').css('height', '300px');
	$('.button-choose a:focus').css('outline', 'none');
	$('#ondemand').removeClass('active');
	$('#enterprise').addClass('active');
	
});

$('#ondemand').click(function(event){

	event.preventDefault();
	$('#form-enterprise').css('display', 'none');
	$('#form-ondemand').css('display', 'block','height','800px');
	$('#wufooFormm1xz667s1nhjzve').css('height', '800px');
	$('.button-choose a:focus').css('outline', 'none');
	$('#enterprise').removeClass('active');
	$('#ondemand').addClass('active');
});

$(document).ready(function() {
	function displayAnchor() {
		var url = document.location.toString();
	
		 // If URL contains 'enterprise', trigger the correct box
		if (url.match('enterprise')) {
			$('#enterprise').trigger('click');
		}
		else {
			$('#form-ondemand').css('display', 'block', 'height', '800px');
			$('#form-enterprise').css('display', 'none');
		}
	} 

	displayAnchor();

});

