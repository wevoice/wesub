$(function() {
    $.ajax({
        type: 'get',
        url: '/site_media/src/js/dfxp/sample.dfxp.xml',
        dataType: 'xml',
        success: function(resp) {
            window.$xml = $(resp);
        }
    });
});
