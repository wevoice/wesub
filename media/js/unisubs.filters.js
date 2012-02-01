jQuery(document).ready(function($){
    $('#sort-filter').click(function(e) {
        e.preventDefault();

        $('.filters').toggle();
        
        $(this).children('span').toggleClass('open');
    });

    $('select', '.filters').change(function(e) {
        window.location = $(this).children('option:selected').attr('value');
    });
});
