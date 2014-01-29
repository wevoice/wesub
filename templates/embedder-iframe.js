// This must be done when the js file is first loaded
var scriptFiles = document.getElementsByTagName("script");
var THIS_JS_FILE = scriptFiles[scriptFiles.length-1].src;

(function(window) {
    var AmaraIframeController = function() {
	var iframes = [];
	var timers = [];
	var iframeDomain = '';
	var resize = function(index, width, height) {
	    iframes[index].width = 0;
	    iframes[index].width = width;
	    iframes[index].height = height;
	};
	this.resizeReceiver = function(e) {
	    if (e.data.initDone)
		window.clearInterval(timers[e.data.index]);
	    if (e.data.resize)
		resize(e.data.index, e.data.width, e.data.height);
	};
	this.initIframes = function() {
	    var elements = document.getElementsByClassName("amara-embed");
	    var parser = document.createElement('a');
	    window.addEventListener('message', this.resizeReceiver, false);
	    parser.href = THIS_JS_FILE;
	    iframeDomain = "http://" + parser.host;
	    for (var i = 0 ; i < elements.length ; i++) {
		var currentDiv = elements[i];
		var iframe = document.createElement("IFRAME");
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
	    var newIndex = 0;
	    iframes.forEach(function(iframe, index) {
		timers.push(window.setInterval(function() {
		    controller.postToIframe(iframe, index);
		}
					       ,100));
	    });
	};

	this.postToIframe = function(iframe, index) {
	    if (iframe.contentWindow) {
		iframe.contentWindow.postMessage({fromIframeController: true, index: index}, iframeDomain);
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
