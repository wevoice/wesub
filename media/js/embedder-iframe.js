(function(window) {
    var AmaraIframeController = function() {
	var iframes = [];
	var toto = 0;
	this.initIframes = function() {
	    var elements = document.getElementsByClassName("amara-embed");
	    for (var i = 0 ; i < elements.length ; i++) {
		var currentDiv = elements[i];
		var iframe = document.createElement("IFRAME");
		iframe.src = "http://" + window.location.host + "/embedder-widget-iframe/?data=" +
		    encodeURIComponent(JSON.stringify(currentDiv.dataset));
		iframe.style.border = "none";
		iframe.style.overflow = "hidden";
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
	    if (iframe.contentWindow && iframe.contentWindow.document && iframe.contentWindow.document.documentElement && (
		iframe.width != iframe.contentWindow.document.documentElement.scrollWidth ||
		    iframe.height != iframe.contentWindow.document.documentElement.scrollHeight)) {
		iframe.width = 0;
		iframe.width = iframe.contentWindow.document.documentElement.scrollWidth;
		iframe.contentWindow.document.documentElement.childNodes[iframe.contentWindow.document.documentElement.childNodes.length - 1].height = 1;
		iframe.height = iframe.contentWindow.document.documentElement.scrollHeight;
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
