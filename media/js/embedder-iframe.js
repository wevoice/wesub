(function(window) {
    var AmaraIframeController = function() {
	var iframes = [];
	var toto = 0;
	this.initIframes = function() {
	    var elements = document.getElementsByClassName("amara-embed");
	    for (var i = 0 ; i < elements.length ; i++) {
		var currentDiv = elements[i];
		var iframe = document.createElement("IFRAME");
		var parser = document.createElement('a');
		var scripts = document.getElementsByTagName("script");
		parser.href = scripts[scripts.length-1].src;
		iframe.src = "http://" + parser.host + "/embedder-widget-iframe/?data=" +
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
	    if (iframe.contentDocument && iframe.contentDocument.body && 
		iframe.contentWindow && iframe.contentWindow.document.documentElement) {
		var sh = Math.min(iframe.contentWindow.document.documentElement.scrollHeight,
				  iframe.contentDocument.body.scrollHeight);
		var sw = Math.min(iframe.contentWindow.document.documentElement.scrollWidth,
				  iframe.contentDocument.body.scrollWidth);
		if( (iframe.width != sw) || (iframe.height != sh)) {
		    iframe.width = 0;
		    iframe.width = sw;
		    iframe.height = sh;
		}
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
