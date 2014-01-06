(function(window) {
    var AmaraIframeController = function() {
	var iframes = [];
	this.initIframes = function() {
	    console.log("Entering initIframes");
	    var elements = document.getElementsByClassName("amara-embed");
	    console.log("In initIframes: " + elements);
	    for (var i = 0 ; i < elements.length ; i++) {
		var currentDiv = elements[i];
		var url = currentDiv.getAttribute('data-url');
		var iframe = document.createElement("IFRAME");
		iframe.src = "http://" + window.location.host + "/embedder-widget/" + url;
		currentDiv.appendChild(iframe);
		iframes.push(iframe);
	    }
	};
	this.initResize = function() {
	    var controller = this;
	    iframes.forEach(function(iframe) {
		window.setInterval(function() {
		    controller.resizeIframe(iframe);
		}
				   ,100);
	    });
	};
	this.resizeIframe = function(iframe) {
	    if (iframe.contentDocument && iframe.contentDocument.body && iframe.contentDocument.body.scrollWidth) {
		iframe.width = 0;
		iframe.width = iframe.contentDocument.body.scrollWidth + 20;
		iframe.height = iframe.contentDocument.body.scrollHeight + 20;
            }
	};
    };
    window.AmaraIframeController = AmaraIframeController;

    var initIframeController = function() {
	var controller = new window.AmaraIframeController();
	controller.initIframes();
	controller.initResize();
    };
    window.initIframeController = initIframeController;

})(window);


if(window.attachEvent) {
    window.attachEvent('onload', window.initIframeController);
} else {
    if(window.onload) {
        var curronload = window.onload;
        var newonload = function() {
            curronload();
            window.initIframeController();
        };
        window.onload = newonload;
    } else {
        window.onload = window.initIframeController;
    }
}
