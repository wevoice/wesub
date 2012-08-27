var JSON;if(!JSON){JSON={};}(function(){'use strict';function f(n){return n<10?'0'+n:n;}if(typeof Date.prototype.toJSON!=='function'){Date.prototype.toJSON=function(key){return isFinite(this.valueOf())?this.getUTCFullYear()+'-'+f(this.getUTCMonth()+1)+'-'+f(this.getUTCDate())+'T'+f(this.getUTCHours())+':'+f(this.getUTCMinutes())+':'+f(this.getUTCSeconds())+'Z':null;};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(key){return this.valueOf();};}var cx=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,escapable=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,gap,indent,meta={'\b':'\\b','\t':'\\t','\n':'\\n','\f':'\\f','\r':'\\r','"':'\\"','\\':'\\\\'},rep;function quote(string){escapable.lastIndex=0;return escapable.test(string)?'"'+string.replace(escapable,function(a){var c=meta[a];return typeof c==='string'?c:'\\u'+('0000'+a.charCodeAt(0).toString(16)).slice(-4);})+'"':'"'+string+'"';}function str(key,holder){var i,k,v,length,mind=gap,partial,value=holder[key];if(value&&typeof value==='object'&&typeof value.toJSON==='function'){value=value.toJSON(key);}if(typeof rep==='function'){value=rep.call(holder,key,value);}switch(typeof value){case'string':return quote(value);case'number':return isFinite(value)?String(value):'null';case'boolean':case'null':return String(value);case'object':if(!value){return'null';}gap+=indent;partial=[];if(Object.prototype.toString.apply(value)==='[object Array]'){length=value.length;for(i=0;i<length;i+=1){partial[i]=str(i,value)||'null';}v=partial.length===0?'[]':gap?'[\n'+gap+partial.join(',\n'+gap)+'\n'+mind+']':'['+partial.join(',')+']';gap=mind;return v;}if(rep&&typeof rep==='object'){length=rep.length;for(i=0;i<length;i+=1){if(typeof rep[i]==='string'){k=rep[i];v=str(k,value);if(v){partial.push(quote(k)+(gap?': ':':')+v);}}}}else{for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=str(k,value);if(v){partial.push(quote(k)+(gap?': ':':')+v);}}}}v=partial.length===0?'{}':gap?'{\n'+gap+partial.join(',\n'+gap)+'\n'+mind+'}':'{'+partial.join(',')+'}';gap=mind;return v;}}if(typeof JSON.stringify!=='function'){JSON.stringify=function(value,replacer,space){var i;gap='';indent='';if(typeof space==='number'){for(i=0;i<space;i+=1){indent+=' ';}}else if(typeof space==='string'){indent=space;}rep=replacer;if(replacer&&typeof replacer!=='function'&&(typeof replacer!=='object'||typeof replacer.length!=='number')){throw new Error('JSON.stringify');}return str('',{'':value});};}if(typeof JSON.parse!=='function'){JSON.parse=function(text,reviver){var j;function walk(holder,key){var k,v,value=holder[key];if(value&&typeof value==='object'){for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=walk(value,k);if(v!==undefined){value[k]=v;}else{delete value[k];}}}}return reviver.call(holder,key,value);}text=String(text);cx.lastIndex=0;if(cx.test(text)){text=text.replace(cx,function(a){return'\\u'+('0000'+a.charCodeAt(0).toString(16)).slice(-4);});}if(/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,'@').replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,']').replace(/(?:^|:|,)(?:\s*\[)+/g,''))){j=eval('('+text+')');return typeof reviver==='function'?walk({'':j},''):j;}throw new SyntaxError('JSON.parse');};}}());
// Underscore.js 1.3.3
// (c) 2009-2012 Jeremy Ashkenas, DocumentCloud Inc.
// Underscore is freely distributable under the MIT license.
// Portions of Underscore are inspired or borrowed from Prototype,
// Oliver Steele's Functional, and John Resig's Micro-Templating.
// For all details and documentation:
// http://documentcloud.github.com/underscore
(function(){function r(a,c,d){if(a===c)return 0!==a||1/a==1/c;if(null==a||null==c)return a===c;a._chain&&(a=a._wrapped);c._chain&&(c=c._wrapped);if(a.isEqual&&b.isFunction(a.isEqual))return a.isEqual(c);if(c.isEqual&&b.isFunction(c.isEqual))return c.isEqual(a);var e=l.call(a);if(e!=l.call(c))return!1;switch(e){case "[object String]":return a==""+c;case "[object Number]":return a!=+a?c!=+c:0==a?1/a==1/c:a==+c;case "[object Date]":case "[object Boolean]":return+a==+c;case "[object RegExp]":return a.source==
c.source&&a.global==c.global&&a.multiline==c.multiline&&a.ignoreCase==c.ignoreCase}if("object"!=typeof a||"object"!=typeof c)return!1;for(var f=d.length;f--;)if(d[f]==a)return!0;d.push(a);var f=0,g=!0;if("[object Array]"==e){if(f=a.length,g=f==c.length)for(;f--&&(g=f in a==f in c&&r(a[f],c[f],d)););}else{if("constructor"in a!="constructor"in c||a.constructor!=c.constructor)return!1;for(var h in a)if(b.has(a,h)&&(f++,!(g=b.has(c,h)&&r(a[h],c[h],d))))break;if(g){for(h in c)if(b.has(c,h)&&!f--)break;
g=!f}}d.pop();return g}var s=this,I=s._,o={},k=Array.prototype,p=Object.prototype,i=k.slice,J=k.unshift,l=p.toString,K=p.hasOwnProperty,y=k.forEach,z=k.map,A=k.reduce,B=k.reduceRight,C=k.filter,D=k.every,E=k.some,q=k.indexOf,F=k.lastIndexOf,p=Array.isArray,L=Object.keys,t=Function.prototype.bind,b=function(a){return new m(a)};"undefined"!==typeof exports?("undefined"!==typeof module&&module.exports&&(exports=module.exports=b),exports._=b):s._=b;b.VERSION="1.3.3";var j=b.each=b.forEach=function(a,
c,d){if(a!=null)if(y&&a.forEach===y)a.forEach(c,d);else if(a.length===+a.length)for(var e=0,f=a.length;e<f;e++){if(e in a&&c.call(d,a[e],e,a)===o)break}else for(e in a)if(b.has(a,e)&&c.call(d,a[e],e,a)===o)break};b.map=b.collect=function(a,c,b){var e=[];if(a==null)return e;if(z&&a.map===z)return a.map(c,b);j(a,function(a,g,h){e[e.length]=c.call(b,a,g,h)});if(a.length===+a.length)e.length=a.length;return e};b.reduce=b.foldl=b.inject=function(a,c,d,e){var f=arguments.length>2;a==null&&(a=[]);if(A&&
a.reduce===A){e&&(c=b.bind(c,e));return f?a.reduce(c,d):a.reduce(c)}j(a,function(a,b,i){if(f)d=c.call(e,d,a,b,i);else{d=a;f=true}});if(!f)throw new TypeError("Reduce of empty array with no initial value");return d};b.reduceRight=b.foldr=function(a,c,d,e){var f=arguments.length>2;a==null&&(a=[]);if(B&&a.reduceRight===B){e&&(c=b.bind(c,e));return f?a.reduceRight(c,d):a.reduceRight(c)}var g=b.toArray(a).reverse();e&&!f&&(c=b.bind(c,e));return f?b.reduce(g,c,d,e):b.reduce(g,c)};b.find=b.detect=function(a,
c,b){var e;G(a,function(a,g,h){if(c.call(b,a,g,h)){e=a;return true}});return e};b.filter=b.select=function(a,c,b){var e=[];if(a==null)return e;if(C&&a.filter===C)return a.filter(c,b);j(a,function(a,g,h){c.call(b,a,g,h)&&(e[e.length]=a)});return e};b.reject=function(a,c,b){var e=[];if(a==null)return e;j(a,function(a,g,h){c.call(b,a,g,h)||(e[e.length]=a)});return e};b.every=b.all=function(a,c,b){var e=true;if(a==null)return e;if(D&&a.every===D)return a.every(c,b);j(a,function(a,g,h){if(!(e=e&&c.call(b,
a,g,h)))return o});return!!e};var G=b.some=b.any=function(a,c,d){c||(c=b.identity);var e=false;if(a==null)return e;if(E&&a.some===E)return a.some(c,d);j(a,function(a,b,h){if(e||(e=c.call(d,a,b,h)))return o});return!!e};b.include=b.contains=function(a,c){var b=false;if(a==null)return b;if(q&&a.indexOf===q)return a.indexOf(c)!=-1;return b=G(a,function(a){return a===c})};b.invoke=function(a,c){var d=i.call(arguments,2);return b.map(a,function(a){return(b.isFunction(c)?c||a:a[c]).apply(a,d)})};b.pluck=
function(a,c){return b.map(a,function(a){return a[c]})};b.max=function(a,c,d){if(!c&&b.isArray(a)&&a[0]===+a[0])return Math.max.apply(Math,a);if(!c&&b.isEmpty(a))return-Infinity;var e={computed:-Infinity};j(a,function(a,b,h){b=c?c.call(d,a,b,h):a;b>=e.computed&&(e={value:a,computed:b})});return e.value};b.min=function(a,c,d){if(!c&&b.isArray(a)&&a[0]===+a[0])return Math.min.apply(Math,a);if(!c&&b.isEmpty(a))return Infinity;var e={computed:Infinity};j(a,function(a,b,h){b=c?c.call(d,a,b,h):a;b<e.computed&&
(e={value:a,computed:b})});return e.value};b.shuffle=function(a){var b=[],d;j(a,function(a,f){d=Math.floor(Math.random()*(f+1));b[f]=b[d];b[d]=a});return b};b.sortBy=function(a,c,d){var e=b.isFunction(c)?c:function(a){return a[c]};return b.pluck(b.map(a,function(a,b,c){return{value:a,criteria:e.call(d,a,b,c)}}).sort(function(a,b){var c=a.criteria,d=b.criteria;return c===void 0?1:d===void 0?-1:c<d?-1:c>d?1:0}),"value")};b.groupBy=function(a,c){var d={},e=b.isFunction(c)?c:function(a){return a[c]};
j(a,function(a,b){var c=e(a,b);(d[c]||(d[c]=[])).push(a)});return d};b.sortedIndex=function(a,c,d){d||(d=b.identity);for(var e=0,f=a.length;e<f;){var g=e+f>>1;d(a[g])<d(c)?e=g+1:f=g}return e};b.toArray=function(a){return!a?[]:b.isArray(a)||b.isArguments(a)?i.call(a):a.toArray&&b.isFunction(a.toArray)?a.toArray():b.values(a)};b.size=function(a){return b.isArray(a)?a.length:b.keys(a).length};b.first=b.head=b.take=function(a,b,d){return b!=null&&!d?i.call(a,0,b):a[0]};b.initial=function(a,b,d){return i.call(a,
0,a.length-(b==null||d?1:b))};b.last=function(a,b,d){return b!=null&&!d?i.call(a,Math.max(a.length-b,0)):a[a.length-1]};b.rest=b.tail=function(a,b,d){return i.call(a,b==null||d?1:b)};b.compact=function(a){return b.filter(a,function(a){return!!a})};b.flatten=function(a,c){return b.reduce(a,function(a,e){if(b.isArray(e))return a.concat(c?e:b.flatten(e));a[a.length]=e;return a},[])};b.without=function(a){return b.difference(a,i.call(arguments,1))};b.uniq=b.unique=function(a,c,d){var d=d?b.map(a,d):a,
e=[];a.length<3&&(c=true);b.reduce(d,function(d,g,h){if(c?b.last(d)!==g||!d.length:!b.include(d,g)){d.push(g);e.push(a[h])}return d},[]);return e};b.union=function(){return b.uniq(b.flatten(arguments,true))};b.intersection=b.intersect=function(a){var c=i.call(arguments,1);return b.filter(b.uniq(a),function(a){return b.every(c,function(c){return b.indexOf(c,a)>=0})})};b.difference=function(a){var c=b.flatten(i.call(arguments,1),true);return b.filter(a,function(a){return!b.include(c,a)})};b.zip=function(){for(var a=
i.call(arguments),c=b.max(b.pluck(a,"length")),d=Array(c),e=0;e<c;e++)d[e]=b.pluck(a,""+e);return d};b.indexOf=function(a,c,d){if(a==null)return-1;var e;if(d){d=b.sortedIndex(a,c);return a[d]===c?d:-1}if(q&&a.indexOf===q)return a.indexOf(c);d=0;for(e=a.length;d<e;d++)if(d in a&&a[d]===c)return d;return-1};b.lastIndexOf=function(a,b){if(a==null)return-1;if(F&&a.lastIndexOf===F)return a.lastIndexOf(b);for(var d=a.length;d--;)if(d in a&&a[d]===b)return d;return-1};b.range=function(a,b,d){if(arguments.length<=
1){b=a||0;a=0}for(var d=arguments[2]||1,e=Math.max(Math.ceil((b-a)/d),0),f=0,g=Array(e);f<e;){g[f++]=a;a=a+d}return g};var H=function(){};b.bind=function(a,c){var d,e;if(a.bind===t&&t)return t.apply(a,i.call(arguments,1));if(!b.isFunction(a))throw new TypeError;e=i.call(arguments,2);return d=function(){if(!(this instanceof d))return a.apply(c,e.concat(i.call(arguments)));H.prototype=a.prototype;var b=new H,g=a.apply(b,e.concat(i.call(arguments)));return Object(g)===g?g:b}};b.bindAll=function(a){var c=
i.call(arguments,1);c.length==0&&(c=b.functions(a));j(c,function(c){a[c]=b.bind(a[c],a)});return a};b.memoize=function(a,c){var d={};c||(c=b.identity);return function(){var e=c.apply(this,arguments);return b.has(d,e)?d[e]:d[e]=a.apply(this,arguments)}};b.delay=function(a,b){var d=i.call(arguments,2);return setTimeout(function(){return a.apply(null,d)},b)};b.defer=function(a){return b.delay.apply(b,[a,1].concat(i.call(arguments,1)))};b.throttle=function(a,c){var d,e,f,g,h,i,j=b.debounce(function(){h=
g=false},c);return function(){d=this;e=arguments;f||(f=setTimeout(function(){f=null;h&&a.apply(d,e);j()},c));g?h=true:i=a.apply(d,e);j();g=true;return i}};b.debounce=function(a,b,d){var e;return function(){var f=this,g=arguments;d&&!e&&a.apply(f,g);clearTimeout(e);e=setTimeout(function(){e=null;d||a.apply(f,g)},b)}};b.once=function(a){var b=false,d;return function(){if(b)return d;b=true;return d=a.apply(this,arguments)}};b.wrap=function(a,b){return function(){var d=[a].concat(i.call(arguments,0));
return b.apply(this,d)}};b.compose=function(){var a=arguments;return function(){for(var b=arguments,d=a.length-1;d>=0;d--)b=[a[d].apply(this,b)];return b[0]}};b.after=function(a,b){return a<=0?b():function(){if(--a<1)return b.apply(this,arguments)}};b.keys=L||function(a){if(a!==Object(a))throw new TypeError("Invalid object");var c=[],d;for(d in a)b.has(a,d)&&(c[c.length]=d);return c};b.values=function(a){return b.map(a,b.identity)};b.functions=b.methods=function(a){var c=[],d;for(d in a)b.isFunction(a[d])&&
c.push(d);return c.sort()};b.extend=function(a){j(i.call(arguments,1),function(b){for(var d in b)a[d]=b[d]});return a};b.pick=function(a){var c={};j(b.flatten(i.call(arguments,1)),function(b){b in a&&(c[b]=a[b])});return c};b.defaults=function(a){j(i.call(arguments,1),function(b){for(var d in b)a[d]==null&&(a[d]=b[d])});return a};b.clone=function(a){return!b.isObject(a)?a:b.isArray(a)?a.slice():b.extend({},a)};b.tap=function(a,b){b(a);return a};b.isEqual=function(a,b){return r(a,b,[])};b.isEmpty=
function(a){if(a==null)return true;if(b.isArray(a)||b.isString(a))return a.length===0;for(var c in a)if(b.has(a,c))return false;return true};b.isElement=function(a){return!!(a&&a.nodeType==1)};b.isArray=p||function(a){return l.call(a)=="[object Array]"};b.isObject=function(a){return a===Object(a)};b.isArguments=function(a){return l.call(a)=="[object Arguments]"};b.isArguments(arguments)||(b.isArguments=function(a){return!(!a||!b.has(a,"callee"))});b.isFunction=function(a){return l.call(a)=="[object Function]"};
b.isString=function(a){return l.call(a)=="[object String]"};b.isNumber=function(a){return l.call(a)=="[object Number]"};b.isFinite=function(a){return b.isNumber(a)&&isFinite(a)};b.isNaN=function(a){return a!==a};b.isBoolean=function(a){return a===true||a===false||l.call(a)=="[object Boolean]"};b.isDate=function(a){return l.call(a)=="[object Date]"};b.isRegExp=function(a){return l.call(a)=="[object RegExp]"};b.isNull=function(a){return a===null};b.isUndefined=function(a){return a===void 0};b.has=function(a,
b){return K.call(a,b)};b.noConflict=function(){s._=I;return this};b.identity=function(a){return a};b.times=function(a,b,d){for(var e=0;e<a;e++)b.call(d,e)};b.escape=function(a){return(""+a).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#x27;").replace(/\//g,"&#x2F;")};b.result=function(a,c){if(a==null)return null;var d=a[c];return b.isFunction(d)?d.call(a):d};b.mixin=function(a){j(b.functions(a),function(c){M(c,b[c]=a[c])})};var N=0;b.uniqueId=
function(a){var b=N++;return a?a+b:b};b.templateSettings={evaluate:/<%([\s\S]+?)%>/g,interpolate:/<%=([\s\S]+?)%>/g,escape:/<%-([\s\S]+?)%>/g};var u=/.^/,n={"\\":"\\","'":"'",r:"\r",n:"\n",t:"\t",u2028:"\u2028",u2029:"\u2029"},v;for(v in n)n[n[v]]=v;var O=/\\|'|\r|\n|\t|\u2028|\u2029/g,P=/\\(\\|'|r|n|t|u2028|u2029)/g,w=function(a){return a.replace(P,function(a,b){return n[b]})};b.template=function(a,c,d){d=b.defaults(d||{},b.templateSettings);a="__p+='"+a.replace(O,function(a){return"\\"+n[a]}).replace(d.escape||
u,function(a,b){return"'+\n_.escape("+w(b)+")+\n'"}).replace(d.interpolate||u,function(a,b){return"'+\n("+w(b)+")+\n'"}).replace(d.evaluate||u,function(a,b){return"';\n"+w(b)+"\n;__p+='"})+"';\n";d.variable||(a="with(obj||{}){\n"+a+"}\n");var a="var __p='';var print=function(){__p+=Array.prototype.join.call(arguments, '')};\n"+a+"return __p;\n",e=new Function(d.variable||"obj","_",a);if(c)return e(c,b);c=function(a){return e.call(this,a,b)};c.source="function("+(d.variable||"obj")+"){\n"+a+"}";return c};
b.chain=function(a){return b(a).chain()};var m=function(a){this._wrapped=a};b.prototype=m.prototype;var x=function(a,c){return c?b(a).chain():a},M=function(a,c){m.prototype[a]=function(){var a=i.call(arguments);J.call(a,this._wrapped);return x(c.apply(b,a),this._chain)}};b.mixin(b);j("pop,push,reverse,shift,sort,splice,unshift".split(","),function(a){var b=k[a];m.prototype[a]=function(){var d=this._wrapped;b.apply(d,arguments);var e=d.length;(a=="shift"||a=="splice")&&e===0&&delete d[0];return x(d,
this._chain)}});j(["concat","join","slice"],function(a){var b=k[a];m.prototype[a]=function(){return x(b.apply(this._wrapped,arguments),this._chain)}});m.prototype.chain=function(){this._chain=true;return this};m.prototype.value=function(){return this._wrapped}}).call(this);
/* Zepto v1.0rc1 - polyfill zepto event detect fx ajax form touch - zeptojs.com/license */
(function(a){String.prototype.trim===a&&(String.prototype.trim=function(){return this.replace(/^\s+/,"").replace(/\s+$/,"")}),Array.prototype.reduce===a&&(Array.prototype.reduce=function(b){if(this===void 0||this===null)throw new TypeError;var c=Object(this),d=c.length>>>0,e=0,f;if(typeof b!="function")throw new TypeError;if(d==0&&arguments.length==1)throw new TypeError;if(arguments.length>=2)f=arguments[1];else do{if(e in c){f=c[e++];break}if(++e>=d)throw new TypeError}while(!0);while(e<d)e in c&&(f=b.call(a,f,c[e],e,c)),e++;return f})})();var Zepto=function(){function A(a){return v.call(a)=="[object Function]"}function B(a){return a instanceof Object}function C(b){var c,d;if(v.call(b)!=="[object Object]")return!1;d=A(b.constructor)&&b.constructor.prototype;if(!d||!hasOwnProperty.call(d,"isPrototypeOf"))return!1;for(c in b);return c===a||hasOwnProperty.call(b,c)}function D(a){return a instanceof Array}function E(a){return typeof a.length=="number"}function F(b){return b.filter(function(b){return b!==a&&b!==null})}function G(a){return a.length>0?[].concat.apply([],a):a}function H(a){return a.replace(/::/g,"/").replace(/([A-Z]+)([A-Z][a-z])/g,"$1_$2").replace(/([a-z\d])([A-Z])/g,"$1_$2").replace(/_/g,"-").toLowerCase()}function I(a){return a in i?i[a]:i[a]=new RegExp("(^|\\s)"+a+"(\\s|$)")}function J(a,b){return typeof b=="number"&&!k[H(a)]?b+"px":b}function K(a){var b,c;return h[a]||(b=g.createElement(a),g.body.appendChild(b),c=j(b,"").getPropertyValue("display"),b.parentNode.removeChild(b),c=="none"&&(c="block"),h[a]=c),h[a]}function L(b,d){return d===a?c(b):c(b).filter(d)}function M(a,b,c,d){return A(b)?b.call(a,c,d):b}function N(a,b,d){var e=a%2?b:b.parentNode;e?e.insertBefore(d,a?a==1?e.firstChild:a==2?b:null:b.nextSibling):c(d).remove()}function O(a,b){b(a);for(var c in a.childNodes)O(a.childNodes[c],b)}var a,b,c,d,e=[],f=e.slice,g=window.document,h={},i={},j=g.defaultView.getComputedStyle,k={"column-count":1,columns:1,"font-weight":1,"line-height":1,opacity:1,"z-index":1,zoom:1},l=/^\s*<(\w+|!)[^>]*>/,m=[1,3,8,9,11],n=["after","prepend","before","append"],o=g.createElement("table"),p=g.createElement("tr"),q={tr:g.createElement("tbody"),tbody:o,thead:o,tfoot:o,td:p,th:p,"*":g.createElement("div")},r=/complete|loaded|interactive/,s=/^\.([\w-]+)$/,t=/^#([\w-]+)$/,u=/^[\w-]+$/,v={}.toString,w={},x,y,z=g.createElement("div");return w.matches=function(a,b){if(!a||a.nodeType!==1)return!1;var c=a.webkitMatchesSelector||a.mozMatchesSelector||a.oMatchesSelector||a.matchesSelector;if(c)return c.call(a,b);var d,e=a.parentNode,f=!e;return f&&(e=z).appendChild(a),d=~w.qsa(e,b).indexOf(a),f&&z.removeChild(a),d},x=function(a){return a.replace(/-+(.)?/g,function(a,b){return b?b.toUpperCase():""})},y=function(a){return a.filter(function(b,c){return a.indexOf(b)==c})},w.fragment=function(b,d){d===a&&(d=l.test(b)&&RegExp.$1),d in q||(d="*");var e=q[d];return e.innerHTML=""+b,c.each(f.call(e.childNodes),function(){e.removeChild(this)})},w.Z=function(a,b){return a=a||[],a.__proto__=arguments.callee.prototype,a.selector=b||"",a},w.isZ=function(a){return a instanceof w.Z},w.init=function(b,d){if(!b)return w.Z();if(A(b))return c(g).ready(b);if(w.isZ(b))return b;var e;if(D(b))e=F(b);else if(C(b))e=[c.extend({},b)],b=null;else if(m.indexOf(b.nodeType)>=0||b===window)e=[b],b=null;else if(l.test(b))e=w.fragment(b.trim(),RegExp.$1),b=null;else{if(d!==a)return c(d).find(b);e=w.qsa(g,b)}return w.Z(e,b)},c=function(a,b){return w.init(a,b)},c.extend=function(c){return f.call(arguments,1).forEach(function(d){for(b in d)d[b]!==a&&(c[b]=d[b])}),c},w.qsa=function(a,b){var c;return a===g&&t.test(b)?(c=a.getElementById(RegExp.$1))?[c]:e:a.nodeType!==1&&a.nodeType!==9?e:f.call(s.test(b)?a.getElementsByClassName(RegExp.$1):u.test(b)?a.getElementsByTagName(b):a.querySelectorAll(b))},c.isFunction=A,c.isObject=B,c.isArray=D,c.isPlainObject=C,c.inArray=function(a,b,c){return e.indexOf.call(b,a,c)},c.trim=function(a){return a.trim()},c.uuid=0,c.map=function(a,b){var c,d=[],e,f;if(E(a))for(e=0;e<a.length;e++)c=b(a[e],e),c!=null&&d.push(c);else for(f in a)c=b(a[f],f),c!=null&&d.push(c);return G(d)},c.each=function(a,b){var c,d;if(E(a)){for(c=0;c<a.length;c++)if(b.call(a[c],c,a[c])===!1)return a}else for(d in a)if(b.call(a[d],d,a[d])===!1)return a;return a},c.fn={forEach:e.forEach,reduce:e.reduce,push:e.push,indexOf:e.indexOf,concat:e.concat,map:function(a){return c.map(this,function(b,c){return a.call(b,c,b)})},slice:function(){return c(f.apply(this,arguments))},ready:function(a){return r.test(g.readyState)?a(c):g.addEventListener("DOMContentLoaded",function(){a(c)},!1),this},get:function(b){return b===a?f.call(this):this[b]},toArray:function(){return this.get()},size:function(){return this.length},remove:function(){return this.each(function(){this.parentNode!=null&&this.parentNode.removeChild(this)})},each:function(a){return this.forEach(function(b,c){a.call(b,c,b)}),this},filter:function(a){return c([].filter.call(this,function(b){return w.matches(b,a)}))},add:function(a,b){return c(y(this.concat(c(a,b))))},is:function(a){return this.length>0&&w.matches(this[0],a)},not:function(b){var d=[];if(A(b)&&b.call!==a)this.each(function(a){b.call(this,a)||d.push(this)});else{var e=typeof b=="string"?this.filter(b):E(b)&&A(b.item)?f.call(b):c(b);this.forEach(function(a){e.indexOf(a)<0&&d.push(a)})}return c(d)},eq:function(a){return a===-1?this.slice(a):this.slice(a,+a+1)},first:function(){var a=this[0];return a&&!B(a)?a:c(a)},last:function(){var a=this[this.length-1];return a&&!B(a)?a:c(a)},find:function(a){var b;return this.length==1?b=w.qsa(this[0],a):b=this.map(function(){return w.qsa(this,a)}),c(b)},closest:function(a,b){var d=this[0];while(d&&!w.matches(d,a))d=d!==b&&d!==g&&d.parentNode;return c(d)},parents:function(a){var b=[],d=this;while(d.length>0)d=c.map(d,function(a){if((a=a.parentNode)&&a!==g&&b.indexOf(a)<0)return b.push(a),a});return L(b,a)},parent:function(a){return L(y(this.pluck("parentNode")),a)},children:function(a){return L(this.map(function(){return f.call(this.children)}),a)},siblings:function(a){return L(this.map(function(a,b){return f.call(b.parentNode.children).filter(function(a){return a!==b})}),a)},empty:function(){return this.each(function(){this.innerHTML=""})},pluck:function(a){return this.map(function(){return this[a]})},show:function(){return this.each(function(){this.style.display=="none"&&(this.style.display=null),j(this,"").getPropertyValue("display")=="none"&&(this.style.display=K(this.nodeName))})},replaceWith:function(a){return this.before(a).remove()},wrap:function(a){return this.each(function(){c(this).wrapAll(c(a)[0].cloneNode(!1))})},wrapAll:function(a){return this[0]&&(c(this[0]).before(a=c(a)),a.append(this)),this},unwrap:function(){return this.parent().each(function(){c(this).replaceWith(c(this).children())}),this},clone:function(){return c(this.map(function(){return this.cloneNode(!0)}))},hide:function(){return this.css("display","none")},toggle:function(b){return(b===a?this.css("display")=="none":b)?this.show():this.hide()},prev:function(){return c(this.pluck("previousElementSibling"))},next:function(){return c(this.pluck("nextElementSibling"))},html:function(b){return b===a?this.length>0?this[0].innerHTML:null:this.each(function(a){var d=this.innerHTML;c(this).empty().append(M(this,b,a,d))})},text:function(b){return b===a?this.length>0?this[0].textContent:null:this.each(function(){this.textContent=b})},attr:function(c,d){var e;return typeof c=="string"&&d===a?this.length==0||this[0].nodeType!==1?a:c=="value"&&this[0].nodeName=="INPUT"?this.val():!(e=this[0].getAttribute(c))&&c in this[0]?this[0][c]:e:this.each(function(a){if(this.nodeType!==1)return;if(B(c))for(b in c)this.setAttribute(b,c[b]);else this.setAttribute(c,M(this,d,a,this.getAttribute(c)))})},removeAttr:function(a){return this.each(function(){this.nodeType===1&&this.removeAttribute(a)})},prop:function(b,c){return c===a?this[0]?this[0][b]:a:this.each(function(a){this[b]=M(this,c,a,this[b])})},data:function(b,c){var d=this.attr("data-"+H(b),c);return d!==null?d:a},val:function(b){return b===a?this.length>0?this[0].value:a:this.each(function(a){this.value=M(this,b,a,this.value)})},offset:function(){if(this.length==0)return null;var a=this[0].getBoundingClientRect();return{left:a.left+window.pageXOffset,top:a.top+window.pageYOffset,width:a.width,height:a.height}},css:function(c,d){if(d===a&&typeof c=="string")return this.length==0?a:this[0].style[x(c)]||j(this[0],"").getPropertyValue(c);var e="";for(b in c)typeof c[b]=="string"&&c[b]==""?this.each(function(){this.style.removeProperty(H(b))}):e+=H(b)+":"+J(b,c[b])+";";return typeof c=="string"&&(d==""?this.each(function(){this.style.removeProperty(H(c))}):e=H(c)+":"+J(c,d)),this.each(function(){this.style.cssText+=";"+e})},index:function(a){return a?this.indexOf(c(a)[0]):this.parent().children().indexOf(this[0])},hasClass:function(a){return this.length<1?!1:I(a).test(this[0].className)},addClass:function(a){return this.each(function(b){d=[];var e=this.className,f=M(this,a,b,e);f.split(/\s+/g).forEach(function(a){c(this).hasClass(a)||d.push(a)},this),d.length&&(this.className+=(e?" ":"")+d.join(" "))})},removeClass:function(b){return this.each(function(c){if(b===a)return this.className="";d=this.className,M(this,b,c,d).split(/\s+/g).forEach(function(a){d=d.replace(I(a)," ")}),this.className=d.trim()})},toggleClass:function(b,d){return this.each(function(e){var f=M(this,b,e,this.className);(d===a?!c(this).hasClass(f):d)?c(this).addClass(f):c(this).removeClass(f)})}},["width","height"].forEach(function(b){c.fn[b]=function(d){var e,f=b.replace(/./,function(a){return a[0].toUpperCase()});return d===a?this[0]==window?window["inner"+f]:this[0]==g?g.documentElement["offset"+f]:(e=this.offset())&&e[b]:this.each(function(a){var e=c(this);e.css(b,M(this,d,a,e[b]()))})}}),n.forEach(function(a,b){c.fn[a]=function(){var a=c.map(arguments,function(a){return B(a)?a:w.fragment(a)});if(a.length<1)return this;var d=this.length,e=d>1,f=b<2;return this.each(function(c,g){for(var h=0;h<a.length;h++){var i=a[f?a.length-h-1:h];O(i,function(a){a.nodeName!=null&&a.nodeName.toUpperCase()==="SCRIPT"&&(!a.type||a.type==="text/javascript")&&window.eval.call(window,a.innerHTML)}),e&&c<d-1&&(i=i.cloneNode(!0)),N(b,g,i)}})},c.fn[b%2?a+"To":"insert"+(b?"Before":"After")]=function(b){return c(b)[a](this),this}}),w.Z.prototype=c.fn,w.camelize=x,w.uniq=y,c.zepto=w,c}();window.Zepto=Zepto,"$"in window||(window.$=Zepto),function(a){function f(a){return a._zid||(a._zid=d++)}function g(a,b,d,e){b=h(b);if(b.ns)var g=i(b.ns);return(c[f(a)]||[]).filter(function(a){return a&&(!b.e||a.e==b.e)&&(!b.ns||g.test(a.ns))&&(!d||f(a.fn)===f(d))&&(!e||a.sel==e)})}function h(a){var b=(""+a).split(".");return{e:b[0],ns:b.slice(1).sort().join(" ")}}function i(a){return new RegExp("(?:^| )"+a.replace(" "," .* ?")+"(?: |$)")}function j(b,c,d){a.isObject(b)?a.each(b,d):b.split(/\s/).forEach(function(a){d(a,c)})}function k(b,d,e,g,i,k){k=!!k;var l=f(b),m=c[l]||(c[l]=[]);j(d,e,function(c,d){var e=i&&i(d,c),f=e||d,j=function(a){var c=f.apply(b,[a].concat(a.data));return c===!1&&a.preventDefault(),c},l=a.extend(h(c),{fn:d,proxy:j,sel:g,del:e,i:m.length});m.push(l),b.addEventListener(l.e,j,k)})}function l(a,b,d,e){var h=f(a);j(b||"",d,function(b,d){g(a,b,d,e).forEach(function(b){delete c[h][b.i],a.removeEventListener(b.e,b.proxy,!1)})})}function p(b){var c=a.extend({originalEvent:b},b);return a.each(o,function(a,d){c[a]=function(){return this[d]=m,b[a].apply(b,arguments)},c[d]=n}),c}function q(a){if(!("defaultPrevented"in a)){a.defaultPrevented=!1;var b=a.preventDefault;a.preventDefault=function(){this.defaultPrevented=!0,b.call(this)}}}var b=a.zepto.qsa,c={},d=1,e={};e.click=e.mousedown=e.mouseup=e.mousemove="MouseEvents",a.event={add:k,remove:l},a.proxy=function(b,c){if(a.isFunction(b)){var d=function(){return b.apply(c,arguments)};return d._zid=f(b),d}if(typeof c=="string")return a.proxy(b[c],b);throw new TypeError("expected function")},a.fn.bind=function(a,b){return this.each(function(){k(this,a,b)})},a.fn.unbind=function(a,b){return this.each(function(){l(this,a,b)})},a.fn.one=function(a,b){return this.each(function(c,d){k(this,a,b,null,function(a,b){return function(){var c=a.apply(d,arguments);return l(d,b,a),c}})})};var m=function(){return!0},n=function(){return!1},o={preventDefault:"isDefaultPrevented",stopImmediatePropagation:"isImmediatePropagationStopped",stopPropagation:"isPropagationStopped"};a.fn.delegate=function(b,c,d){var e=!1;if(c=="blur"||c=="focus")a.iswebkit?c=c=="blur"?"focusout":c=="focus"?"focusin":c:e=!0;return this.each(function(f,g){k(g,c,d,b,function(c){return function(d){var e,f=a(d.target).closest(b,g).get(0);if(f)return e=a.extend(p(d),{currentTarget:f,liveFired:g}),c.apply(f,[e].concat([].slice.call(arguments,1)))}},e)})},a.fn.undelegate=function(a,b,c){return this.each(function(){l(this,b,c,a)})},a.fn.live=function(b,c){return a(document.body).delegate(this.selector,b,c),this},a.fn.die=function(b,c){return a(document.body).undelegate(this.selector,b,c),this},a.fn.on=function(b,c,d){return c==undefined||a.isFunction(c)?this.bind(b,c):this.delegate(c,b,d)},a.fn.off=function(b,c,d){return c==undefined||a.isFunction(c)?this.unbind(b,c):this.undelegate(c,b,d)},a.fn.trigger=function(b,c){return typeof b=="string"&&(b=a.Event(b)),q(b),b.data=c,this.each(function(){"dispatchEvent"in this&&this.dispatchEvent(b)})},a.fn.triggerHandler=function(b,c){var d,e;return this.each(function(f,h){d=p(typeof b=="string"?a.Event(b):b),d.data=c,d.target=h,a.each(g(h,b.type||b),function(a,b){e=b.proxy(d);if(d.isImmediatePropagationStopped())return!1})}),e},"focusin focusout load resize scroll unload click dblclick mousedown mouseup mousemove mouseover mouseout change select keydown keypress keyup error".split(" ").forEach(function(b){a.fn[b]=function(a){return this.bind(b,a)}}),["focus","blur"].forEach(function(b){a.fn[b]=function(a){if(a)this.bind(b,a);else if(this.length)try{this.get(0)[b]()}catch(c){}return this}}),a.Event=function(a,b){var c=document.createEvent(e[a]||"Events"),d=!0;if(b)for(var f in b)f=="bubbles"?d=!!b[f]:c[f]=b[f];return c.initEvent(a,d,!0,null,null,null,null,null,null,null,null,null,null,null,null),c}}(Zepto),function(a){function b(a){var b=this.os={},c=this.browser={},d=a.match(/WebKit\/([\d.]+)/),e=a.match(/(Android)\s+([\d.]+)/),f=a.match(/(iPad).*OS\s([\d_]+)/),g=!f&&a.match(/(iPhone\sOS)\s([\d_]+)/),h=a.match(/(webOS|hpwOS)[\s\/]([\d.]+)/),i=h&&a.match(/TouchPad/),j=a.match(/Kindle\/([\d.]+)/),k=a.match(/Silk\/([\d._]+)/),l=a.match(/(BlackBerry).*Version\/([\d.]+)/);if(c.webkit=!!d)c.version=d[1];e&&(b.android=!0,b.version=e[2]),g&&(b.ios=b.iphone=!0,b.version=g[2].replace(/_/g,".")),f&&(b.ios=b.ipad=!0,b.version=f[2].replace(/_/g,".")),h&&(b.webos=!0,b.version=h[2]),i&&(b.touchpad=!0),l&&(b.blackberry=!0,b.version=l[2]),j&&(b.kindle=!0,b.version=j[1]),k&&(c.silk=!0,c.version=k[1]),!k&&b.android&&a.match(/Kindle Fire/)&&(c.silk=!0)}b.call(a,navigator.userAgent),a.__detect=b}(Zepto),function(a,b){function l(a){return a.toLowerCase()}function m(a){return d?d+a:l(a)}var c="",d,e,f,g={Webkit:"webkit",Moz:"",O:"o",ms:"MS"},h=window.document,i=h.createElement("div"),j=/^((translate|rotate|scale)(X|Y|Z|3d)?|matrix(3d)?|perspective|skew(X|Y)?)$/i,k={};a.each(g,function(a,e){if(i.style[a+"TransitionProperty"]!==b)return c="-"+l(a)+"-",d=e,!1}),k[c+"transition-property"]=k[c+"transition-duration"]=k[c+"transition-timing-function"]=k[c+"animation-name"]=k[c+"animation-duration"]="",a.fx={off:d===b&&i.style.transitionProperty===b,cssPrefix:c,transitionEnd:m("TransitionEnd"),animationEnd:m("AnimationEnd")},a.fn.animate=function(b,c,d,e){return a.isObject(c)&&(d=c.easing,e=c.complete,c=c.duration),c&&(c/=1e3),this.anim(b,c,d,e)},a.fn.anim=function(d,e,f,g){var h,i={},l,m=this,n,o=a.fx.transitionEnd;e===b&&(e=.4),a.fx.off&&(e=0);if(typeof d=="string")i[c+"animation-name"]=d,i[c+"animation-duration"]=e+"s",o=a.fx.animationEnd;else{for(l in d)j.test(l)?(h||(h=[]),h.push(l+"("+d[l]+")")):i[l]=d[l];h&&(i[c+"transform"]=h.join(" ")),!a.fx.off&&typeof d=="object"&&(i[c+"transition-property"]=Object.keys(d).join(", "),i[c+"transition-duration"]=e+"s",i[c+"transition-timing-function"]=f||"linear")}return n=function(b){if(typeof b!="undefined"){if(b.target!==b.currentTarget)return;a(b.target).unbind(o,arguments.callee)}a(this).css(k),g&&g.call(this)},e>0&&this.bind(o,n),setTimeout(function(){m.css(i),e<=0&&setTimeout(function(){m.each(function(){n.call(this)})},0)},0),this},i=null}(Zepto),function($){function triggerAndReturn(a,b,c){var d=$.Event(b);return $(a).trigger(d,c),!d.defaultPrevented}function triggerGlobal(a,b,c,d){if(a.global)return triggerAndReturn(b||document,c,d)}function ajaxStart(a){a.global&&$.active++===0&&triggerGlobal(a,null,"ajaxStart")}function ajaxStop(a){a.global&&!--$.active&&triggerGlobal(a,null,"ajaxStop")}function ajaxBeforeSend(a,b){var c=b.context;if(b.beforeSend.call(c,a,b)===!1||triggerGlobal(b,c,"ajaxBeforeSend",[a,b])===!1)return!1;triggerGlobal(b,c,"ajaxSend",[a,b])}function ajaxSuccess(a,b,c){var d=c.context,e="success";c.success.call(d,a,e,b),triggerGlobal(c,d,"ajaxSuccess",[b,c,a]),ajaxComplete(e,b,c)}function ajaxError(a,b,c,d){var e=d.context;d.error.call(e,c,b,a),triggerGlobal(d,e,"ajaxError",[c,d,a]),ajaxComplete(b,c,d)}function ajaxComplete(a,b,c){var d=c.context;c.complete.call(d,b,a),triggerGlobal(c,d,"ajaxComplete",[b,c]),ajaxStop(c)}function empty(){}function mimeToDataType(a){return a&&(a==htmlType?"html":a==jsonType?"json":scriptTypeRE.test(a)?"script":xmlTypeRE.test(a)&&"xml")||"text"}function appendQuery(a,b){return(a+"&"+b).replace(/[&?]{1,2}/,"?")}function serializeData(a){isObject(a.data)&&(a.data=$.param(a.data)),a.data&&(!a.type||a.type.toUpperCase()=="GET")&&(a.url=appendQuery(a.url,a.data))}function serialize(a,b,c,d){var e=$.isArray(b);$.each(b,function(b,f){d&&(b=c?d:d+"["+(e?"":b)+"]"),!d&&e?a.add(f.name,f.value):(c?$.isArray(f):isObject(f))?serialize(a,f,c,b):a.add(b,f)})}var jsonpID=0,isObject=$.isObject,document=window.document,key,name,rscript=/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,scriptTypeRE=/^(?:text|application)\/javascript/i,xmlTypeRE=/^(?:text|application)\/xml/i,jsonType="application/json",htmlType="text/html",blankRE=/^\s*$/;$.active=0,$.ajaxJSONP=function(a){var b="jsonp"+ ++jsonpID,c=document.createElement("script"),d=function(){$(c).remove(),b in window&&(window[b]=empty),ajaxComplete("abort",e,a)},e={abort:d},f;return a.error&&(c.onerror=function(){e.abort(),a.error()}),window[b]=function(d){clearTimeout(f),$(c).remove(),delete window[b],ajaxSuccess(d,e,a)},serializeData(a),c.src=a.url.replace(/=\?/,"="+b),$("head").append(c),a.timeout>0&&(f=setTimeout(function(){e.abort(),ajaxComplete("timeout",e,a)},a.timeout)),e},$.ajaxSettings={type:"GET",beforeSend:empty,success:empty,error:empty,complete:empty,context:null,global:!0,xhr:function(){return new window.XMLHttpRequest},accepts:{script:"text/javascript, application/javascript",json:jsonType,xml:"application/xml, text/xml",html:htmlType,text:"text/plain"},crossDomain:!1,timeout:0},$.ajax=function(options){var settings=$.extend({},options||{});for(key in $.ajaxSettings)settings[key]===undefined&&(settings[key]=$.ajaxSettings[key]);ajaxStart(settings),settings.crossDomain||(settings.crossDomain=/^([\w-]+:)?\/\/([^\/]+)/.test(settings.url)&&RegExp.$2!=window.location.host);var dataType=settings.dataType,hasPlaceholder=/=\?/.test(settings.url);if(dataType=="jsonp"||hasPlaceholder)return hasPlaceholder||(settings.url=appendQuery(settings.url,"callback=?")),$.ajaxJSONP(settings);settings.url||(settings.url=window.location.toString()),serializeData(settings);var mime=settings.accepts[dataType],baseHeaders={},protocol=/^([\w-]+:)\/\//.test(settings.url)?RegExp.$1:window.location.protocol,xhr=$.ajaxSettings.xhr(),abortTimeout;settings.crossDomain||(baseHeaders["X-Requested-With"]="XMLHttpRequest"),mime&&(baseHeaders.Accept=mime,mime.indexOf(",")>-1&&(mime=mime.split(",",2)[0]),xhr.overrideMimeType&&xhr.overrideMimeType(mime));if(settings.contentType||settings.data&&settings.type.toUpperCase()!="GET")baseHeaders["Content-Type"]=settings.contentType||"application/x-www-form-urlencoded";settings.headers=$.extend(baseHeaders,settings.headers||{}),xhr.onreadystatechange=function(){if(xhr.readyState==4){clearTimeout(abortTimeout);var result,error=!1;if(xhr.status>=200&&xhr.status<300||xhr.status==304||xhr.status==0&&protocol=="file:"){dataType=dataType||mimeToDataType(xhr.getResponseHeader("content-type")),result=xhr.responseText;try{dataType=="script"?(1,eval)(result):dataType=="xml"?result=xhr.responseXML:dataType=="json"&&(result=blankRE.test(result)?null:JSON.parse(result))}catch(e){error=e}error?ajaxError(error,"parsererror",xhr,settings):ajaxSuccess(result,xhr,settings)}else ajaxError(null,"error",xhr,settings)}};var async="async"in settings?settings.async:!0;xhr.open(settings.type,settings.url,async);for(name in settings.headers)xhr.setRequestHeader(name,settings.headers[name]);return ajaxBeforeSend(xhr,settings)===!1?(xhr.abort(),!1):(settings.timeout>0&&(abortTimeout=setTimeout(function(){xhr.onreadystatechange=empty,xhr.abort(),ajaxError(null,"timeout",xhr,settings)},settings.timeout)),xhr.send(settings.data?settings.data:null),xhr)},$.get=function(a,b){return $.ajax({url:a,success:b})},$.post=function(a,b,c,d){return $.isFunction(b)&&(d=d||c,c=b,b=null),$.ajax({type:"POST",url:a,data:b,success:c,dataType:d})},$.getJSON=function(a,b){return $.ajax({url:a,success:b,dataType:"json"})},$.fn.load=function(a,b){if(!this.length)return this;var c=this,d=a.split(/\s/),e;return d.length>1&&(a=d[0],e=d[1]),$.get(a,function(a){c.html(e?$(document.createElement("div")).html(a.replace(rscript,"")).find(e).html():a),b&&b.call(c)}),this};var escape=encodeURIComponent;$.param=function(a,b){var c=[];return c.add=function(a,b){this.push(escape(a)+"="+escape(b))},serialize(c,a,b),c.join("&").replace("%20","+")}}(Zepto),function(a){a.fn.serializeArray=function(){var b=[],c;return a(Array.prototype.slice.call(this.get(0).elements)).each(function(){c=a(this);var d=c.attr("type");this.nodeName.toLowerCase()!="fieldset"&&!this.disabled&&d!="submit"&&d!="reset"&&d!="button"&&(d!="radio"&&d!="checkbox"||this.checked)&&b.push({name:c.attr("name"),value:c.val()})}),b},a.fn.serialize=function(){var a=[];return this.serializeArray().forEach(function(b){a.push(encodeURIComponent(b.name)+"="+encodeURIComponent(b.value))}),a.join("&")},a.fn.submit=function(b){if(b)this.bind("submit",b);else if(this.length){var c=a.Event("submit");this.eq(0).trigger(c),c.defaultPrevented||this.get(0).submit()}return this}}(Zepto),function(a){function d(a){return"tagName"in a?a:a.parentNode}function e(a,b,c,d){var e=Math.abs(a-b),f=Math.abs(c-d);return e>=f?a-b>0?"Left":"Right":c-d>0?"Up":"Down"}function h(){g=null,b.last&&(b.el.trigger("longTap"),b={})}function i(){g&&clearTimeout(g),g=null}var b={},c,f=750,g;a(document).ready(function(){var j,k;a(document.body).bind("touchstart",function(e){j=Date.now(),k=j-(b.last||j),b.el=a(d(e.touches[0].target)),c&&clearTimeout(c),b.x1=e.touches[0].pageX,b.y1=e.touches[0].pageY,k>0&&k<=250&&(b.isDoubleTap=!0),b.last=j,g=setTimeout(h,f)}).bind("touchmove",function(a){i(),b.x2=a.touches[0].pageX,b.y2=a.touches[0].pageY}).bind("touchend",function(a){i(),b.isDoubleTap?(b.el.trigger("doubleTap"),b={}):b.x2&&Math.abs(b.x1-b.x2)>30||b.y2&&Math.abs(b.y1-b.y2)>30?(b.el.trigger("swipe")&&b.el.trigger("swipe"+e(b.x1,b.x2,b.y1,b.y2)),b={}):"last"in b&&(b.el.trigger("tap"),c=setTimeout(function(){c=null,b.el.trigger("singleTap"),b={}},250))}).bind("touchcancel",function(){c&&clearTimeout(c),g&&clearTimeout(g),g=c=null,b={}})}),["swipe","swipeLeft","swipeRight","swipeUp","swipeDown","doubleTap","tap","singleTap","longTap"].forEach(function(b){a.fn[b]=function(a){return this.bind(b,a)}})}(Zepto);// Backbone.js 0.9.2

// (c) 2010-2012 Jeremy Ashkenas, DocumentCloud Inc.
// Backbone may be freely distributed under the MIT license.
// For all details and documentation:
// http://backbonejs.org
(function(){var l=this,y=l.Backbone,z=Array.prototype.slice,A=Array.prototype.splice,g;g="undefined"!==typeof exports?exports:l.Backbone={};g.VERSION="0.9.2";var f=l._;!f&&"undefined"!==typeof require&&(f=require("underscore"));var i=l.jQuery||l.Zepto||l.ender;g.setDomLibrary=function(a){i=a};g.noConflict=function(){l.Backbone=y;return this};g.emulateHTTP=!1;g.emulateJSON=!1;var p=/\s+/,k=g.Events={on:function(a,b,c){var d,e,f,g,j;if(!b)return this;a=a.split(p);for(d=this._callbacks||(this._callbacks=
{});e=a.shift();)f=(j=d[e])?j.tail:{},f.next=g={},f.context=c,f.callback=b,d[e]={tail:g,next:j?j.next:f};return this},off:function(a,b,c){var d,e,h,g,j,q;if(e=this._callbacks){if(!a&&!b&&!c)return delete this._callbacks,this;for(a=a?a.split(p):f.keys(e);d=a.shift();)if(h=e[d],delete e[d],h&&(b||c))for(g=h.tail;(h=h.next)!==g;)if(j=h.callback,q=h.context,b&&j!==b||c&&q!==c)this.on(d,j,q);return this}},trigger:function(a){var b,c,d,e,f,g;if(!(d=this._callbacks))return this;f=d.all;a=a.split(p);for(g=
z.call(arguments,1);b=a.shift();){if(c=d[b])for(e=c.tail;(c=c.next)!==e;)c.callback.apply(c.context||this,g);if(c=f){e=c.tail;for(b=[b].concat(g);(c=c.next)!==e;)c.callback.apply(c.context||this,b)}}return this}};k.bind=k.on;k.unbind=k.off;var o=g.Model=function(a,b){var c;a||(a={});b&&b.parse&&(a=this.parse(a));if(c=n(this,"defaults"))a=f.extend({},c,a);b&&b.collection&&(this.collection=b.collection);this.attributes={};this._escapedAttributes={};this.cid=f.uniqueId("c");this.changed={};this._silent=
{};this._pending={};this.set(a,{silent:!0});this.changed={};this._silent={};this._pending={};this._previousAttributes=f.clone(this.attributes);this.initialize.apply(this,arguments)};f.extend(o.prototype,k,{changed:null,_silent:null,_pending:null,idAttribute:"id",initialize:function(){},toJSON:function(){return f.clone(this.attributes)},get:function(a){return this.attributes[a]},escape:function(a){var b;if(b=this._escapedAttributes[a])return b;b=this.get(a);return this._escapedAttributes[a]=f.escape(null==
b?"":""+b)},has:function(a){return null!=this.get(a)},set:function(a,b,c){var d,e;f.isObject(a)||null==a?(d=a,c=b):(d={},d[a]=b);c||(c={});if(!d)return this;d instanceof o&&(d=d.attributes);if(c.unset)for(e in d)d[e]=void 0;if(!this._validate(d,c))return!1;this.idAttribute in d&&(this.id=d[this.idAttribute]);var b=c.changes={},h=this.attributes,g=this._escapedAttributes,j=this._previousAttributes||{};for(e in d){a=d[e];if(!f.isEqual(h[e],a)||c.unset&&f.has(h,e))delete g[e],(c.silent?this._silent:
b)[e]=!0;c.unset?delete h[e]:h[e]=a;!f.isEqual(j[e],a)||f.has(h,e)!=f.has(j,e)?(this.changed[e]=a,c.silent||(this._pending[e]=!0)):(delete this.changed[e],delete this._pending[e])}c.silent||this.change(c);return this},unset:function(a,b){(b||(b={})).unset=!0;return this.set(a,null,b)},clear:function(a){(a||(a={})).unset=!0;return this.set(f.clone(this.attributes),a)},fetch:function(a){var a=a?f.clone(a):{},b=this,c=a.success;a.success=function(d,e,f){if(!b.set(b.parse(d,f),a))return!1;c&&c(b,d)};
a.error=g.wrapError(a.error,b,a);return(this.sync||g.sync).call(this,"read",this,a)},save:function(a,b,c){var d,e;f.isObject(a)||null==a?(d=a,c=b):(d={},d[a]=b);c=c?f.clone(c):{};if(c.wait){if(!this._validate(d,c))return!1;e=f.clone(this.attributes)}a=f.extend({},c,{silent:!0});if(d&&!this.set(d,c.wait?a:c))return!1;var h=this,i=c.success;c.success=function(a,b,e){b=h.parse(a,e);if(c.wait){delete c.wait;b=f.extend(d||{},b)}if(!h.set(b,c))return false;i?i(h,a):h.trigger("sync",h,a,c)};c.error=g.wrapError(c.error,
h,c);b=this.isNew()?"create":"update";b=(this.sync||g.sync).call(this,b,this,c);c.wait&&this.set(e,a);return b},destroy:function(a){var a=a?f.clone(a):{},b=this,c=a.success,d=function(){b.trigger("destroy",b,b.collection,a)};if(this.isNew())return d(),!1;a.success=function(e){a.wait&&d();c?c(b,e):b.trigger("sync",b,e,a)};a.error=g.wrapError(a.error,b,a);var e=(this.sync||g.sync).call(this,"delete",this,a);a.wait||d();return e},url:function(){var a=n(this,"urlRoot")||n(this.collection,"url")||t();
return this.isNew()?a:a+("/"==a.charAt(a.length-1)?"":"/")+encodeURIComponent(this.id)},parse:function(a){return a},clone:function(){return new this.constructor(this.attributes)},isNew:function(){return null==this.id},change:function(a){a||(a={});var b=this._changing;this._changing=!0;for(var c in this._silent)this._pending[c]=!0;var d=f.extend({},a.changes,this._silent);this._silent={};for(c in d)this.trigger("change:"+c,this,this.get(c),a);if(b)return this;for(;!f.isEmpty(this._pending);){this._pending=
{};this.trigger("change",this,a);for(c in this.changed)!this._pending[c]&&!this._silent[c]&&delete this.changed[c];this._previousAttributes=f.clone(this.attributes)}this._changing=!1;return this},hasChanged:function(a){return!arguments.length?!f.isEmpty(this.changed):f.has(this.changed,a)},changedAttributes:function(a){if(!a)return this.hasChanged()?f.clone(this.changed):!1;var b,c=!1,d=this._previousAttributes,e;for(e in a)if(!f.isEqual(d[e],b=a[e]))(c||(c={}))[e]=b;return c},previous:function(a){return!arguments.length||
!this._previousAttributes?null:this._previousAttributes[a]},previousAttributes:function(){return f.clone(this._previousAttributes)},isValid:function(){return!this.validate(this.attributes)},_validate:function(a,b){if(b.silent||!this.validate)return!0;var a=f.extend({},this.attributes,a),c=this.validate(a,b);if(!c)return!0;b&&b.error?b.error(this,c,b):this.trigger("error",this,c,b);return!1}});var r=g.Collection=function(a,b){b||(b={});b.model&&(this.model=b.model);b.comparator&&(this.comparator=b.comparator);
this._reset();this.initialize.apply(this,arguments);a&&this.reset(a,{silent:!0,parse:b.parse})};f.extend(r.prototype,k,{model:o,initialize:function(){},toJSON:function(a){return this.map(function(b){return b.toJSON(a)})},add:function(a,b){var c,d,e,g,i,j={},k={},l=[];b||(b={});a=f.isArray(a)?a.slice():[a];c=0;for(d=a.length;c<d;c++){if(!(e=a[c]=this._prepareModel(a[c],b)))throw Error("Can't add an invalid model to a collection");g=e.cid;i=e.id;j[g]||this._byCid[g]||null!=i&&(k[i]||this._byId[i])?
l.push(c):j[g]=k[i]=e}for(c=l.length;c--;)a.splice(l[c],1);c=0;for(d=a.length;c<d;c++)(e=a[c]).on("all",this._onModelEvent,this),this._byCid[e.cid]=e,null!=e.id&&(this._byId[e.id]=e);this.length+=d;A.apply(this.models,[null!=b.at?b.at:this.models.length,0].concat(a));this.comparator&&this.sort({silent:!0});if(b.silent)return this;c=0;for(d=this.models.length;c<d;c++)if(j[(e=this.models[c]).cid])b.index=c,e.trigger("add",e,this,b);return this},remove:function(a,b){var c,d,e,g;b||(b={});a=f.isArray(a)?
a.slice():[a];c=0;for(d=a.length;c<d;c++)if(g=this.getByCid(a[c])||this.get(a[c]))delete this._byId[g.id],delete this._byCid[g.cid],e=this.indexOf(g),this.models.splice(e,1),this.length--,b.silent||(b.index=e,g.trigger("remove",g,this,b)),this._removeReference(g);return this},push:function(a,b){a=this._prepareModel(a,b);this.add(a,b);return a},pop:function(a){var b=this.at(this.length-1);this.remove(b,a);return b},unshift:function(a,b){a=this._prepareModel(a,b);this.add(a,f.extend({at:0},b));return a},
shift:function(a){var b=this.at(0);this.remove(b,a);return b},get:function(a){return null==a?void 0:this._byId[null!=a.id?a.id:a]},getByCid:function(a){return a&&this._byCid[a.cid||a]},at:function(a){return this.models[a]},where:function(a){return f.isEmpty(a)?[]:this.filter(function(b){for(var c in a)if(a[c]!==b.get(c))return!1;return!0})},sort:function(a){a||(a={});if(!this.comparator)throw Error("Cannot sort a set without a comparator");var b=f.bind(this.comparator,this);1==this.comparator.length?
this.models=this.sortBy(b):this.models.sort(b);a.silent||this.trigger("reset",this,a);return this},pluck:function(a){return f.map(this.models,function(b){return b.get(a)})},reset:function(a,b){a||(a=[]);b||(b={});for(var c=0,d=this.models.length;c<d;c++)this._removeReference(this.models[c]);this._reset();this.add(a,f.extend({silent:!0},b));b.silent||this.trigger("reset",this,b);return this},fetch:function(a){a=a?f.clone(a):{};void 0===a.parse&&(a.parse=!0);var b=this,c=a.success;a.success=function(d,
e,f){b[a.add?"add":"reset"](b.parse(d,f),a);c&&c(b,d)};a.error=g.wrapError(a.error,b,a);return(this.sync||g.sync).call(this,"read",this,a)},create:function(a,b){var c=this,b=b?f.clone(b):{},a=this._prepareModel(a,b);if(!a)return!1;b.wait||c.add(a,b);var d=b.success;b.success=function(e,f){b.wait&&c.add(e,b);d?d(e,f):e.trigger("sync",a,f,b)};a.save(null,b);return a},parse:function(a){return a},chain:function(){return f(this.models).chain()},_reset:function(){this.length=0;this.models=[];this._byId=
{};this._byCid={}},_prepareModel:function(a,b){b||(b={});a instanceof o?a.collection||(a.collection=this):(b.collection=this,a=new this.model(a,b),a._validate(a.attributes,b)||(a=!1));return a},_removeReference:function(a){this==a.collection&&delete a.collection;a.off("all",this._onModelEvent,this)},_onModelEvent:function(a,b,c,d){("add"==a||"remove"==a)&&c!=this||("destroy"==a&&this.remove(b,d),b&&a==="change:"+b.idAttribute&&(delete this._byId[b.previous(b.idAttribute)],this._byId[b.id]=b),this.trigger.apply(this,
arguments))}});f.each("forEach,each,map,reduce,reduceRight,find,detect,filter,select,reject,every,all,some,any,include,contains,invoke,max,min,sortBy,sortedIndex,toArray,size,first,initial,rest,last,without,indexOf,shuffle,lastIndexOf,isEmpty,groupBy".split(","),function(a){r.prototype[a]=function(){return f[a].apply(f,[this.models].concat(f.toArray(arguments)))}});var u=g.Router=function(a){a||(a={});a.routes&&(this.routes=a.routes);this._bindRoutes();this.initialize.apply(this,arguments)},B=/:\w+/g,
C=/\*\w+/g,D=/[-[\]{}()+?.,\\^$|#\s]/g;f.extend(u.prototype,k,{initialize:function(){},route:function(a,b,c){g.history||(g.history=new m);f.isRegExp(a)||(a=this._routeToRegExp(a));c||(c=this[b]);g.history.route(a,f.bind(function(d){d=this._extractParameters(a,d);c&&c.apply(this,d);this.trigger.apply(this,["route:"+b].concat(d));g.history.trigger("route",this,b,d)},this));return this},navigate:function(a,b){g.history.navigate(a,b)},_bindRoutes:function(){if(this.routes){var a=[],b;for(b in this.routes)a.unshift([b,
this.routes[b]]);b=0;for(var c=a.length;b<c;b++)this.route(a[b][0],a[b][1],this[a[b][1]])}},_routeToRegExp:function(a){a=a.replace(D,"\\$&").replace(B,"([^/]+)").replace(C,"(.*?)");return RegExp("^"+a+"$")},_extractParameters:function(a,b){return a.exec(b).slice(1)}});var m=g.History=function(){this.handlers=[];f.bindAll(this,"checkUrl")},s=/^[#\/]/,E=/msie [\w.]+/;m.started=!1;f.extend(m.prototype,k,{interval:50,getHash:function(a){return(a=(a?a.location:window.location).href.match(/#(.*)$/))?a[1]:
""},getFragment:function(a,b){if(null==a)if(this._hasPushState||b){var a=window.location.pathname,c=window.location.search;c&&(a+=c)}else a=this.getHash();a.indexOf(this.options.root)||(a=a.substr(this.options.root.length));return a.replace(s,"")},start:function(a){if(m.started)throw Error("Backbone.history has already been started");m.started=!0;this.options=f.extend({},{root:"/"},this.options,a);this._wantsHashChange=!1!==this.options.hashChange;this._wantsPushState=!!this.options.pushState;this._hasPushState=
!(!this.options.pushState||!window.history||!window.history.pushState);var a=this.getFragment(),b=document.documentMode;if(b=E.exec(navigator.userAgent.toLowerCase())&&(!b||7>=b))this.iframe=i('<iframe src="javascript:0" tabindex="-1" />').hide().appendTo("body")[0].contentWindow,this.navigate(a);this._hasPushState?i(window).bind("popstate",this.checkUrl):this._wantsHashChange&&"onhashchange"in window&&!b?i(window).bind("hashchange",this.checkUrl):this._wantsHashChange&&(this._checkUrlInterval=setInterval(this.checkUrl,
this.interval));this.fragment=a;a=window.location;b=a.pathname==this.options.root;if(this._wantsHashChange&&this._wantsPushState&&!this._hasPushState&&!b)return this.fragment=this.getFragment(null,!0),window.location.replace(this.options.root+"#"+this.fragment),!0;this._wantsPushState&&this._hasPushState&&b&&a.hash&&(this.fragment=this.getHash().replace(s,""),window.history.replaceState({},document.title,a.protocol+"//"+a.host+this.options.root+this.fragment));if(!this.options.silent)return this.loadUrl()},
stop:function(){i(window).unbind("popstate",this.checkUrl).unbind("hashchange",this.checkUrl);clearInterval(this._checkUrlInterval);m.started=!1},route:function(a,b){this.handlers.unshift({route:a,callback:b})},checkUrl:function(){var a=this.getFragment();a==this.fragment&&this.iframe&&(a=this.getFragment(this.getHash(this.iframe)));if(a==this.fragment)return!1;this.iframe&&this.navigate(a);this.loadUrl()||this.loadUrl(this.getHash())},loadUrl:function(a){var b=this.fragment=this.getFragment(a);return f.any(this.handlers,
function(a){if(a.route.test(b))return a.callback(b),!0})},navigate:function(a,b){if(!m.started)return!1;if(!b||!0===b)b={trigger:b};var c=(a||"").replace(s,"");this.fragment!=c&&(this._hasPushState?(0!=c.indexOf(this.options.root)&&(c=this.options.root+c),this.fragment=c,window.history[b.replace?"replaceState":"pushState"]({},document.title,c)):this._wantsHashChange?(this.fragment=c,this._updateHash(window.location,c,b.replace),this.iframe&&c!=this.getFragment(this.getHash(this.iframe))&&(b.replace||
this.iframe.document.open().close(),this._updateHash(this.iframe.location,c,b.replace))):window.location.assign(this.options.root+a),b.trigger&&this.loadUrl(a))},_updateHash:function(a,b,c){c?a.replace(a.toString().replace(/(javascript:|#).*$/,"")+"#"+b):a.hash=b}});var v=g.View=function(a){this.cid=f.uniqueId("view");this._configure(a||{});this._ensureElement();this.initialize.apply(this,arguments);this.delegateEvents()},F=/^(\S+)\s*(.*)$/,w="model,collection,el,id,attributes,className,tagName".split(",");
f.extend(v.prototype,k,{tagName:"div",$:function(a){return this.$el.find(a)},initialize:function(){},render:function(){return this},remove:function(){this.$el.remove();return this},make:function(a,b,c){a=document.createElement(a);b&&i(a).attr(b);c&&i(a).html(c);return a},setElement:function(a,b){this.$el&&this.undelegateEvents();this.$el=a instanceof i?a:i(a);this.el=this.$el[0];!1!==b&&this.delegateEvents();return this},delegateEvents:function(a){if(a||(a=n(this,"events"))){this.undelegateEvents();
for(var b in a){var c=a[b];f.isFunction(c)||(c=this[a[b]]);if(!c)throw Error('Method "'+a[b]+'" does not exist');var d=b.match(F),e=d[1],d=d[2],c=f.bind(c,this),e=e+(".delegateEvents"+this.cid);""===d?this.$el.bind(e,c):this.$el.delegate(d,e,c)}}},undelegateEvents:function(){this.$el.unbind(".delegateEvents"+this.cid)},_configure:function(a){this.options&&(a=f.extend({},this.options,a));for(var b=0,c=w.length;b<c;b++){var d=w[b];a[d]&&(this[d]=a[d])}this.options=a},_ensureElement:function(){if(this.el)this.setElement(this.el,
!1);else{var a=n(this,"attributes")||{};this.id&&(a.id=this.id);this.className&&(a["class"]=this.className);this.setElement(this.make(this.tagName,a),!1)}}});o.extend=r.extend=u.extend=v.extend=function(a,b){var c=G(this,a,b);c.extend=this.extend;return c};var H={create:"POST",update:"PUT","delete":"DELETE",read:"GET"};g.sync=function(a,b,c){var d=H[a];c||(c={});var e={type:d,dataType:"json"};c.url||(e.url=n(b,"url")||t());if(!c.data&&b&&("create"==a||"update"==a))e.contentType="application/json",
e.data=JSON.stringify(b.toJSON());g.emulateJSON&&(e.contentType="application/x-www-form-urlencoded",e.data=e.data?{model:e.data}:{});if(g.emulateHTTP&&("PUT"===d||"DELETE"===d))g.emulateJSON&&(e.data._method=d),e.type="POST",e.beforeSend=function(a){a.setRequestHeader("X-HTTP-Method-Override",d)};"GET"!==e.type&&!g.emulateJSON&&(e.processData=!1);return i.ajax(f.extend(e,c))};g.wrapError=function(a,b,c){return function(d,e){e=d===b?e:d;a?a(b,e,c):b.trigger("error",b,e,c)}};var x=function(){},G=function(a,
b,c){var d;d=b&&b.hasOwnProperty("constructor")?b.constructor:function(){a.apply(this,arguments)};f.extend(d,a);x.prototype=a.prototype;d.prototype=new x;b&&f.extend(d.prototype,b);c&&f.extend(d,c);d.prototype.constructor=d;d.__super__=a.prototype;return d},n=function(a,b){return!a||!a[b]?null:f.isFunction(a[b])?a[b]():a[b]},t=function(){throw Error('A "url" property or function must be specified');}}).call(this);
/*
 * popcorn.js version 5f34b14
 * http://popcornjs.org
 *
 * Copyright 2011, Mozilla Foundation
 * Licensed under the MIT license
 */

(function(global, document) {

  // Popcorn.js does not support archaic browsers
  if ( !document.addEventListener ) {
    global.Popcorn = {
      isSupported: false
    };

    var methods = ( "byId forEach extend effects error guid sizeOf isArray nop position disable enable destroy" +
          "addTrackEvent removeTrackEvent getTrackEvents getTrackEvent getLastTrackEventId " +
          "timeUpdate plugin removePlugin compose effect xhr getJSONP getScript" ).split(/\s+/);

    while ( methods.length ) {
      global.Popcorn[ methods.shift() ] = function() {};
    }
    return;
  }

  var

  AP = Array.prototype,
  OP = Object.prototype,

  forEach = AP.forEach,
  slice = AP.slice,
  hasOwn = OP.hasOwnProperty,
  toString = OP.toString,

  // Copy global Popcorn (may not exist)
  _Popcorn = global.Popcorn,

  //  Ready fn cache
  readyStack = [],
  readyBound = false,
  readyFired = false,

  //  Non-public internal data object
  internal = {
    events: {
      hash: {},
      apis: {}
    }
  },

  //  Non-public `requestAnimFrame`
  //  http://paulirish.com/2011/requestanimationframe-for-smart-animating/
  requestAnimFrame = (function(){
    return global.requestAnimationFrame ||
      global.webkitRequestAnimationFrame ||
      global.mozRequestAnimationFrame ||
      global.oRequestAnimationFrame ||
      global.msRequestAnimationFrame ||
      function( callback, element ) {
        global.setTimeout( callback, 16 );
      };
  }()),

  //  Non-public `getKeys`, return an object's keys as an array
  getKeys = function( obj ) {
    return Object.keys ? Object.keys( obj ) : (function( obj ) {
      var item,
          list = [];

      for ( item in obj ) {
        if ( hasOwn.call( obj, item ) ) {
          list.push( item );
        }
      }
      return list;
    })( obj );
  },

  //  Declare constructor
  //  Returns an instance object.
  Popcorn = function( entity, options ) {
    //  Return new Popcorn object
    return new Popcorn.p.init( entity, options || null );
  };

  //  Popcorn API version, automatically inserted via build system.
  Popcorn.version = "5f34b14";

  //  Boolean flag allowing a client to determine if Popcorn can be supported
  Popcorn.isSupported = true;

  //  Instance caching
  Popcorn.instances = [];

  //  Declare a shortcut (Popcorn.p) to and a definition of
  //  the new prototype for our Popcorn constructor
  Popcorn.p = Popcorn.prototype = {

    init: function( entity, options ) {

      var matches, nodeName,
          self = this;

      //  Supports Popcorn(function () { /../ })
      //  Originally proposed by Daniel Brooks

      if ( typeof entity === "function" ) {

        //  If document ready has already fired
        if ( document.readyState === "complete" ) {

          entity( document, Popcorn );

          return;
        }
        //  Add `entity` fn to ready stack
        readyStack.push( entity );

        //  This process should happen once per page load
        if ( !readyBound ) {

          //  set readyBound flag
          readyBound = true;

          var DOMContentLoaded  = function() {

            readyFired = true;

            //  Remove global DOM ready listener
            document.removeEventListener( "DOMContentLoaded", DOMContentLoaded, false );

            //  Execute all ready function in the stack
            for ( var i = 0, readyStackLength = readyStack.length; i < readyStackLength; i++ ) {

              readyStack[ i ].call( document, Popcorn );

            }
            //  GC readyStack
            readyStack = null;
          };

          //  Register global DOM ready listener
          document.addEventListener( "DOMContentLoaded", DOMContentLoaded, false );
        }

        return;
      }

      if ( typeof entity === "string" ) {
        try {
          matches = document.querySelector( entity );
        } catch( e ) {
          throw new Error( "Popcorn.js Error: Invalid media element selector: " + entity );
        }
      }

      //  Get media element by id or object reference
      this.media = matches || entity;

      //  inner reference to this media element's nodeName string value
      nodeName = ( this.media.nodeName && this.media.nodeName.toLowerCase() ) || "video";

      //  Create an audio or video element property reference
      this[ nodeName ] = this.media;

      this.options = options || {};

      //  Resolve custom ID or default prefixed ID
      this.id = this.options.id || Popcorn.guid( nodeName );

      //  Throw if an attempt is made to use an ID that already exists
      if ( Popcorn.byId( this.id ) ) {
        throw new Error( "Popcorn.js Error: Cannot use duplicate ID (" + this.id + ")" );
      }

      this.isDestroyed = false;

      this.data = {

        // data structure of all
        running: {
          cue: []
        },

        // Executed by either timeupdate event or in rAF loop
        timeUpdate: Popcorn.nop,

        // Allows disabling a plugin per instance
        disabled: {},

        // Stores DOM event queues by type
        events: {},

        // Stores Special event hooks data
        hooks: {},

        // Store track event history data
        history: [],

        // Stores ad-hoc state related data]
        state: {
          volume: this.media.volume
        },

        // Store track event object references by trackId
        trackRefs: {},

        // Playback track event queues
        trackEvents: {
          byStart: [{

            start: -1,
            end: -1
          }],
          byEnd: [{
            start: -1,
            end: -1
          }],
          animating: [],
          startIndex: 0,
          endIndex: 0,
          previousUpdateTime: -1
        }
      };

      //  Register new instance
      Popcorn.instances.push( this );

      //  function to fire when video is ready
      var isReady = function() {

        // chrome bug: http://code.google.com/p/chromium/issues/detail?id=119598
        // it is possible the video's time is less than 0
        // this has the potential to call track events more than once, when they should not
        // start: 0, end: 1 will start, end, start again, when it should just start
        // just setting it to 0 if it is below 0 fixes this issue
        if ( self.media.currentTime < 0 ) {

          self.media.currentTime = 0;
        }

        self.media.removeEventListener( "loadeddata", isReady, false );

        var duration, videoDurationPlus,
            runningPlugins, runningPlugin, rpLength, rpNatives;

        //  Adding padding to the front and end of the arrays
        //  this is so we do not fall off either end
        duration = self.media.duration;

        //  Check for no duration info (NaN)
        videoDurationPlus = duration != duration ? Number.MAX_VALUE : duration + 1;

        Popcorn.addTrackEvent( self, {
          start: videoDurationPlus,
          end: videoDurationPlus
        });

        if ( self.options.frameAnimation ) {

          //  if Popcorn is created with frameAnimation option set to true,
          //  requestAnimFrame is used instead of "timeupdate" media event.
          //  This is for greater frame time accuracy, theoretically up to
          //  60 frames per second as opposed to ~4 ( ~every 15-250ms)
          self.data.timeUpdate = function () {

            Popcorn.timeUpdate( self, {} );

            // fire frame for each enabled active plugin of every type
            Popcorn.forEach( Popcorn.manifest, function( key, val ) {

              runningPlugins = self.data.running[ val ];

              // ensure there are running plugins on this type on this instance
              if ( runningPlugins ) {

                rpLength = runningPlugins.length;
                for ( var i = 0; i < rpLength; i++ ) {

                  runningPlugin = runningPlugins[ i ];
                  rpNatives = runningPlugin._natives;
                  rpNatives && rpNatives.frame &&
                    rpNatives.frame.call( self, {}, runningPlugin, self.currentTime() );
                }
              }
            });

            self.emit( "timeupdate" );

            !self.isDestroyed && requestAnimFrame( self.data.timeUpdate );
          };

          !self.isDestroyed && requestAnimFrame( self.data.timeUpdate );

        } else {

          self.data.timeUpdate = function( event ) {
            Popcorn.timeUpdate( self, event );
          };

          if ( !self.isDestroyed ) {
            self.media.addEventListener( "timeupdate", self.data.timeUpdate, false );
          }
        }
      };

      Object.defineProperty( this, "error", {
        get: function() {

          return self.media.error;
        }
      });

      if ( self.media.readyState >= 2 ) {

        isReady();
      } else {

        self.media.addEventListener( "loadeddata", isReady, false );
      }

      return this;
    }
  };

  //  Extend constructor prototype to instance prototype
  //  Allows chaining methods to instances
  Popcorn.p.init.prototype = Popcorn.p;

  Popcorn.byId = function( str ) {
    var instances = Popcorn.instances,
        length = instances.length,
        i = 0;

    for ( ; i < length; i++ ) {
      if ( instances[ i ].id === str ) {
        return instances[ i ];
      }
    }

    return null;
  };

  Popcorn.forEach = function( obj, fn, context ) {

    if ( !obj || !fn ) {
      return {};
    }

    context = context || this;

    var key, len;

    // Use native whenever possible
    if ( forEach && obj.forEach === forEach ) {
      return obj.forEach( fn, context );
    }

    if ( toString.call( obj ) === "[object NodeList]" ) {
      for ( key = 0, len = obj.length; key < len; key++ ) {
        fn.call( context, obj[ key ], key, obj );
      }
      return obj;
    }

    for ( key in obj ) {
      if ( hasOwn.call( obj, key ) ) {
        fn.call( context, obj[ key ], key, obj );
      }
    }
    return obj;
  };

  Popcorn.extend = function( obj ) {
    var dest = obj, src = slice.call( arguments, 1 );

    Popcorn.forEach( src, function( copy ) {
      for ( var prop in copy ) {
        dest[ prop ] = copy[ prop ];
      }
    });

    return dest;
  };


  // A Few reusable utils, memoized onto Popcorn
  Popcorn.extend( Popcorn, {
    noConflict: function( deep ) {

      if ( deep ) {
        global.Popcorn = _Popcorn;
      }

      return Popcorn;
    },
    error: function( msg ) {
      throw new Error( msg );
    },
    guid: function( prefix ) {
      Popcorn.guid.counter++;
      return  ( prefix ? prefix : "" ) + ( +new Date() + Popcorn.guid.counter );
    },
    sizeOf: function( obj ) {
      var size = 0;

      for ( var prop in obj ) {
        size++;
      }

      return size;
    },
    isArray: Array.isArray || function( array ) {
      return toString.call( array ) === "[object Array]";
    },

    nop: function() {},

    position: function( elem ) {

      var clientRect = elem.getBoundingClientRect(),
          bounds = {},
          doc = elem.ownerDocument,
          docElem = document.documentElement,
          body = document.body,
          clientTop, clientLeft, scrollTop, scrollLeft, top, left;

      //  Determine correct clientTop/Left
      clientTop = docElem.clientTop || body.clientTop || 0;
      clientLeft = docElem.clientLeft || body.clientLeft || 0;

      //  Determine correct scrollTop/Left
      scrollTop = ( global.pageYOffset && docElem.scrollTop || body.scrollTop );
      scrollLeft = ( global.pageXOffset && docElem.scrollLeft || body.scrollLeft );

      //  Temp top/left
      top = Math.ceil( clientRect.top + scrollTop - clientTop );
      left = Math.ceil( clientRect.left + scrollLeft - clientLeft );

      for ( var p in clientRect ) {
        bounds[ p ] = Math.round( clientRect[ p ] );
      }

      return Popcorn.extend({}, bounds, { top: top, left: left });
    },

    disable: function( instance, plugin ) {

      if ( !instance.data.disabled[ plugin ] ) {

        instance.data.disabled[ plugin ] = true;

        for ( var i = instance.data.running[ plugin ].length - 1, event; i >= 0; i-- ) {

          event = instance.data.running[ plugin ][ i ];
          event._natives.end.call( instance, null, event  );
        }
      }

      return instance;
    },
    enable: function( instance, plugin ) {

      if ( instance.data.disabled[ plugin ] ) {

        instance.data.disabled[ plugin ] = false;

        for ( var i = instance.data.running[ plugin ].length - 1, event; i >= 0; i-- ) {

          event = instance.data.running[ plugin ][ i ];
          event._natives.start.call( instance, null, event  );
        }
      }

      return instance;
    },
    destroy: function( instance ) {
      var events = instance.data.events,
          trackEvents = instance.data.trackEvents,
          singleEvent, item, fn, plugin;

      //  Iterate through all events and remove them
      for ( item in events ) {
        singleEvent = events[ item ];
        for ( fn in singleEvent ) {
          delete singleEvent[ fn ];
        }
        events[ item ] = null;
      }

      // remove all plugins off the given instance
      for ( plugin in Popcorn.registryByName ) {
        Popcorn.removePlugin( instance, plugin );
      }

      // Remove all data.trackEvents #1178
      trackEvents.byStart.length = 0;
      trackEvents.byEnd.length = 0;

      if ( !instance.isDestroyed ) {
        instance.data.timeUpdate && instance.media.removeEventListener( "timeupdate", instance.data.timeUpdate, false );
        instance.isDestroyed = true;
      }
    }
  });

  //  Memoized GUID Counter
  Popcorn.guid.counter = 1;

  //  Factory to implement getters, setters and controllers
  //  as Popcorn instance methods. The IIFE will create and return
  //  an object with defined methods
  Popcorn.extend(Popcorn.p, (function() {

      var methods = "load play pause currentTime playbackRate volume duration preload playbackRate " +
                    "autoplay loop controls muted buffered readyState seeking paused played seekable ended",
          ret = {};


      //  Build methods, store in object that is returned and passed to extend
      Popcorn.forEach( methods.split( /\s+/g ), function( name ) {

        ret[ name ] = function( arg ) {
          var previous;

          if ( typeof this.media[ name ] === "function" ) {

            // Support for shorthanded play(n)/pause(n) jump to currentTime
            // If arg is not null or undefined and called by one of the
            // allowed shorthandable methods, then set the currentTime
            // Supports time as seconds or SMPTE
            if ( arg != null && /play|pause/.test( name ) ) {
              this.media.currentTime = Popcorn.util.toSeconds( arg );
            }

            this.media[ name ]();

            return this;
          }

          if ( arg != null ) {
            // Capture the current value of the attribute property
            previous = this.media[ name ];

            // Set the attribute property with the new value
            this.media[ name ] = arg;

            // If the new value is not the same as the old value
            // emit an "attrchanged event"
            if ( previous !== arg ) {
              this.emit( "attrchange", {
                attribute: name,
                previousValue: previous,
                currentValue: arg
              });
            }
            return this;
          }

          return this.media[ name ];
        };
      });

      return ret;

    })()
  );

  Popcorn.forEach( "enable disable".split(" "), function( method ) {
    Popcorn.p[ method ] = function( plugin ) {
      return Popcorn[ method ]( this, plugin );
    };
  });

  Popcorn.extend(Popcorn.p, {

    //  Rounded currentTime
    roundTime: function() {
      return Math.round( this.media.currentTime );
    },

    //  Attach an event to a single point in time
    exec: function( id, time, fn ) {
      var length = arguments.length,
          trackEvent, sec;

      // Check if first could possibly be a SMPTE string
      // p.cue( "smpte string", fn );
      // try/catch avoid awful throw in Popcorn.util.toSeconds
      // TODO: Get rid of that, replace with NaN return?
      try {
        sec = Popcorn.util.toSeconds( id );
      } catch ( e ) {}

      // If it can be converted into a number then
      // it's safe to assume that the string was SMPTE
      if ( typeof sec === "number" ) {
        id = sec;
      }

      // Shift arguments based on use case
      //
      // Back compat for:
      // p.cue( time, fn );
      if ( typeof id === "number" && length === 2 ) {
        fn = time;
        time = id;
        id = Popcorn.guid( "cue" );
      } else {
        // Support for new forms

        // p.cue( "empty-cue" );
        if ( length === 1 ) {
          // Set a time for an empty cue. It's not important what
          // the time actually is, because the cue is a no-op
          time = -1;

        } else {

          // Get the trackEvent that matches the given id.
          trackEvent = this.getTrackEvent( id );

          if ( trackEvent ) {

            // p.cue( "my-id", 12 );
            // p.cue( "my-id", function() { ... });
            if ( typeof id === "string" && length === 2 ) {

              // p.cue( "my-id", 12 );
              // The path will update the cue time.
              if ( typeof time === "number" ) {
                // Re-use existing trackEvent start callback
                fn = trackEvent._natives.start;
              }

              // p.cue( "my-id", function() { ... });
              // The path will update the cue function
              if ( typeof time === "function" ) {
                fn = time;
                // Re-use existing trackEvent start time
                time = trackEvent.start;
              }
            }
          } else {

            if ( length >= 2 ) {

              // p.cue( "a", "00:00:00");
              if ( typeof time === "string" ) {
                try {
                  sec = Popcorn.util.toSeconds( time );
                } catch ( e ) {}

                time = sec;
              }

              // p.cue( "b", 11 );
              // p.cue( "b", 11, function() {} );
              if ( typeof time === "number" ) {
                fn = fn || Popcorn.nop();
              }

              // p.cue( "c", function() {});
              if ( typeof time === "function" ) {
                fn = time;
                time = -1;
              }
            }
          }
        }
      }

      //  Creating a one second track event with an empty end
      //  Or update an existing track event with new values
      Popcorn.addTrackEvent( this, {
        id: id,
        start: time,
        end: time + 1,
        _running: false,
        _natives: {
          start: fn || Popcorn.nop,
          end: Popcorn.nop,
          type: "cue"
        }
      });

      return this;
    },

    // Mute the calling media, optionally toggle
    mute: function( toggle ) {

      var event = toggle == null || toggle === true ? "muted" : "unmuted";

      // If `toggle` is explicitly `false`,
      // unmute the media and restore the volume level
      if ( event === "unmuted" ) {
        this.media.muted = false;
        this.media.volume = this.data.state.volume;
      }

      // If `toggle` is either null or undefined,
      // save the current volume and mute the media element
      if ( event === "muted" ) {
        this.data.state.volume = this.media.volume;
        this.media.muted = true;
      }

      // Trigger either muted|unmuted event
      this.emit( event );

      return this;
    },

    // Convenience method, unmute the calling media
    unmute: function( toggle ) {

      return this.mute( toggle == null ? false : !toggle );
    },

    // Get the client bounding box of an instance element
    position: function() {
      return Popcorn.position( this.media );
    },

    // Toggle a plugin's playback behaviour (on or off) per instance
    toggle: function( plugin ) {
      return Popcorn[ this.data.disabled[ plugin ] ? "enable" : "disable" ]( this, plugin );
    },

    // Set default values for plugin options objects per instance
    defaults: function( plugin, defaults ) {

      // If an array of default configurations is provided,
      // iterate and apply each to this instance
      if ( Popcorn.isArray( plugin ) ) {

        Popcorn.forEach( plugin, function( obj ) {
          for ( var name in obj ) {
            this.defaults( name, obj[ name ] );
          }
        }, this );

        return this;
      }

      if ( !this.options.defaults ) {
        this.options.defaults = {};
      }

      if ( !this.options.defaults[ plugin ] ) {
        this.options.defaults[ plugin ] = {};
      }

      Popcorn.extend( this.options.defaults[ plugin ], defaults );

      return this;
    }
  });

  Popcorn.Events  = {
    UIEvents: "blur focus focusin focusout load resize scroll unload",
    MouseEvents: "mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave click dblclick",
    Events: "loadstart progress suspend emptied stalled play pause error " +
            "loadedmetadata loadeddata waiting playing canplay canplaythrough " +
            "seeking seeked timeupdate ended ratechange durationchange volumechange"
  };

  Popcorn.Events.Natives = Popcorn.Events.UIEvents + " " +
                           Popcorn.Events.MouseEvents + " " +
                           Popcorn.Events.Events;

  internal.events.apiTypes = [ "UIEvents", "MouseEvents", "Events" ];

  // Privately compile events table at load time
  (function( events, data ) {

    var apis = internal.events.apiTypes,
    eventsList = events.Natives.split( /\s+/g ),
    idx = 0, len = eventsList.length, prop;

    for( ; idx < len; idx++ ) {
      data.hash[ eventsList[idx] ] = true;
    }

    apis.forEach(function( val, idx ) {

      data.apis[ val ] = {};

      var apiEvents = events[ val ].split( /\s+/g ),
      len = apiEvents.length,
      k = 0;

      for ( ; k < len; k++ ) {
        data.apis[ val ][ apiEvents[ k ] ] = true;
      }
    });
  })( Popcorn.Events, internal.events );

  Popcorn.events = {

    isNative: function( type ) {
      return !!internal.events.hash[ type ];
    },
    getInterface: function( type ) {

      if ( !Popcorn.events.isNative( type ) ) {
        return false;
      }

      var eventApi = internal.events,
        apis = eventApi.apiTypes,
        apihash = eventApi.apis,
        idx = 0, len = apis.length, api, tmp;

      for ( ; idx < len; idx++ ) {
        tmp = apis[ idx ];

        if ( apihash[ tmp ][ type ] ) {
          api = tmp;
          break;
        }
      }
      return api;
    },
    //  Compile all native events to single array
    all: Popcorn.Events.Natives.split( /\s+/g ),
    //  Defines all Event handling static functions
    fn: {
      trigger: function( type, data ) {

        var eventInterface, evt;
        //  setup checks for custom event system
        if ( this.data.events[ type ] && Popcorn.sizeOf( this.data.events[ type ] ) ) {

          eventInterface  = Popcorn.events.getInterface( type );

          if ( eventInterface ) {

            evt = document.createEvent( eventInterface );
            evt.initEvent( type, true, true, global, 1 );

            this.media.dispatchEvent( evt );

            return this;
          }

          //  Custom events
          Popcorn.forEach( this.data.events[ type ], function( obj, key ) {

            obj.call( this, data );

          }, this );

        }

        return this;
      },
      listen: function( type, fn ) {

        var self = this,
            hasEvents = true,
            eventHook = Popcorn.events.hooks[ type ],
            origType = type,
            tmp;

        if ( !this.data.events[ type ] ) {
          this.data.events[ type ] = {};
          hasEvents = false;
        }

        // Check and setup event hooks
        if ( eventHook ) {

          // Execute hook add method if defined
          if ( eventHook.add ) {
            eventHook.add.call( this, {}, fn );
          }

          // Reassign event type to our piggyback event type if defined
          if ( eventHook.bind ) {
            type = eventHook.bind;
          }

          // Reassign handler if defined
          if ( eventHook.handler ) {
            tmp = fn;

            fn = function wrapper( event ) {
              eventHook.handler.call( self, event, tmp );
            };
          }

          // assume the piggy back event is registered
          hasEvents = true;

          // Setup event registry entry
          if ( !this.data.events[ type ] ) {
            this.data.events[ type ] = {};
            // Toggle if the previous assumption was untrue
            hasEvents = false;
          }
        }

        //  Register event and handler
        this.data.events[ type ][ fn.name || ( fn.toString() + Popcorn.guid() ) ] = fn;

        // only attach one event of any type
        if ( !hasEvents && Popcorn.events.all.indexOf( type ) > -1 ) {

          this.media.addEventListener( type, function( event ) {

            Popcorn.forEach( self.data.events[ type ], function( obj, key ) {
              if ( typeof obj === "function" ) {
                obj.call( self, event );
              }
            });

          }, false);
        }
        return this;
      },
      unlisten: function( type, fn ) {

        if ( this.data.events[ type ] && this.data.events[ type ][ fn ] ) {

          delete this.data.events[ type ][ fn ];

          return this;
        }

        this.data.events[ type ] = null;

        return this;
      }
    },
    hooks: {
      canplayall: {
        bind: "canplaythrough",
        add: function( event, callback ) {

          var state = false;

          if ( this.media.readyState ) {

            callback.call( this, event );

            state = true;
          }

          this.data.hooks.canplayall = {
            fired: state
          };
        },
        // declare special handling instructions
        handler: function canplayall( event, callback ) {

          if ( !this.data.hooks.canplayall.fired ) {
            // trigger original user callback once
            callback.call( this, event );

            this.data.hooks.canplayall.fired = true;
          }
        }
      }
    }
  };

  //  Extend Popcorn.events.fns (listen, unlisten, trigger) to all Popcorn instances
  //  Extend aliases (on, off, emit)
  Popcorn.forEach( [ [ "trigger", "emit" ], [ "listen", "on" ], [ "unlisten", "off" ] ], function( key ) {
    Popcorn.p[ key[ 0 ] ] = Popcorn.p[ key[ 1 ] ] = Popcorn.events.fn[ key[ 0 ] ];
  });

  // Internal Only - Adds track events to the instance object
  Popcorn.addTrackEvent = function( obj, track ) {
    var trackEvent, isUpdate, eventType;

    // Do a lookup for existing trackevents with this id
    if ( track.id ) {
      trackEvent = obj.getTrackEvent( track.id );
    }

    // If a track event by this id currently exists, modify it
    if ( trackEvent ) {
      isUpdate = true;
      // Create a new object with the existing trackEvent
      // Extend with new track properties
      track = Popcorn.extend( {}, trackEvent, track );

      // Remove the existing track from the instance
      obj.removeTrackEvent( track.id );
    }

    // Determine if this track has default options set for it
    // If so, apply them to the track object
    if ( track && track._natives && track._natives.type &&
        ( obj.options.defaults && obj.options.defaults[ track._natives.type ] ) ) {

      track = Popcorn.extend( {}, obj.options.defaults[ track._natives.type ], track );
    }

    if ( track._natives ) {
      //  Supports user defined track event id
      track._id = track.id || track._id || Popcorn.guid( track._natives.type );

      //  Push track event ids into the history
      obj.data.history.push( track._id );
    }

    track.start = Popcorn.util.toSeconds( track.start, obj.options.framerate );
    track.end   = Popcorn.util.toSeconds( track.end, obj.options.framerate );

    //  Store this definition in an array sorted by times
    var byStart = obj.data.trackEvents.byStart,
        byEnd = obj.data.trackEvents.byEnd,
        startIndex, endIndex;

    for ( startIndex = byStart.length - 1; startIndex >= 0; startIndex-- ) {

      if ( track.start >= byStart[ startIndex ].start ) {
        byStart.splice( startIndex + 1, 0, track );
        break;
      }
    }

    for ( endIndex = byEnd.length - 1; endIndex >= 0; endIndex-- ) {

      if ( track.end > byEnd[ endIndex ].end ) {
        byEnd.splice( endIndex + 1, 0, track );
        break;
      }
    }

    // Display track event immediately if it's enabled and current
    if ( track.end > obj.media.currentTime &&
        track.start <= obj.media.currentTime ) {

      track._running = true;
      obj.data.running[ track._natives.type ].push( track );

      if ( !obj.data.disabled[ track._natives.type ] ) {

        track._natives.start.call( obj, null, track );
      }
    }

    // update startIndex and endIndex
    if ( startIndex <= obj.data.trackEvents.startIndex &&
      track.start <= obj.data.trackEvents.previousUpdateTime ) {

      obj.data.trackEvents.startIndex++;
    }

    if ( endIndex <= obj.data.trackEvents.endIndex &&
      track.end < obj.data.trackEvents.previousUpdateTime ) {

      obj.data.trackEvents.endIndex++;
    }

    this.timeUpdate( obj, null, true );

    // Store references to user added trackevents in ref table
    if ( track._id ) {
      Popcorn.addTrackEvent.ref( obj, track );
    }

    // If the call to addTrackEvent was an update/modify call, fire an event
    if ( isUpdate ) {

      // Determine appropriate event type to trigger
      // they are identical in function, but the naming
      // adds some level of intuition for the end developer
      // to rely on
      if ( track._natives.type === "cue" ) {
        eventType = "cuechange";
      } else {
        eventType = "trackchange";
      }

      // Fire an event with change information
      obj.emit( eventType, {
        id: track.id,
        previousValue: {
          time: trackEvent.start,
          fn: trackEvent._natives.start
        },
        currentValue: {
          time: track.start,
          fn: track._natives.start
        }
      });
    } else if ( track._natives ) {

      // Fire a trackadded event
      obj.emit( "trackadded", Popcorn.extend({}, track, {
        plugin: track._natives.type,
        type: "trackadded"
      }));
    }
  };

  // Internal Only - Adds track event references to the instance object's trackRefs hash table
  Popcorn.addTrackEvent.ref = function( obj, track ) {
    obj.data.trackRefs[ track._id ] = track;

    return obj;
  };

  Popcorn.removeTrackEvent  = function( obj, removeId ) {

    var start, end, animate,
        historyLen = obj.data.history.length,
        length = obj.data.trackEvents.byStart.length,
        index = 0,
        indexWasAt = 0,
        byStart = [],
        byEnd = [],
        animating = [],
        history = [],
        track;

    while ( --length > -1 ) {
      start = obj.data.trackEvents.byStart[ index ];
      end = obj.data.trackEvents.byEnd[ index ];

      // Padding events will not have _id properties.
      // These should be safely pushed onto the front and back of the
      // track event array
      if ( !start._id ) {
        byStart.push( start );
        byEnd.push( end );
      }

      // Filter for user track events (vs system track events)
      if ( start._id ) {

        // If not a matching start event for removal
        if ( start._id !== removeId ) {
          byStart.push( start );
        }

        // If not a matching end event for removal
        if ( end._id !== removeId ) {
          byEnd.push( end );
        }

        // If the _id is matched, capture the current index
        if ( start._id === removeId ) {
          indexWasAt = index;

          // cache the track event being removed
          track = start;

          // If a _teardown function was defined,
          // enforce for track event removals
          if ( start._natives._teardown ) {
            start._natives._teardown.call( obj, start );
          }
        }
      }
      // Increment the track index
      index++;
    }

    // Reset length to be used by the condition below to determine
    // if animating track events should also be filtered for removal.
    // Reset index below to be used by the reverse while as an
    // incrementing counter
    length = obj.data.trackEvents.animating.length;
    index = 0;

    if ( length ) {
      while ( --length > -1 ) {
        animate = obj.data.trackEvents.animating[ index ];

        // Padding events will not have _id properties.
        // These should be safely pushed onto the front and back of the
        // track event array
        if ( !animate._id ) {
          animating.push( animate );
        }

        // If not a matching animate event for removal
        if ( animate._id && animate._id !== removeId ) {
          animating.push( animate );
        }
        // Increment the track index
        index++;
      }
    }

    //  Update
    if ( indexWasAt <= obj.data.trackEvents.startIndex ) {
      obj.data.trackEvents.startIndex--;
    }

    if ( indexWasAt <= obj.data.trackEvents.endIndex ) {
      obj.data.trackEvents.endIndex--;
    }

    obj.data.trackEvents.byStart = byStart;
    obj.data.trackEvents.byEnd = byEnd;
    obj.data.trackEvents.animating = animating;

    for ( var i = 0; i < historyLen; i++ ) {
      if ( obj.data.history[ i ] !== removeId ) {
        history.push( obj.data.history[ i ] );
      }
    }

    // Update ordered history array
    obj.data.history = history;

    // Update track event references
    Popcorn.removeTrackEvent.ref( obj, removeId );

    if ( track && track._natives ) {

      // Fire a trackremoved event
      obj.emit( "trackremoved", Popcorn.extend({}, track, {
        plugin: track._natives.type,
        type: "trackremoved"
      }));
    }
  };

  // Internal Only - Removes track event references from instance object's trackRefs hash table
  Popcorn.removeTrackEvent.ref = function( obj, removeId ) {
    delete obj.data.trackRefs[ removeId ];

    return obj;
  };

  // Return an array of track events bound to this instance object
  Popcorn.getTrackEvents = function( obj ) {

    var trackevents = [],
      refs = obj.data.trackEvents.byStart,
      length = refs.length,
      idx = 0,
      ref;

    for ( ; idx < length; idx++ ) {
      ref = refs[ idx ];
      // Return only user attributed track event references
      if ( ref._id ) {
        trackevents.push( ref );
      }
    }

    return trackevents;
  };

  // Internal Only - Returns an instance object's trackRefs hash table
  Popcorn.getTrackEvents.ref = function( obj ) {
    return obj.data.trackRefs;
  };

  // Return a single track event bound to this instance object
  Popcorn.getTrackEvent = function( obj, trackId ) {
    return obj.data.trackRefs[ trackId ];
  };

  // Internal Only - Returns an instance object's track reference by track id
  Popcorn.getTrackEvent.ref = function( obj, trackId ) {
    return obj.data.trackRefs[ trackId ];
  };

  Popcorn.getLastTrackEventId = function( obj ) {
    return obj.data.history[ obj.data.history.length - 1 ];
  };

  Popcorn.timeUpdate = function( obj, event ) {

    var currentTime = obj.media.currentTime,
        previousTime = obj.data.trackEvents.previousUpdateTime,
        tracks = obj.data.trackEvents,
        end = tracks.endIndex,
        start = tracks.startIndex,
        byStartLen = tracks.byStart.length,
        byEndLen = tracks.byEnd.length,
        registryByName = Popcorn.registryByName,
        trackstart = "trackstart",
        trackend = "trackend",

        byEnd, byStart, byAnimate, natives, type, runningPlugins;

    //  Playbar advancing
    if ( previousTime <= currentTime ) {

      while ( tracks.byEnd[ end ] && tracks.byEnd[ end ].end <= currentTime ) {

        byEnd = tracks.byEnd[ end ];
        natives = byEnd._natives;
        type = natives && natives.type;

        //  If plugin does not exist on this instance, remove it
        if ( !natives ||
            ( !!registryByName[ type ] ||
              !!obj[ type ] ) ) {

          if ( byEnd._running === true ) {

            byEnd._running = false;
            runningPlugins = obj.data.running[ type ];
            runningPlugins.splice( runningPlugins.indexOf( byEnd ), 1 );

            if ( !obj.data.disabled[ type ] ) {

              natives.end.call( obj, event, byEnd );

              obj.emit( trackend,
                Popcorn.extend({}, byEnd, {
                  plugin: type,
                  type: trackend
                })
              );
            }
          }

          end++;
        } else {
          // remove track event
          Popcorn.removeTrackEvent( obj, byEnd._id );
          return;
        }
      }

      while ( tracks.byStart[ start ] && tracks.byStart[ start ].start <= currentTime ) {

        byStart = tracks.byStart[ start ];
        natives = byStart._natives;
        type = natives && natives.type;

        //  If plugin does not exist on this instance, remove it
        if ( !natives ||
            ( !!registryByName[ type ] ||
              !!obj[ type ] ) ) {

          if ( byStart.end > currentTime &&
                byStart._running === false ) {

            byStart._running = true;
            obj.data.running[ type ].push( byStart );

            if ( !obj.data.disabled[ type ] ) {

              natives.start.call( obj, event, byStart );

              obj.emit( trackstart,
                Popcorn.extend({}, byStart, {
                  plugin: type,
                  type: trackstart
                })
              );
            }
          }
          start++;
        } else {
          // remove track event
          Popcorn.removeTrackEvent( obj, byStart._id );
          return;
        }
      }

    // Playbar receding
    } else if ( previousTime > currentTime ) {

      while ( tracks.byStart[ start ] && tracks.byStart[ start ].start > currentTime ) {

        byStart = tracks.byStart[ start ];
        natives = byStart._natives;
        type = natives && natives.type;

        // if plugin does not exist on this instance, remove it
        if ( !natives ||
            ( !!registryByName[ type ] ||
              !!obj[ type ] ) ) {

          if ( byStart._running === true ) {

            byStart._running = false;
            runningPlugins = obj.data.running[ type ];
            runningPlugins.splice( runningPlugins.indexOf( byStart ), 1 );

            if ( !obj.data.disabled[ type ] ) {

              natives.end.call( obj, event, byStart );

              obj.emit( trackend,
                Popcorn.extend({}, byStart, {
                  plugin: type,
                  type: trackend
                })
              );
            }
          }
          start--;
        } else {
          // remove track event
          Popcorn.removeTrackEvent( obj, byStart._id );
          return;
        }
      }

      while ( tracks.byEnd[ end ] && tracks.byEnd[ end ].end > currentTime ) {

        byEnd = tracks.byEnd[ end ];
        natives = byEnd._natives;
        type = natives && natives.type;

        // if plugin does not exist on this instance, remove it
        if ( !natives ||
            ( !!registryByName[ type ] ||
              !!obj[ type ] ) ) {

          if ( byEnd.start <= currentTime &&
                byEnd._running === false ) {

            byEnd._running = true;
            obj.data.running[ type ].push( byEnd );

            if ( !obj.data.disabled[ type ] ) {

              natives.start.call( obj, event, byEnd );

              obj.emit( trackstart,
                Popcorn.extend({}, byEnd, {
                  plugin: type,
                  type: trackstart
                })
              );
            }
          }
          end--;
        } else {
          // remove track event
          Popcorn.removeTrackEvent( obj, byEnd._id );
          return;
        }
      }
    }

    tracks.endIndex = end;
    tracks.startIndex = start;
    tracks.previousUpdateTime = currentTime;

    //enforce index integrity if trackRemoved
    tracks.byStart.length < byStartLen && tracks.startIndex--;
    tracks.byEnd.length < byEndLen && tracks.endIndex--;

  };

  //  Map and Extend TrackEvent functions to all Popcorn instances
  Popcorn.extend( Popcorn.p, {

    getTrackEvents: function() {
      return Popcorn.getTrackEvents.call( null, this );
    },

    getTrackEvent: function( id ) {
      return Popcorn.getTrackEvent.call( null, this, id );
    },

    getLastTrackEventId: function() {
      return Popcorn.getLastTrackEventId.call( null, this );
    },

    removeTrackEvent: function( id ) {

      Popcorn.removeTrackEvent.call( null, this, id );
      return this;
    },

    removePlugin: function( name ) {
      Popcorn.removePlugin.call( null, this, name );
      return this;
    },

    timeUpdate: function( event ) {
      Popcorn.timeUpdate.call( null, this, event );
      return this;
    },

    destroy: function() {
      Popcorn.destroy.call( null, this );
      return this;
    }
  });

  //  Plugin manifests
  Popcorn.manifest = {};
  //  Plugins are registered
  Popcorn.registry = [];
  Popcorn.registryByName = {};
  //  An interface for extending Popcorn
  //  with plugin functionality
  Popcorn.plugin = function( name, definition, manifest ) {

    if ( Popcorn.protect.natives.indexOf( name.toLowerCase() ) >= 0 ) {
      Popcorn.error( "'" + name + "' is a protected function name" );
      return;
    }

    //  Provides some sugar, but ultimately extends
    //  the definition into Popcorn.p
    var reserved = [ "start", "end" ],
        plugin = {},
        setup,
        isfn = typeof definition === "function",
        methods = [ "_setup", "_teardown", "start", "end", "frame" ];

    // combines calls of two function calls into one
    var combineFn = function( first, second ) {

      first = first || Popcorn.nop;
      second = second || Popcorn.nop;

      return function() {
        first.apply( this, arguments );
        second.apply( this, arguments );
      };
    };

    //  If `manifest` arg is undefined, check for manifest within the `definition` object
    //  If no `definition.manifest`, an empty object is a sufficient fallback
    Popcorn.manifest[ name ] = manifest = manifest || definition.manifest || {};

    // apply safe, and empty default functions
    methods.forEach(function( method ) {
      definition[ method ] = safeTry( definition[ method ] || Popcorn.nop, name );
    });

    var pluginFn = function( setup, options ) {

      if ( !options ) {
        return this;
      }

      // When the "ranges" property is set and its value is an array, short-circuit
      // the pluginFn definition to recall itself with an options object generated from
      // each range object in the ranges array. (eg. { start: 15, end: 16 } )
      if ( options.ranges && Popcorn.isArray(options.ranges) ) {
        Popcorn.forEach( options.ranges, function( range ) {
          // Create a fresh object, extend with current options
          // and start/end range object's properties
          // Works with in/out as well.
          var opts = Popcorn.extend( {}, options, range );

          // Remove the ranges property to prevent infinitely
          // entering this condition
          delete opts.ranges;

          // Call the plugin with the newly created opts object
          this[ name ]( opts );
        }, this);

        // Return the Popcorn instance to avoid creating an empty track event
        return this;
      }

      //  Storing the plugin natives
      var natives = options._natives = {},
          compose = "",
          originalOpts, manifestOpts;

      Popcorn.extend( natives, setup );

      options._natives.type = name;
      options._running = false;

      natives.start = natives.start || natives[ "in" ];
      natives.end = natives.end || natives[ "out" ];

      if ( options.once ) {
        natives.end = combineFn( natives.end, function() {
          this.removeTrackEvent( options._id );
        });
      }

      // extend teardown to always call end if running
      natives._teardown = combineFn(function() {

        var args = slice.call( arguments ),
            runningPlugins = this.data.running[ natives.type ];

        // end function signature is not the same as teardown,
        // put null on the front of arguments for the event parameter
        args.unshift( null );

        // only call end if event is running
        args[ 1 ]._running &&
          runningPlugins.splice( runningPlugins.indexOf( options ), 1 ) &&
          natives.end.apply( this, args );
      }, natives._teardown );

      // default to an empty string if no effect exists
      // split string into an array of effects
      options.compose = options.compose && options.compose.split( " " ) || [];
      options.effect = options.effect && options.effect.split( " " ) || [];

      // join the two arrays together
      options.compose = options.compose.concat( options.effect );

      options.compose.forEach(function( composeOption ) {

        // if the requested compose is garbage, throw it away
        compose = Popcorn.compositions[ composeOption ] || {};

        // extends previous functions with compose function
        methods.forEach(function( method ) {
          natives[ method ] = combineFn( natives[ method ], compose[ method ] );
        });
      });

      //  Ensure a manifest object, an empty object is a sufficient fallback
      options._natives.manifest = manifest;

      //  Checks for expected properties
      if ( !( "start" in options ) ) {
        options.start = options[ "in" ] || 0;
      }

      if ( !options.end && options.end !== 0 ) {
        options.end = options[ "out" ] || Number.MAX_VALUE;
      }

      // Use hasOwn to detect non-inherited toString, since all
      // objects will receive a toString - its otherwise undetectable
      if ( !hasOwn.call( options, "toString" ) ) {
        options.toString = function() {
          var props = [
            "start: " + options.start,
            "end: " + options.end,
            "id: " + (options.id || options._id)
          ];

          // Matches null and undefined, allows: false, 0, "" and truthy
          if ( options.target != null ) {
            props.push( "target: " + options.target );
          }

          return name + " ( " + props.join(", ") + " )";
        };
      }

      // Resolves 239, 241, 242
      if ( !options.target ) {

        //  Sometimes the manifest may be missing entirely
        //  or it has an options object that doesn't have a `target` property
        manifestOpts = "options" in manifest && manifest.options;

        options.target = manifestOpts && "target" in manifestOpts && manifestOpts.target;
      }

      if ( options._natives ) {
        // ensure an initial id is there before setup is called
        options._id = Popcorn.guid( options._natives.type );
      }

      // Trigger _setup method if exists
      options._natives._setup && options._natives._setup.call( this, options );

      // Create new track event for this instance
      Popcorn.addTrackEvent( this, options );

      //  Future support for plugin event definitions
      //  for all of the native events
      Popcorn.forEach( setup, function( callback, type ) {

        if ( type !== "type" ) {

          if ( reserved.indexOf( type ) === -1 ) {

            this.on( type, callback );
          }
        }

      }, this );

      return this;
    };

    //  Extend Popcorn.p with new named definition
    //  Assign new named definition
    Popcorn.p[ name ] = plugin[ name ] = function( id, options ) {
      var length = arguments.length,
          trackEvent, defaults, mergedSetupOpts;

      // Shift arguments based on use case
      //
      // Back compat for:
      // p.plugin( options );
      if ( id && !options ) {
        options = id;
        id = null;
      } else {

        // Get the trackEvent that matches the given id.
        trackEvent = this.getTrackEvent( id );

        // If the track event does not exist, ensure that the options
        // object has a proper id
        if ( !trackEvent ) {
          options.id = id;

        // If the track event does exist, merge the updated properties
        } else {

          options = Popcorn.extend( {}, trackEvent, options );

          Popcorn.addTrackEvent( this, options );

          return this;
        }
      }

      this.data.running[ name ] = this.data.running[ name ] || [];

      // Merge with defaults if they exist, make sure per call is prioritized
      defaults = ( this.options.defaults && this.options.defaults[ name ] ) || {};
      mergedSetupOpts = Popcorn.extend( {}, defaults, options );

      return pluginFn.call( this, isfn ? definition.call( this, mergedSetupOpts ) : definition,
                                  mergedSetupOpts );
    };

    // if the manifest parameter exists we should extend it onto the definition object
    // so that it shows up when calling Popcorn.registry and Popcorn.registryByName
    if ( manifest ) {
      Popcorn.extend( definition, {
        manifest: manifest
      });
    }

    //  Push into the registry
    var entry = {
      fn: plugin[ name ],
      definition: definition,
      base: definition,
      parents: [],
      name: name
    };
    Popcorn.registry.push(
       Popcorn.extend( plugin, entry, {
        type: name
      })
    );
    Popcorn.registryByName[ name ] = entry;

    return plugin;
  };

  // Storage for plugin function errors
  Popcorn.plugin.errors = [];

  // Returns wrapped plugin function
  function safeTry( fn, pluginName ) {
    return function() {

      //  When Popcorn.plugin.debug is true, do not suppress errors
      if ( Popcorn.plugin.debug ) {
        return fn.apply( this, arguments );
      }

      try {
        return fn.apply( this, arguments );
      } catch ( ex ) {

        // Push plugin function errors into logging queue
        Popcorn.plugin.errors.push({
          plugin: pluginName,
          thrown: ex,
          source: fn.toString()
        });

        // Trigger an error that the instance can listen for
        // and react to
        this.emit( "pluginerror", Popcorn.plugin.errors );
      }
    };
  }

  // Debug-mode flag for plugin development
  // True for Popcorn development versions, false for stable/tagged versions
  Popcorn.plugin.debug = ( Popcorn.version === "@" + "VERSION" );

  //  removePlugin( type ) removes all tracks of that from all instances of popcorn
  //  removePlugin( obj, type ) removes all tracks of type from obj, where obj is a single instance of popcorn
  Popcorn.removePlugin = function( obj, name ) {

    //  Check if we are removing plugin from an instance or from all of Popcorn
    if ( !name ) {

      //  Fix the order
      name = obj;
      obj = Popcorn.p;

      if ( Popcorn.protect.natives.indexOf( name.toLowerCase() ) >= 0 ) {
        Popcorn.error( "'" + name + "' is a protected function name" );
        return;
      }

      var registryLen = Popcorn.registry.length,
          registryIdx;

      // remove plugin reference from registry
      for ( registryIdx = 0; registryIdx < registryLen; registryIdx++ ) {
        if ( Popcorn.registry[ registryIdx ].name === name ) {
          Popcorn.registry.splice( registryIdx, 1 );
          delete Popcorn.registryByName[ name ];
          delete Popcorn.manifest[ name ];

          // delete the plugin
          delete obj[ name ];

          // plugin found and removed, stop checking, we are done
          return;
        }
      }

    }

    var byStart = obj.data.trackEvents.byStart,
        byEnd = obj.data.trackEvents.byEnd,
        animating = obj.data.trackEvents.animating,
        idx, sl;

    // remove all trackEvents
    for ( idx = 0, sl = byStart.length; idx < sl; idx++ ) {

      if ( byStart[ idx ] && byStart[ idx ]._natives && byStart[ idx ]._natives.type === name ) {

        byStart[ idx ]._natives._teardown && byStart[ idx ]._natives._teardown.call( obj, byStart[ idx ] );

        byStart.splice( idx, 1 );

        // update for loop if something removed, but keep checking
        idx--; sl--;
        if ( obj.data.trackEvents.startIndex <= idx ) {
          obj.data.trackEvents.startIndex--;
          obj.data.trackEvents.endIndex--;
        }
      }

      // clean any remaining references in the end index
      // we do this seperate from the above check because they might not be in the same order
      if ( byEnd[ idx ] && byEnd[ idx ]._natives && byEnd[ idx ]._natives.type === name ) {

        byEnd.splice( idx, 1 );
      }
    }

    //remove all animating events
    for ( idx = 0, sl = animating.length; idx < sl; idx++ ) {

      if ( animating[ idx ] && animating[ idx ]._natives && animating[ idx ]._natives.type === name ) {

        animating.splice( idx, 1 );

        // update for loop if something removed, but keep checking
        idx--; sl--;
      }
    }

  };

  Popcorn.compositions = {};

  //  Plugin inheritance
  Popcorn.compose = function( name, definition, manifest ) {

    //  If `manifest` arg is undefined, check for manifest within the `definition` object
    //  If no `definition.manifest`, an empty object is a sufficient fallback
    Popcorn.manifest[ name ] = manifest = manifest || definition.manifest || {};

    // register the effect by name
    Popcorn.compositions[ name ] = definition;
  };

  Popcorn.plugin.effect = Popcorn.effect = Popcorn.compose;

  var rnaiveExpr = /^(?:\.|#|\[)/;

  //  Basic DOM utilities and helpers API. See #1037
  Popcorn.dom = {
    debug: false,
    //  Popcorn.dom.find( selector, context )
    //
    //  Returns the first element that matches the specified selector
    //  Optionally provide a context element, defaults to `document`
    //
    //  eg.
    //  Popcorn.dom.find("video") returns the first video element
    //  Popcorn.dom.find("#foo") returns the first element with `id="foo"`
    //  Popcorn.dom.find("foo") returns the first element with `id="foo"`
    //     Note: Popcorn.dom.find("foo") is the only allowed deviation
    //           from valid querySelector selector syntax
    //
    //  Popcorn.dom.find(".baz") returns the first element with `class="baz"`
    //  Popcorn.dom.find("[preload]") returns the first element with `preload="..."`
    //  ...
    //  See https://developer.mozilla.org/En/DOM/Document.querySelector
    //
    //
    find: function( selector, context ) {
      var node = null;

      //  Default context is the `document`
      context = context || document;

      if ( selector ) {

        //  If the selector does not begin with "#", "." or "[",
        //  it could be either a nodeName or ID w/o "#"
        if ( !rnaiveExpr.test( selector ) ) {

          //  Try finding an element that matches by ID first
          node = document.getElementById( selector );

          //  If a match was found by ID, return the element
          if ( node !== null ) {
            return node;
          }
        }
        //  Assume no elements have been found yet
        //  Catch any invalid selector syntax errors and bury them.
        try {
          node = context.querySelector( selector );
        } catch ( e ) {
          if ( Popcorn.dom.debug ) {
            throw new Error(e);
          }
        }
      }
      return node;
    }
  };

  //  Cache references to reused RegExps
  var rparams = /\?/,
  //  XHR Setup object
  setup = {
    url: "",
    data: "",
    dataType: "",
    success: Popcorn.nop,
    type: "GET",
    async: true,
    xhr: function() {
      return new global.XMLHttpRequest();
    }
  };

  Popcorn.xhr = function( options ) {

    options.dataType = options.dataType && options.dataType.toLowerCase() || null;

    if ( options.dataType &&
         ( options.dataType === "jsonp" || options.dataType === "script" ) ) {

      Popcorn.xhr.getJSONP(
        options.url,
        options.success,
        options.dataType === "script"
      );
      return;
    }

    var settings = Popcorn.extend( {}, setup, options );

    //  Create new XMLHttpRequest object
    settings.ajax  = settings.xhr();

    if ( settings.ajax ) {

      if ( settings.type === "GET" && settings.data ) {

        //  append query string
        settings.url += ( rparams.test( settings.url ) ? "&" : "?" ) + settings.data;

        //  Garbage collect and reset settings.data
        settings.data = null;
      }


      settings.ajax.open( settings.type, settings.url, settings.async );
      settings.ajax.send( settings.data || null );

      return Popcorn.xhr.httpData( settings );
    }
  };


  Popcorn.xhr.httpData = function( settings ) {

    var data, json = null,
        parser, xml = null;

    settings.ajax.onreadystatechange = function() {

      if ( settings.ajax.readyState === 4 ) {

        try {
          json = JSON.parse( settings.ajax.responseText );
        } catch( e ) {
          //suppress
        }

        data = {
          xml: settings.ajax.responseXML,
          text: settings.ajax.responseText,
          json: json
        };

        // Normalize: data.xml is non-null in IE9 regardless of if response is valid xml
        if ( !data.xml || !data.xml.documentElement ) {
          data.xml = null;

          try {
            parser = new DOMParser();
            xml = parser.parseFromString( settings.ajax.responseText, "text/xml" );

            if ( !xml.getElementsByTagName( "parsererror" ).length ) {
              data.xml = xml;
            }
          } catch ( e ) {
            // data.xml remains null
          }
        }

        //  If a dataType was specified, return that type of data
        if ( settings.dataType ) {
          data = data[ settings.dataType ];
        }


        settings.success.call( settings.ajax, data );

      }
    };
    return data;
  };

  Popcorn.xhr.getJSONP = function( url, success, isScript ) {

    var head = document.head || document.getElementsByTagName( "head" )[ 0 ] || document.documentElement,
      script = document.createElement( "script" ),
      isFired = false,
      params = [],
      rjsonp = /(=)\?(?=&|$)|\?\?/,
      replaceInUrl, prefix, paramStr, callback, callparam;

    if ( !isScript ) {

      // is there a calback already in the url
      callparam = url.match( /(callback=[^&]*)/ );

      if ( callparam !== null && callparam.length ) {

        prefix = callparam[ 1 ].split( "=" )[ 1 ];

        // Since we need to support developer specified callbacks
        // and placeholders in harmony, make sure matches to "callback="
        // aren't just placeholders.
        // We coded ourselves into a corner here.
        // JSONP callbacks should never have been
        // allowed to have developer specified callbacks
        if ( prefix === "?" ) {
          prefix = "jsonp";
        }

        // get the callback name
        callback = Popcorn.guid( prefix );

        // replace existing callback name with unique callback name
        url = url.replace( /(callback=[^&]*)/, "callback=" + callback );
      } else {

        callback = Popcorn.guid( "jsonp" );

        if ( rjsonp.test( url ) ) {
          url = url.replace( rjsonp, "$1" + callback );
        }

        // split on first question mark,
        // this is to capture the query string
        params = url.split( /\?(.+)?/ );

        // rebuild url with callback
        url = params[ 0 ] + "?";
        if ( params[ 1 ] ) {
          url += params[ 1 ] + "&";
        }
        url += "callback=" + callback;
      }

      //  Define the JSONP success callback globally
      window[ callback ] = function( data ) {
        // Fire success callbacks
        success && success( data );
        isFired = true;
      };
    }

    script.addEventListener( "load",  function() {

      //  Handling remote script loading callbacks
      if ( isScript ) {
        //  getScript
        success && success();
      }

      //  Executing for JSONP requests
      if ( isFired ) {
        //  Garbage collect the callback
        delete window[ callback ];
      }
      //  Garbage collect the script resource
      head.removeChild( script );
    }, false );

    script.src = url;

    head.insertBefore( script, head.firstChild );

    return;
  };

  Popcorn.getJSONP = Popcorn.xhr.getJSONP;

  Popcorn.getScript = Popcorn.xhr.getScript = function( url, success ) {

    return Popcorn.xhr.getJSONP( url, success, true );
  };

  Popcorn.util = {
    // Simple function to parse a timestamp into seconds
    // Acceptable formats are:
    // HH:MM:SS.MMM
    // HH:MM:SS;FF
    // Hours and minutes are optional. They default to 0
    toSeconds: function( timeStr, framerate ) {
      // Hours and minutes are optional
      // Seconds must be specified
      // Seconds can be followed by milliseconds OR by the frame information
      var validTimeFormat = /^([0-9]+:){0,2}[0-9]+([.;][0-9]+)?$/,
          errorMessage = "Invalid time format",
          digitPairs, lastIndex, lastPair, firstPair,
          frameInfo, frameTime;

      if ( typeof timeStr === "number" ) {
        return timeStr;
      }

      if ( typeof timeStr === "string" &&
            !validTimeFormat.test( timeStr ) ) {
        Popcorn.error( errorMessage );
      }

      digitPairs = timeStr.split( ":" );
      lastIndex = digitPairs.length - 1;
      lastPair = digitPairs[ lastIndex ];

      // Fix last element:
      if ( lastPair.indexOf( ";" ) > -1 ) {

        frameInfo = lastPair.split( ";" );
        frameTime = 0;

        if ( framerate && ( typeof framerate === "number" ) ) {
          frameTime = parseFloat( frameInfo[ 1 ], 10 ) / framerate;
        }

        digitPairs[ lastIndex ] = parseInt( frameInfo[ 0 ], 10 ) + frameTime;
      }

      firstPair = digitPairs[ 0 ];

      return {

        1: parseFloat( firstPair, 10 ),

        2: ( parseInt( firstPair, 10 ) * 60 ) +
              parseFloat( digitPairs[ 1 ], 10 ),

        3: ( parseInt( firstPair, 10 ) * 3600 ) +
            ( parseInt( digitPairs[ 1 ], 10 ) * 60 ) +
              parseFloat( digitPairs[ 2 ], 10 )

      }[ digitPairs.length || 1 ];
    }
  };

  // alias for exec function
  Popcorn.p.cue = Popcorn.p.exec;

  //  Protected API methods
  Popcorn.protect = {
    natives: getKeys( Popcorn.p ).map(function( val ) {
      return val.toLowerCase();
    })
  };

  // Setup logging for deprecated methods
  Popcorn.forEach({
    // Deprecated: Recommended
    "listen": "on",
    "unlisten": "off",
    "trigger": "emit",
    "exec": "cue"

  }, function( recommend, api ) {
    var original = Popcorn.p[ api ];
    // Override the deprecated api method with a method of the same name
    // that logs a warning and defers to the new recommended method
    Popcorn.p[ api ] = function() {
      if ( typeof console !== "undefined" && console.warn ) {
        console.warn(
          "Deprecated method '" + api + "', " +
          (recommend == null ? "do not use." : "use '" + recommend + "' instead." )
        );

        // Restore api after first warning
        Popcorn.p[ api ] = original;
      }
      return Popcorn.p[ recommend ].apply( this, [].slice.call( arguments ) );
    };
  });


  //  Exposes Popcorn to global context
  global.Popcorn = Popcorn;

})(window, window.document);
(function( global, Popcorn ) {

  var navigator = global.navigator;

  // Initialize locale data
  // Based on http://en.wikipedia.org/wiki/Language_localisation#Language_tags_and_codes
  function initLocale( arg ) {

    var locale = typeof arg === "string" ? arg : [ arg.language, arg.region ].join( "-" ),
        parts = locale.split( "-" );

    // Setup locale data table
    return {
      iso6391: locale,
      language: parts[ 0 ] || "",
      region: parts[ 1 ] || ""
    };
  }

  // Declare locale data table
  var localeData = initLocale( navigator.userLanguage || navigator.language );

  Popcorn.locale = {

    // Popcorn.locale.get()
    // returns reference to privately
    // defined localeData
    get: function() {
      return localeData;
    },

    // Popcorn.locale.set( string|object );
    set: function( arg ) {

      localeData = initLocale( arg );

      Popcorn.locale.broadcast();

      return localeData;
    },

    // Popcorn.locale.broadcast( type )
    // Sends events to all popcorn media instances that are
    // listening for locale events
    broadcast: function( type ) {

      var instances = Popcorn.instances,
          length = instances.length,
          idx = 0,
          instance;

      type = type || "locale:changed";

      // Iterate all current instances
      for ( ; idx < length; idx++ ) {
        instance = instances[ idx ];

        // For those instances with locale event listeners,
        // trigger a locale change event
        if ( type in instance.data.events  ) {
          instance.trigger( type );
        }
      }
    }
  };
})( this, this.Popcorn );(function( Popcorn ) {

  var

  AP = Array.prototype,
  OP = Object.prototype,

  forEach = AP.forEach,
  slice = AP.slice,
  hasOwn = OP.hasOwnProperty,
  toString = OP.toString;

  // stores parsers keyed on filetype
  Popcorn.parsers = {};

  // An interface for extending Popcorn
  // with parser functionality
  Popcorn.parser = function( name, type, definition ) {

    if ( Popcorn.protect.natives.indexOf( name.toLowerCase() ) >= 0 ) {
      Popcorn.error( "'" + name + "' is a protected function name" );
      return;
    }

    // fixes parameters for overloaded function call
    if ( typeof type === "function" && !definition ) {
      definition = type;
      type = "";
    }

    if ( typeof definition !== "function" || typeof type !== "string" ) {
      return;
    }

    // Provides some sugar, but ultimately extends
    // the definition into Popcorn.p

    var natives = Popcorn.events.all,
        parseFn,
        parser = {};

    parseFn = function( filename, callback ) {

      if ( !filename ) {
        return this;
      }

      var that = this;

      Popcorn.xhr({
        url: filename,
        dataType: type,
        success: function( data ) {

          var tracksObject = definition( data ),
              tracksData,
              tracksDataLen,
              tracksDef,
              idx = 0;

          tracksData = tracksObject.data || [];
          tracksDataLen = tracksData.length;
          tracksDef = null;

          //  If no tracks to process, return immediately
          if ( !tracksDataLen ) {
            return;
          }

          //  Create tracks out of parsed object
          for ( ; idx < tracksDataLen; idx++ ) {

            tracksDef = tracksData[ idx ];

            for ( var key in tracksDef ) {

              if ( hasOwn.call( tracksDef, key ) && !!that[ key ] ) {

                that[ key ]( tracksDef[ key ] );
              }
            }
          }
          if ( callback ) {
            callback();
          }
        }
      });

      return this;
    };

    // Assign new named definition
    parser[ name ] = parseFn;

    // Extend Popcorn.p with new named definition
    Popcorn.extend( Popcorn.p, parser );

    // keys the function name by filetype extension
    //Popcorn.parsers[ name ] = true;

    return parser;
  };
})( Popcorn );(function( Popcorn ) {

  // combines calls of two function calls into one
  var combineFn = function( first, second ) {

    first = first || Popcorn.nop;
    second = second || Popcorn.nop;

    return function() {

      first.apply( this, arguments );
      second.apply( this, arguments );
    };
  };

  //  ID string matching
  var rIdExp  = /^(#([\w\-\_\.]+))$/;

  Popcorn.player = function( name, player ) {

    // return early if a player already exists under this name
    if ( Popcorn[ name ] ) {

      return;
    }

    player = player || {};

    var playerFn = function( target, src, options ) {

      options = options || {};

      // List of events
      var date = new Date() / 1000,
          baselineTime = date,
          currentTime = 0,
          readyState = 0,
          volume = 1,
          muted = false,
          events = {},

          // The container div of the resource
          container = typeof target === "string" ? Popcorn.dom.find( target ) : target,
          basePlayer = {},
          timeout,
          popcorn;

      if ( !Object.prototype.__defineGetter__ ) {

        basePlayer = container || document.createElement( "div" );
      }

      // copies a div into the media object
      for( var val in container ) {

        // don't copy properties if using container as baseplayer
        if ( val in basePlayer ) {

          continue;
        }

        if ( typeof container[ val ] === "object" ) {

          basePlayer[ val ] = container[ val ];
        } else if ( typeof container[ val ] === "function" ) {

          basePlayer[ val ] = (function( value ) {

            // this is a stupid ugly kludgy hack in honour of Safari
            // in Safari a NodeList is a function, not an object
            if ( "length" in container[ value ] && !container[ value ].call ) {

              return container[ value ];
            } else {

              return function() {

                return container[ value ].apply( container, arguments );
              };
            }
          }( val ));
        } else {

          Popcorn.player.defineProperty( basePlayer, val, {
            get: (function( value ) {

              return function() {

                return container[ value ];
              };
            }( val )),
            set: Popcorn.nop,
            configurable: true
          });
        }
      }

      var timeupdate = function() {

        date = new Date() / 1000;

        if ( !basePlayer.paused ) {

          basePlayer.currentTime = basePlayer.currentTime + ( date - baselineTime );
          basePlayer.dispatchEvent( "timeupdate" );
          timeout = setTimeout( timeupdate, 10 );
        }

        baselineTime = date;
      };

      basePlayer.play = function() {

        this.paused = false;

        if ( basePlayer.readyState >= 4 ) {

          baselineTime = new Date() / 1000;
          basePlayer.dispatchEvent( "play" );
          timeupdate();
        }
      };

      basePlayer.pause = function() {

        this.paused = true;
        basePlayer.dispatchEvent( "pause" );
      };

      Popcorn.player.defineProperty( basePlayer, "currentTime", {
        get: function() {

          return currentTime;
        },
        set: function( val ) {

          // make sure val is a number
          currentTime = +val;
          basePlayer.dispatchEvent( "timeupdate" );

          return currentTime;
        },
        configurable: true
      });

      Popcorn.player.defineProperty( basePlayer, "volume", {
        get: function() {

          return volume;
        },
        set: function( val ) {

          // make sure val is a number
          volume = +val;
          basePlayer.dispatchEvent( "volumechange" );
          return volume;
        },
        configurable: true
      });

      Popcorn.player.defineProperty( basePlayer, "muted", {
        get: function() {

          return muted;
        },
        set: function( val ) {

          // make sure val is a number
          muted = +val;
          basePlayer.dispatchEvent( "volumechange" );
          return muted;
        },
        configurable: true
      });

      Popcorn.player.defineProperty( basePlayer, "readyState", {
        get: function() {

          return readyState;
        },
        set: function( val ) {

          readyState = val;
          return readyState;
        },
        configurable: true
      });

      // Adds an event listener to the object
      basePlayer.addEventListener = function( evtName, fn ) {

        if ( !events[ evtName ] ) {

          events[ evtName ] = [];
        }

        events[ evtName ].push( fn );
        return fn;
      };

      // Removes an event listener from the object
      basePlayer.removeEventListener = function( evtName, fn ) {

        var i,
            listeners = events[ evtName ];

        if ( !listeners ){

          return;
        }

        // walk backwards so we can safely splice
        for ( i = events[ evtName ].length - 1; i >= 0; i-- ) {

          if( fn === listeners[ i ] ) {

            listeners.splice(i, 1);
          }
        }

        return fn;
      };

      // Can take event object or simple string
      basePlayer.dispatchEvent = function( oEvent ) {

        var evt,
            self = this,
            eventInterface,
            eventName = oEvent.type;

        // A string was passed, create event object
        if ( !eventName ) {

          eventName = oEvent;
          eventInterface  = Popcorn.events.getInterface( eventName );

          if ( eventInterface ) {

            evt = document.createEvent( eventInterface );
            evt.initEvent( eventName, true, true, window, 1 );
          }
        }

        if ( events[ eventName ] ) {

          for ( var i = events[ eventName ].length - 1; i >= 0; i-- ) {

            events[ eventName ][ i ].call( self, evt, self );
          }
        }
      };

      // Attempt to get src from playerFn parameter
      basePlayer.src = src || "";
      basePlayer.duration = 0;
      basePlayer.paused = true;
      basePlayer.ended = 0;

      options && options.events && Popcorn.forEach( options.events, function( val, key ) {

        basePlayer.addEventListener( key, val, false );
      });

      // true and undefined returns on canPlayType means we should attempt to use it,
      // false means we cannot play this type
      if ( player._canPlayType( container.nodeName, src ) !== false ) {

        if ( player._setup ) {

          player._setup.call( basePlayer, options );
        } else {

          // there is no setup, which means there is nothing to load
          basePlayer.readyState = 4;
          basePlayer.dispatchEvent( "loadedmetadata" );
          basePlayer.dispatchEvent( "loadeddata" );
          basePlayer.dispatchEvent( "canplaythrough" );
        }
      } else {

        // Asynchronous so that users can catch this event
        setTimeout( function() {
          basePlayer.dispatchEvent( "error" );
        }, 0 );
      }

      popcorn = new Popcorn.p.init( basePlayer, options );

      if ( player._teardown ) {

        popcorn.destroy = combineFn( popcorn.destroy, function() {

          player._teardown.call( basePlayer, options );
        });
      }

      return popcorn;
    };

    playerFn.canPlayType = player._canPlayType = player._canPlayType || Popcorn.nop;

    Popcorn[ name ] = Popcorn.player.registry[ name ] = playerFn;
  };

  Popcorn.player.registry = {};

  Popcorn.player.defineProperty = Object.defineProperty || function( object, description, options ) {

    object.__defineGetter__( description, options.get || Popcorn.nop );
    object.__defineSetter__( description, options.set || Popcorn.nop );
  };

  // player queue is to help players queue things like play and pause
  // HTML5 video's play and pause are asynch, but do fire in sequence
  // play() should really mean "requestPlay()" or "queuePlay()" and
  // stash a callback that will play the media resource when it's ready to be played
  Popcorn.player.playerQueue = function() {

    var _queue = [],
        _running = false;

    return {
      next: function() {

        _running = false;
        _queue.shift();
        _queue[ 0 ] && _queue[ 0 ]();
      },
      add: function( callback ) {

        _queue.push(function() {

          _running = true;
          callback && callback();
        });

        // if there is only one item on the queue, start it
        !_running && _queue[ 0 ]();
      }
    };
  };

  // Popcorn.smart will attempt to find you a wrapper or player. If it can't do that,
  // it will default to using an HTML5 video in the target.
  Popcorn.smart = function( target, src, options ) {
    var node = typeof target === "string" ? Popcorn.dom.find( target ) : target,
        i, srci, j, media, mediaWrapper, popcorn,
        // We leave HTMLVideoElement and HTMLAudioElement wrappers out
        // of the mix, since we'll default to HTML5 video if nothing
        // else works.  Waiting on #1254 before we add YouTube to this.
        wrappers = "HTMLVimeoVideoElement HTMLSoundCloudAudioElement HTMLNullVideoElement".split(" ");

    if ( !node ) {
      Popcorn.error( "Specified target `" + target + "` was not found." );
      return;
    }

    // If our src is not an array, create an array of one.
    src = typeof src === "string" ? [ src ] : src;

    // Loop through each src, and find the first playable.
    for ( i = 0, srcLength = src.length; i < srcLength; i++ ) {
      srci = src[ i ];

      // See if we can use a wrapper directly, if not, try players.
      for ( j = 0; j < wrappers.length; j++ ) {
        mediaWrapper = Popcorn[ wrappers[ j ] ];
        if ( mediaWrapper._canPlaySrc( srci ) === "probably" ) {
          media = mediaWrapper( node );
          popcorn = Popcorn( media, options );
          // Set src, but not until after we return the media so the caller
          // can get error events, if any.
          setTimeout( function() {
            media.src = srci;
          }, 0 );
          return popcorn;
        }
      }

      // No wrapper can play this, check players.
      for ( var key in Popcorn.player.registry ) {
        if ( Popcorn.player.registry.hasOwnProperty( key ) ) {
          if ( Popcorn.player.registry[ key ].canPlayType( node.nodeName, srci ) ) {
            // Popcorn.smart( player, src, /* options */ )
            return Popcorn[ key ]( node, srci, options );
          }
        }
      }
    }

    // If we don't have any players or wrappers that can handle this,
    // Default to using HTML5 video.  Similar to the HTMLVideoElement
    // wrapper, we put a video in the div passed to us via:
    // Popcorn.smart( div, src, options )
    var videoHTML, videoID = Popcorn.guid( "popcorn-video-" );

    // IE9 doesn't like dynamic creation of source elements on <video>
    // so we do it in one shot via innerHTML.
    videoHTML = '<video id="' +  videoID + '" preload=auto autobuffer>';
    for ( i = 0, srcLength = src.length; i < srcLength; i++ ) {
      videoHTML += '<source src="' + src[ i ] + '">';
    }
    videoHTML += "</video>";
    node.innerHTML = videoHTML;

    if ( options && options.events && options.events.error ) {
      node.addEventListener( "error", options.events.error, false );
    }
    return Popcorn( '#' + videoID, options );
  };
})( Popcorn );
/*!
 * Popcorn.sequence
 *
 * Copyright 2011, Rick Waldron
 * Licensed under MIT license.
 *
 */

/* jslint forin: true, maxerr: 50, indent: 4, es5: true  */
/* global Popcorn: true */

// Requires Popcorn.js
(function( global, Popcorn ) {

  // TODO: as support increases, migrate to element.dataset
  var doc = global.document,
      location = global.location,
      rprotocol = /:\/\//,
      // TODO: better solution to this sucky stop-gap
      lochref = location.href.replace( location.href.split("/").slice(-1)[0], "" ),
      // privately held
      range = function(start, stop, step) {

        start = start || 0;
        stop = ( stop || start || 0 ) + 1;
        step = step || 1;

        var len = Math.ceil((stop - start) / step) || 0,
            idx = 0,
            range = [];

        range.length = len;

        while (idx < len) {
         range[idx++] = start;
         start += step;
        }
        return range;
      };

  Popcorn.sequence = function( parent, list ) {
    return new Popcorn.sequence.init( parent, list );
  };

  Popcorn.sequence.init = function( parent, list ) {

    // Video element
    this.parent = doc.getElementById( parent );

    // Store ref to a special ID
    this.seqId = Popcorn.guid( "__sequenced" );

    // List of HTMLVideoElements
    this.queue = [];

    // List of Popcorn objects
    this.playlist = [];

    // Lists of in/out points
    this.inOuts = {

      // Stores the video in/out times for each video in sequence
      ofVideos: [],

      // Stores the clip in/out times for each clip in sequences
      ofClips: []

    };

    // Store first video dimensions
    this.dims = {
      width: 0, //this.video.videoWidth,
      height: 0 //this.video.videoHeight
    };

    this.active = 0;
    this.cycling = false;
    this.playing = false;

    this.times = {
      last: 0
    };

    // Store event pointers and queues
    this.events = {

    };

    var self = this,
        clipOffset = 0;

    // Create `video` elements
    Popcorn.forEach( list, function( media, idx ) {

      var video = doc.createElement( "video" );

      video.preload = "auto";

      // Setup newly created video element
      video.controls = true;

      // If the first, show it, if the after, hide it
      video.style.display = ( idx && "none" ) || "" ;

      // Seta registered sequence id
      video.id = self.seqId + "-" + idx ;

      // Push this video into the sequence queue
      self.queue.push( video );

      var //satisfy lint
       mIn = media["in"],
       mOut = media["out"];

      // Push the in/out points into sequence ioVideos
      self.inOuts.ofVideos.push({
        "in": ( mIn !== undefined && mIn ) || 1,
        "out": ( mOut !== undefined && mOut ) || 0
      });

      self.inOuts.ofVideos[ idx ]["out"] = self.inOuts.ofVideos[ idx ]["out"] || self.inOuts.ofVideos[ idx ]["in"] + 2;

      // Set the sources
      video.src = !rprotocol.test( media.src ) ? lochref + media.src : media.src;

      // Set some squence specific data vars
      video.setAttribute("data-sequence-owner", parent );
      video.setAttribute("data-sequence-guid", self.seqId );
      video.setAttribute("data-sequence-id", idx );
      video.setAttribute("data-sequence-clip", [ self.inOuts.ofVideos[ idx ]["in"], self.inOuts.ofVideos[ idx ]["out"] ].join(":") );

      // Append the video to the parent element
      self.parent.appendChild( video );


      self.playlist.push( Popcorn("#" + video.id ) );

    });

    self.inOuts.ofVideos.forEach(function( obj ) {

      var clipDuration = obj["out"] - obj["in"],
          offs = {
            "in": clipOffset,
            "out": clipOffset + clipDuration
          };

      self.inOuts.ofClips.push( offs );

      clipOffset = offs["out"] + 1;
    });

    Popcorn.forEach( this.queue, function( media, idx ) {

      function canPlayThrough( event ) {

        // If this is idx zero, use it as dimension for all
        if ( !idx ) {
          self.dims.width = media.videoWidth;
          self.dims.height = media.videoHeight;
        }

        media.currentTime = self.inOuts.ofVideos[ idx ]["in"] - 0.5;

        media.removeEventListener( "canplaythrough", canPlayThrough, false );

        return true;
      }

      // Hook up event listeners for managing special playback
      media.addEventListener( "canplaythrough", canPlayThrough, false );

      // TODO: consolidate & DRY
      media.addEventListener( "play", function( event ) {

        self.playing = true;

      }, false );

      media.addEventListener( "pause", function( event ) {

        self.playing = false;

      }, false );

      media.addEventListener( "timeupdate", function( event ) {

        var target = event.srcElement || event.target,
            seqIdx = +(  (target.dataset && target.dataset.sequenceId) || target.getAttribute("data-sequence-id") ),
            floor = Math.floor( media.currentTime );

        if ( self.times.last !== floor &&
              seqIdx === self.active ) {

          self.times.last = floor;

          if ( floor === self.inOuts.ofVideos[ seqIdx ]["out"] ) {

            Popcorn.sequence.cycle.call( self, seqIdx );
          }
        }
      }, false );
    });

    return this;
  };

  Popcorn.sequence.init.prototype = Popcorn.sequence.prototype;

  //
  Popcorn.sequence.cycle = function( idx ) {

    if ( !this.queue ) {
      Popcorn.error("Popcorn.sequence.cycle is not a public method");
    }

    var // Localize references
    queue = this.queue,
    ioVideos = this.inOuts.ofVideos,
    current = queue[ idx ],
    nextIdx = 0,
    next, clip;


    var // Popcorn instances
    $popnext,
    $popprev;


    if ( queue[ idx + 1 ] ) {
      nextIdx = idx + 1;
    }

    // Reset queue
    if ( !queue[ idx + 1 ] ) {

      nextIdx = 0;
      this.playlist[ idx ].pause();

    } else {

      next = queue[ nextIdx ];
      clip = ioVideos[ nextIdx ];

      // Constrain dimentions
      Popcorn.extend( next, {
        width: this.dims.width,
        height: this.dims.height
      });

      $popnext = this.playlist[ nextIdx ];
      $popprev = this.playlist[ idx ];

      // When not resetting to 0
      current.pause();

      this.active = nextIdx;
      this.times.last = clip["in"] - 1;

      // Play the next video in the sequence
      $popnext.currentTime( clip["in"] );

      $popnext[ nextIdx ? "play" : "pause" ]();

      // Trigger custom cycling event hook
      this.trigger( "cycle", {

        position: {
          previous: idx,
          current: nextIdx
        }

      });

      // Set the previous back to it's beginning time
      // $popprev.currentTime( ioVideos[ idx ].in );

      if ( nextIdx ) {
        // Hide the currently ending video
        current.style.display = "none";
        // Show the next video in the sequence
        next.style.display = "";
      }

      this.cycling = false;
    }

    return this;
  };

  var excludes = [ "timeupdate", "play", "pause" ];

  // Sequence object prototype
  Popcorn.extend( Popcorn.sequence.prototype, {

    // Returns Popcorn object from sequence at index
    eq: function( idx ) {
      return this.playlist[ idx ];
    },
    // Remove a sequence from it's playback display container
    remove: function() {
      this.parent.innerHTML = null;
    },
    // Returns Clip object from sequence at index
    clip: function( idx ) {
      return this.inOuts.ofVideos[ idx ];
    },
    // Returns sum duration for all videos in sequence
    duration: function() {

      var ret = 0,
          seq = this.inOuts.ofClips,
          idx = 0;

      for ( ; idx < seq.length; idx++ ) {
        ret += seq[ idx ]["out"] - seq[ idx ]["in"] + 1;
      }

      return ret - 1;
    },

    play: function() {

      this.playlist[ this.active ].play();

      return this;
    },
    // Attach an event to a single point in time
    exec: function ( time, fn ) {

      var index = this.active;

      this.inOuts.ofClips.forEach(function( off, idx ) {
        if ( time >= off["in"] && time <= off["out"] ) {
          index = idx;
        }
      });

      //offsetBy = time - self.inOuts.ofVideos[ index ].in;

      time += this.inOuts.ofVideos[ index ]["in"] - this.inOuts.ofClips[ index ]["in"];

      // Creating a one second track event with an empty end
      Popcorn.addTrackEvent( this.playlist[ index ], {
        start: time - 1,
        end: time,
        _running: false,
        _natives: {
          start: fn || Popcorn.nop,
          end: Popcorn.nop,
          type: "exec"
        }
      });

      return this;
    },
    // Binds event handlers that fire only when all
    // videos in sequence have heard the event
    listen: function( type, callback ) {

      var self = this,
          seq = this.playlist,
          total = seq.length,
          count = 0,
          fnName;

      if ( !callback ) {
        callback = Popcorn.nop;
      }

      // Handling for DOM and Media events
      if ( Popcorn.Events.Natives.indexOf( type ) > -1 ) {
        Popcorn.forEach( seq, function( video ) {

          video.listen( type, function( event ) {

            event.active = self;

            if ( excludes.indexOf( type ) > -1 ) {

              callback.call( video, event );

            } else {
              if ( ++count === total ) {
                callback.call( video, event );
              }
            }
          });
        });

      } else {

        // If no events registered with this name, create a cache
        if ( !this.events[ type ] ) {
          this.events[ type ] = {};
        }

        // Normalize a callback name key
        fnName = callback.name || Popcorn.guid( "__" + type );

        // Store in event cache
        this.events[ type ][ fnName ] = callback;
      }

      // Return the sequence object
      return this;
    },
    unlisten: function( type, name ) {
      // TODO: finish implementation
    },
    trigger: function( type, data ) {
      var self = this;

      // Handling for DOM and Media events
      if ( Popcorn.Events.Natives.indexOf( type ) > -1 ) {

        //  find the active video and trigger api events on that video.
        return;

      } else {

        // Only proceed if there are events of this type
        // currently registered on the sequence
        if ( this.events[ type ] ) {

          Popcorn.forEach( this.events[ type ], function( callback, name ) {
            callback.call( self, { type: type }, data );
          });

        }
      }

      return this;
    }
  });


  Popcorn.forEach( Popcorn.manifest, function( obj, plugin ) {

    // Implement passthrough methods to plugins
    Popcorn.sequence.prototype[ plugin ] = function( options ) {

      // console.log( this, options );
      var videos = {}, assignTo = [],
      idx, off, inOuts, inIdx, outIdx, keys, clip, clipInOut, clipRange;

      for ( idx = 0; idx < this.inOuts.ofClips.length; idx++  ) {
        // store reference
        off = this.inOuts.ofClips[ idx ];
        // array to test against
        inOuts = range( off["in"], off["out"] );

        inIdx = inOuts.indexOf( options.start );
        outIdx = inOuts.indexOf( options.end );

        if ( inIdx > -1 ) {
          videos[ idx ] = Popcorn.extend( {}, off, {
            start: inOuts[ inIdx ],
            clipIdx: inIdx
          });
        }

        if ( outIdx > -1 ) {
          videos[ idx ] = Popcorn.extend( {}, off, {
            end: inOuts[ outIdx ],
            clipIdx: outIdx
          });
        }
      }

      keys = Object.keys( videos ).map(function( val ) {
                return +val;
              });

      assignTo = range( keys[ 0 ], keys[ 1 ] );

      //console.log( "PLUGIN CALL MAPS: ", videos, keys, assignTo );
      for ( idx = 0; idx < assignTo.length; idx++ ) {

        var compile = {},
        play = assignTo[ idx ],
        vClip = videos[ play ];

        if ( vClip ) {

          // has instructions
          clip = this.inOuts.ofVideos[ play ];
          clipInOut = vClip.clipIdx;
          clipRange = range( clip["in"], clip["out"] );

          if ( vClip.start ) {
            compile.start = clipRange[ clipInOut ];
            compile.end = clipRange[ clipRange.length - 1 ];
          }

          if ( vClip.end ) {
            compile.start = clipRange[ 0 ];
            compile.end = clipRange[ clipInOut ];
          }

          //compile.start += 0.1;
          //compile.end += 0.9;

        } else {

          compile.start = this.inOuts.ofVideos[ play ]["in"];
          compile.end = this.inOuts.ofVideos[ play ]["out"];

          //compile.start += 0.1;
          //compile.end += 0.9;

        }

        // Handling full clip persistance
        //if ( compile.start === compile.end ) {
          //compile.start -= 0.1;
          //compile.end += 0.9;
        //}

        // Call the plugin on the appropriate Popcorn object in the playlist
        // Merge original options object & compiled (start/end) object into
        // a new fresh object
        this.playlist[ play ][ plugin ](

          Popcorn.extend( {}, options, compile )

        );

      }

      // Return the sequence object
      return this;
    };

  });
})( this, Popcorn );
(function( Popcorn ) {
  document.addEventListener( "DOMContentLoaded", function() {

    //  Supports non-specific elements
    var dataAttr = "data-timeline-sources",
        medias = document.querySelectorAll( "[" + dataAttr + "]" );

    Popcorn.forEach( medias, function( idx, key ) {

      var media = medias[ key ],
          hasDataSources = false,
          dataSources, data, popcornMedia;

      //  Ensure that the DOM has an id
      if ( !media.id ) {

        media.id = Popcorn.guid( "__popcorn" );
      }

      //  Ensure we're looking at a dom node
      if ( media.nodeType && media.nodeType === 1 ) {

        popcornMedia = Popcorn( "#" + media.id );

        dataSources = ( media.getAttribute( dataAttr ) || "" ).split( "," );

        if ( dataSources[ 0 ] ) {

          Popcorn.forEach( dataSources, function( source ) {

            // split the parser and data as parser!file
            data = source.split( "!" );

            // if no parser is defined for the file, assume "parse" + file extension
            if ( data.length === 1 ) {

              // parse a relative URL for the filename, split to get extension
              data = source.match( /(.*)[\/\\]([^\/\\]+\.\w+)$/ )[ 2 ].split( "." );

              data[ 0 ] = "parse" + data[ 1 ].toUpperCase();
              data[ 1 ] = source;
            }

            //  If the media has data sources and the correct parser is registered, continue to load
            if ( dataSources[ 0 ] && popcornMedia[ data[ 0 ] ] ) {

              //  Set up the media and load in the datasources
              popcornMedia[ data[ 0 ] ]( data[ 1 ] );

            }
          });

        }

        //  Only play the media if it was specified to do so
        if ( !!popcornMedia.autoplay() ) {
          popcornMedia.play();
        }

      }
    });
  }, false );

})( Popcorn );// PLUGIN: Code

(function ( Popcorn ) {

  /**
   * Code Popcorn Plug-in
   *
   * Adds the ability to run arbitrary code (JavaScript functions) according to video timing.
   *
   * @param {Object} options
   *
   * Required parameters: start, end, template, data, and target.
   * Optional parameter: static.
   *
   *   start: the time in seconds when the mustache template should be rendered
   *          in the target div.
   *
   *   end: the time in seconds when the rendered mustache template should be
   *        removed from the target div.
   *
   *   onStart: the function to be run when the start time is reached.
   *
   *   onFrame: [optional] a function to be run on each paint call
   *            (e.g., called ~60 times per second) between the start and end times.
   *
   *   onEnd: [optional] a function to be run when the end time is reached.
   *
   * Example:
     var p = Popcorn('#video')

        // onStart function only
        .code({
          start: 1,
          end: 4,
          onStart: function( options ) {
            // called on start
          }
        })

        // onStart + onEnd only
        .code({
          start: 6,
          end: 8,
          onStart: function( options ) {
            // called on start
          },
          onEnd: function ( options ) {
            // called on end
          }
        })

        // onStart, onEnd, onFrame
        .code({
          start: 10,
          end: 14,
          onStart: function( options ) {
            // called on start
          },
          onFrame: function ( options ) {
            // called on every paint frame between start and end.
            // uses mozRequestAnimationFrame, webkitRequestAnimationFrame,
            // or setTimeout with 16ms window.
          },
          onEnd: function ( options ) {
            // called on end
          }
        });
  *
  */

  Popcorn.plugin( "code" , function( options ) {
    var running = false,
        instance = this;

    // Setup a proper frame interval function (60fps), favouring paint events.
    var step = (function() {

      var buildFrameRunner = function( runner ) {
        return function( f, options ) {

          var _f = function() {
            running && f.call( instance, options );
            running && runner( _f );
          };

          _f();
        };
      };

      // Figure out which level of browser support we have for this
      if ( window.webkitRequestAnimationFrame ) {
        return buildFrameRunner( window.webkitRequestAnimationFrame );
      } else if ( window.mozRequestAnimationFrame ) {
        return buildFrameRunner( window.mozRequestAnimationFrame );
      } else {
        return buildFrameRunner( function( f ) {
          window.setTimeout( f, 16 );
        });
      }

    })();

    if ( !options.onStart || typeof options.onStart !== "function" ) {

      options.onStart = Popcorn.nop;
    }

    if ( options.onEnd && typeof options.onEnd !== "function" ) {

      options.onEnd = undefined;
    }

    if ( options.onFrame && typeof options.onFrame !== "function" ) {

      options.onFrame = undefined;
    }

    return {
      start: function( event, options ) {
        options.onStart.call( instance, options );

        if ( options.onFrame ) {
          running = true;
          step( options.onFrame, options );
        }
      },

      end: function( event, options ) {
        if ( options.onFrame ) {
          running = false;
        }

        if ( options.onEnd ) {
          options.onEnd.call( instance, options );
        }
      }
    };
  },
  {
    about: {
      name: "Popcorn Code Plugin",
      version: "0.1",
      author: "David Humphrey (@humphd)",
      website: "http://vocamus.net/dave"
    },
    options: {
      start: {
       elem: "input",
       type: "number",
       label: "Start"
      },
      end: {
        elem: "input",
        type: "number",
        label: "End"
      },
      onStart: {
        elem: "input",
        type: "function",
        label: "onStart"
      },
      onFrame: {
        elem: "input",
        type: "function",
        label: "onFrame",
        optional: true
      },
      onEnd: {
        elem: "input",
        type: "function",
        label: "onEnd"
      }
    }
  });
})( Popcorn );
// PLUGIN: documentcloud

(function( Popcorn, document ) {

  /**
   * Document Cloud popcorn plug-in
   *
   * @param {Object} options
   *
   * Example:
   *  var p = Popcorn("#video")
   *     // Let the pdf plugin load your PDF file for you using pdfUrl.
   *     .documentcloud({
   *       start: 45
   *       url: "http://www.documentcloud.org/documents/70050-urbina-day-1-in-progress.html", // or .js
   *       width: ...,
   *       height: ...,
   *       zoom: ...,
   *       page: ...,
   *       container: ...
   *     });

api - https://github.com/documentcloud/document-viewer/blob/master/public/javascripts/DV/controllers/api.js

   */

   // track registered plugins by document
   var documentRegistry = {};

  Popcorn.plugin( "documentcloud", {

    manifest: {
      about: {
        name: "Popcorn Document Cloud Plugin",
        version: "0.1",
        author: "@humphd, @ChrisDeCairos",
        website: "http://vocamus.net/dave"
      },
      options: {
        start: {
          elem: "input",
          type: "number",
          label: "Start"
        },
        end: {
          elem: "input",
          type: "number",
          label: "End"
        },
        target: "documentcloud-container",
        width: {
          elem: "input",
          type: "text",
          label: "Width",
          optional: true
        },
        height: {
          elem: "input",
          type: "text",
          label: "Height",
          optional: true
        },
        src: {
          elem: "input",
          type: "url",
          label: "PDF URL",
          "default": "http://www.documentcloud.org/documents/70050-urbina-day-1-in-progress.html"
        },
        preload: {
          elem: "input",
          type: "checkbox",
          label: "Preload",
          "default": true
        },
        page: {
          elem: "input",
          type: "number",
          label: "Page Number",
          optional: true
        },
        aid: {
          elem: "input",
          type: "number",
          label: "Annotation Id",
          optional: true
        }
      }
    },

    _setup: function( options ) {
      var DV = window.DV = window.DV || {},
          that = this;

      //setup elem...
      function load() {
        DV.loaded = false;
        // swap .html URL to .js for API call
        var url = options.url.replace( /\.html$/, ".js" ),
          target = options.target,
          targetDiv = document.getElementById( target ),
          containerDiv = document.createElement( "div" ),
          containerDivSize = Popcorn.position( targetDiv ),
          // need to use size of div if not given
          width = options.width || containerDivSize.width,
          height = options.height || containerDivSize.height,
          sidebar = options.sidebar || true,
          text = options.text || true,
          pdf = options.pdf || true,
          showAnnotations = options.showAnnotations || true,
          zoom = options.zoom || 700,
          search = options.search || true,
          page = options.page,
          container;

        function setOptions( viewer ) {
          options._key = viewer.api.getId();

          options._changeView = function ( viewer ) {
            if ( options.aid ) {
              viewer.pageSet.showAnnotation( viewer.api.getAnnotation( options.aid ) );
            } else {
              viewer.api.setCurrentPage( options.page );
            }
          };
        }

        function documentIsLoaded( url ) {
          var found = false;
          Popcorn.forEach( DV.viewers, function( viewer, idx ) {
            if( viewer.api.getSchema().canonicalURL === url ) {
              var targetDoc;
              setOptions( viewer );
              targetDoc = documentRegistry[ options._key ];
              options._containerId = targetDoc.id;
              targetDoc.num += 1;
              found = true;
              DV.loaded = true;
            }
          });
          return found;
        }

        function createRegistryEntry() {
          var entry = {
            num: 1,
            id: options._containerId
          };
          documentRegistry[ options._key ] = entry;
          DV.loaded = true;
        }

        if ( !documentIsLoaded( options.url ) ) {

          containerDiv.id = options._containerId = Popcorn.guid( target );
          container = "#" + containerDiv.id;
          targetDiv.appendChild( containerDiv );
          that.trigger( "documentready" );

          // Figure out if we need a callback to change the page #
          var afterLoad = options.page || options.aid ?
            function( viewer ) {
              setOptions( viewer );
              options._changeView( viewer );
              containerDiv.style.visibility = "hidden";
              viewer.elements.pages.hide();
              createRegistryEntry();
            } :
            function( viewer ) {
              setOptions( viewer );
              createRegistryEntry();
              containerDiv.style.visibility = "hidden";
              viewer.elements.pages.hide();
            };
          DV.load( url, {
            width: width,
            height: height,
            sidebar: sidebar,
            text: text,
            pdf: pdf,
            showAnnotations: showAnnotations,
            zoom: zoom,
            search: search,
            container: container,
            afterLoad: afterLoad
          });
        }
      }
      function readyCheck() {
        if( window.DV.loaded ) {
          load();
        } else {
          setTimeout( readyCheck, 25 );
        }
      }

      // If the viewer is already loaded, don't repeat the process.
      if ( !DV.loading ) {
        DV.loading = true;
        DV.recordHit = "//www.documentcloud.org/pixel.gif";

        var link = document.createElement( "link" ),
            head = document.getElementsByTagName( "head" )[ 0 ];

        link.rel = "stylesheet";
        link.type = "text/css";
        link.media = "screen";
        link.href = "//s3.documentcloud.org/viewer/viewer-datauri.css";

        head.appendChild( link );

        // Record the fact that the viewer is loaded.
        DV.loaded = false;

        // Request the viewer JavaScript.
        Popcorn.getScript( "http://s3.documentcloud.org/viewer/viewer.js", function() {
          DV.loading = false;
          load();
        });
      } else {

        readyCheck();
      }

      options.toString = function() {
        // use the default option if it doesn't exist
        return options.src || options._natives.manifest.options.src[ "default" ];
      };
    },

    start: function( event, options ) {
      var elem = document.getElementById( options._containerId ),
          viewer = DV.viewers[ options._key ];
      ( options.page || options.aid ) && viewer &&
        options._changeView( viewer );

      if ( elem && viewer) {
        elem.style.visibility = "visible";
        viewer.elements.pages.show();
      }
    },

    end: function( event, options ) {
      var elem = document.getElementById( options._containerId );

      if ( elem && DV.viewers[ options._key ] ) {
        elem.style.visibility = "hidden";
        DV.viewers[ options._key ].elements.pages.hide();
      }
    },

    _teardown: function( options ) {
      var elem = document.getElementById( options._containerId ),
          key = options._key;
      if ( key && DV.viewers[ key ] && --documentRegistry[ key ].num === 0 ) {
        DV.viewers[ key ].api.unload();

        while ( elem.hasChildNodes() ) {
          elem.removeChild( elem.lastChild );
        }
        elem.parentNode.removeChild( elem );
      }
    }
  });
})( Popcorn, window.document );
// PLUGIN: Flickr
(function (Popcorn) {

  /**
   * Flickr popcorn plug-in
   * Appends a users Flickr images to an element on the page.
   * Options parameter will need a start, end, target and userid or username and api_key.
   * Optional parameters are numberofimages, height, width, padding, and border
   * Start is the time that you want this plug-in to execute (in seconds)
   * End is the time that you want this plug-in to stop executing (in seconds)
   * Userid is the id of who's Flickr images you wish to show
   * Tags is a mutually exclusive list of image descriptor tags
   * Username is the username of who's Flickr images you wish to show
   *  using both userid and username is redundant
   *  an api_key is required when using username
   * Apikey is your own api key provided by Flickr
   * Target is the id of the document element that the images are
   *  appended to, this target element must exist on the DOM
   * Numberofimages specify the number of images to retreive from flickr, defaults to 4
   * Height the height of the image, defaults to '50px'
   * Width the width of the image, defaults to '50px'
   * Padding number of pixels between images, defaults to '5px'
   * Border border size in pixels around images, defaults to '0px'
   *
   * @param {Object} options
   *
   * Example:
     var p = Popcorn('#video')
        .flickr({
          start:          5,                 // seconds, mandatory
          end:            15,                // seconds, mandatory
          userid:         '35034346917@N01', // optional
          tags:           'dogs,cats',       // optional
          numberofimages: '8',               // optional
          height:         '50px',            // optional
          width:          '50px',            // optional
          padding:        '5px',             // optional
          border:         '0px',             // optional
          target:         'flickrdiv'        // mandatory
        } )
   *
   */

  var idx = 0;

  Popcorn.plugin( "flickr" , function( options ) {
    var containerDiv,
        target = document.getElementById( options.target ),
        _userid,
        _uri,
        _link,
        _image,
        _count = options.numberofimages || 4,
        _height = options.height || "50px",
        _width = options.width || "50px",
        _padding = options.padding || "5px",
        _border = options.border || "0px";

    // create a new div this way anything in the target div is left intact
    // this is later populated with Flickr images
    containerDiv = document.createElement( "div" );
    containerDiv.id = "flickr" + idx;
    containerDiv.style.width = "100%";
    containerDiv.style.height = "100%";
    containerDiv.style.display = "none";
    idx++;

    target && target.appendChild( containerDiv );

    // get the userid from Flickr API by using the username and apikey
    var isUserIDReady = function() {
      if ( !_userid ) {

        _uri  = "http://api.flickr.com/services/rest/?method=flickr.people.findByUsername&";
        _uri += "username=" + options.username + "&api_key=" + options.apikey + "&format=json&jsoncallback=flickr";
        Popcorn.getJSONP( _uri, function( data ) {
          _userid = data.user.nsid;
          getFlickrData();
        });

      } else {

        setTimeout(function () {
          isUserIDReady();
        }, 5 );
      }
    };

    // get the photos from Flickr API by using the user_id and/or tags
    var getFlickrData = function() {

      _uri  = "http://api.flickr.com/services/feeds/photos_public.gne?";

      if ( _userid ) {
        _uri += "id=" + _userid + "&";
      }
      if ( options.tags ) {
        _uri += "tags=" + options.tags + "&";
      }

      _uri += "lang=en-us&format=json&jsoncallback=flickr";

      Popcorn.xhr.getJSONP( _uri, function( data ) {

        var fragment = document.createElement( "div" );

        fragment.innerHTML = "<p style='padding:" + _padding + ";'>" + data.title + "<p/>";

        Popcorn.forEach( data.items, function ( item, i ) {
          if ( i < _count ) {

            _link = document.createElement( "a" );
            _link.setAttribute( "href", item.link );
            _link.setAttribute( "target", "_blank" );
            _image = document.createElement( "img" );
            _image.setAttribute( "src", item.media.m );
            _image.setAttribute( "height",_height );
            _image.setAttribute( "width", _width );
            _image.setAttribute( "style", "border:" + _border + ";padding:" + _padding );
            _link.appendChild( _image );
            fragment.appendChild( _link );

          } else {

            return false;
          }
        });

        containerDiv.appendChild( fragment );
      });
    };

    if ( options.username && options.apikey ) {
      isUserIDReady();
    }
    else {
      _userid = options.userid;
      getFlickrData();
    }

    options.toString = function() {
      return options.tags || options.username || "Flickr";
    };

    return {
      /**
       * @member flickr
       * The start function will be executed when the currentTime
       * of the video reaches the start time provided by the
       * options variable
       */
      start: function( event, options ) {
        containerDiv.style.display = "inline";
      },
      /**
       * @member flickr
       * The end function will be executed when the currentTime
       * of the video reaches the end time provided by the
       * options variable
       */
      end: function( event, options ) {
        containerDiv.style.display = "none";
      },
      _teardown: function( options ) {
        document.getElementById( options.target ) && document.getElementById( options.target ).removeChild( containerDiv );
      }
    };
  },
  {
    about: {
      name: "Popcorn Flickr Plugin",
      version: "0.2",
      author: "Scott Downe, Steven Weerdenburg, Annasob",
      website: "http://scottdowne.wordpress.com/"
    },
    options: {
      start: {
        elem: "input",
        type: "number",
        label: "Start"
      },
      end: {
        elem: "input",
        type: "number",
        label: "End"
      },
      userid: {
        elem: "input",
        type: "text",
        label: "User ID",
        optional: true
      },
      tags: {
        elem: "input",
        type: "text",
        label: "Tags"
      },
      username: {
        elem: "input",
        type: "text",
        label: "Username",
        optional: true
      },
      apikey: {
        elem: "input",
        type: "text",
        label: "API Key",
        optional: true
      },
      target: "flickr-container",
      height: {
        elem: "input",
        type: "text",
        label: "Height",
        "default": "50px",
        optional: true
      },
      width: {
        elem: "input",
        type: "text",
        label: "Width",
        "default": "50px",
        optional: true
      },
      padding: {
        elem: "input",
        type: "text",
        label: "Padding",
        optional: true
      },
      border: {
        elem: "input",
        type: "text",
        label: "Border",
        "default": "5px",
        optional: true
      },
      numberofimages: {
        elem: "input",
        type: "number",
        "default": 4,
        label: "Number of Images"
      }
    }
  });
})( Popcorn );
// PLUGIN: Footnote/Text

(function ( Popcorn ) {

  /**
   * Footnote popcorn plug-in
   * Adds text to an element on the page.
   * Options parameter will need a start, end, target and text.
   * Start is the time that you want this plug-in to execute
   * End is the time that you want this plug-in to stop executing
   * Text is the text that you want to appear in the target
   * Target is the id of the document element that the text needs to be
   * attached to, this target element must exist on the DOM
   *
   * @param {Object} options
   *
   * Example:
   *  var p = Popcorn('#video')
   *    .footnote({
   *      start: 5, // seconds
   *      end: 15, // seconds
   *      text: 'This video made exclusively for drumbeat.org',
   *      target: 'footnotediv'
   *    });
   **/

  Popcorn.plugin( "footnote", {

    manifest: {
      about: {
        name: "Popcorn Footnote Plugin",
        version: "0.2",
        author: "@annasob, @rwaldron",
        website: "annasob.wordpress.com"
      },
      options: {
        start: {
          elem: "input",
          type: "number",
          label: "Start"
        },
        end: {
          elem: "input",
          type: "number",
          label: "End"
        },
        text: {
          elem: "input",
          type: "text",
          label: "Text"
        },
        target: "footnote-container"
      }
    },

    _setup: function( options ) {

      var target = Popcorn.dom.find( options.target );

      options._container = document.createElement( "div" );
      options._container.style.display = "none";
      options._container.innerHTML  = options.text;

      target.appendChild( options._container );
    },

    /**
     * @member footnote
     * The start function will be executed when the currentTime
     * of the video  reaches the start time provided by the
     * options variable
     */
    start: function( event, options ){
      options._container.style.display = "inline";
    },

    /**
     * @member footnote
     * The end function will be executed when the currentTime
     * of the video  reaches the end time provided by the
     * options variable
     */
    end: function( event, options ){
      options._container.style.display = "none";
    },

    _teardown: function( options ) {
      var target = Popcorn.dom.find( options.target );
      if ( target ) {
        target.removeChild( options._container );
      }
    }

  });
})( Popcorn );
// PLUGIN: Google Feed
(function ( Popcorn ) {

  var i = 1,
      scriptLoaded  = false;

  /**
   * googlefeed popcorn plug-in
   * Adds a feed from the specified blog url at the target div
   * Options parameter will need a start, end, target, url and title
   * -Start is the time that you want this plug-in to execute
   * -End is the time that you want this plug-in to stop executing
   * -Target is the id of the DOM element that you want the map to appear in. This element must be in the DOM
   * -Url is the url of the blog's feed you are trying to access
   * -Title is the title of the blog you want displayed above the feed
   * -Orientation is the orientation of the blog, accepts either Horizontal or Vertical, defaults to Vertical
   * @param {Object} options
   *
   * Example:
    var p = Popcorn("#video")
      .googlefeed({
       start: 5, // seconds
       end: 15, // seconds
       target: "map",
       url: "http://zenit.senecac.on.ca/~chris.tyler/planet/rss20.xml",
       title: "Planet Feed"
    } )
  *
  */

  Popcorn.plugin( "googlefeed", function( options ) {

    var dynamicFeedLoad = function() {
      var dontLoad = false,
          k = 0,
          links = document.getElementsByTagName( "link" ),
          len = links.length,
          head = document.head || document.getElementsByTagName( "head" )[ 0 ],
          css = document.createElement( "link" ),
          resource = "//www.google.com/uds/solutions/dynamicfeed/gfdynamicfeedcontrol.";

      if ( !window.GFdynamicFeedControl ) {

        Popcorn.getScript( resource + "js", function() {
          scriptLoaded = true;
        });

      } else {
        scriptLoaded = true;
      }

      //  Checking if the css file is already included
      for ( ; k < len; k++ ){
        if ( links[ k ].href === resource + "css" ) {
          dontLoad = true;
        }
      }

      if ( !dontLoad ) {
        css.type = "text/css";
        css.rel = "stylesheet";
        css.href =  resource + "css";
        head.insertBefore( css, head.firstChild );
      }
    };

    if ( !window.google ) {

      Popcorn.getScript( "//www.google.com/jsapi", function() {

        google.load( "feeds", "1", {

          callback: function () {

            dynamicFeedLoad();
          }
        });
      });

    } else {
      dynamicFeedLoad();
    }

    // create a new div and append it to the parent div so nothing
    // that already exists in the parent div gets overwritten
    var newdiv = document.createElement( "div" ),
        target = document.getElementById( options.target ),
    initialize = function() {
      //ensure that the script has been loaded
      if ( !scriptLoaded ) {
        setTimeout( function () {
          initialize();
        }, 5 );
      } else {
        // Create the feed control using the user entered url and title
        options.feed = new GFdynamicFeedControl( options.url, newdiv, {
          vertical: options.orientation.toLowerCase() === "vertical" ? true : false,
          horizontal: options.orientation.toLowerCase() === "horizontal" ? true : false,
          title: options.title = options.title || "Blog"
        });
      }
    };

    // Default to vertical orientation if empty or incorrect input
    if( !options.orientation || ( options.orientation.toLowerCase() !== "vertical" &&
      options.orientation.toLowerCase() !== "horizontal" ) ) {
      options.orientation = "vertical";
    }

    newdiv.style.display = "none";
    newdiv.id = "_feed" + i;
    newdiv.style.width = "100%";
    newdiv.style.height = "100%";
    i++;

    target && target.appendChild( newdiv );

    initialize();

    options.toString = function() {
      return options.url || options._natives.manifest.options.url[ "default" ];
    };

    return {
      /**
       * @member webpage
       * The start function will be executed when the currentTime
       * of the video reaches the start time provided by the
       * options variable
       */
      start: function( event, options ){
        newdiv.setAttribute( "style", "display:inline" );
      },
      /**
       * @member webpage
       * The end function will be executed when the currentTime
       * of the video reaches the end time provided by the
       * options variable
       */
      end: function( event, options ){
        newdiv.setAttribute( "style", "display:none" );
      },
      _teardown: function( options ) {
        document.getElementById( options.target ) && document.getElementById( options.target ).removeChild( newdiv );
        delete options.feed;
      }
    };
  },
  {
    about: {
      name: "Popcorn Google Feed Plugin",
      version: "0.1",
      author: "David Seifried",
      website: "dseifried.wordpress.com"
    },
    options: {
      start: {
        elem: "input",
        type: "number",
        label: "Start"
      },
      end: {
        elem: "input",
        type: "number",
        label: "End"
      },
      target: "feed-container",
      url: {
        elem: "input",
        type: "url",
        label: "Feed URL",
        "default": "http://planet.mozilla.org/rss20.xml"
      },
      title: {
        elem: "input",
        type: "text",
        label: "Title",
        "default": "Planet Mozilla",
        optional: true
      },
      orientation: {
        elem: "select",
        options: [ "Vertical", "Horizontal" ],
        label: "Orientation",
        "default": "Vertical",
        optional: true
      }
    }
  });
})( Popcorn );

// PLUGIN: Google Maps
var googleCallback;
(function ( Popcorn ) {

  var i = 1,
    _mapFired = false,
    _mapLoaded = false,
    geocoder, loadMaps;
  //google api callback
  googleCallback = function ( data ) {
    // ensure all of the maps functions needed are loaded
    // before setting _maploaded to true
    if ( typeof google !== "undefined" && google.maps && google.maps.Geocoder && google.maps.LatLng ) {
      geocoder = new google.maps.Geocoder();
      Popcorn.getScript( "//maps.stamen.com/js/tile.stamen.js", function() {
        _mapLoaded = true;
      });
    } else {
      setTimeout(function () {
        googleCallback( data );
      }, 1);
    }
  };
  // function that loads the google api
  loadMaps = function () {
    // for some reason the Google Map API adds content to the body
    if ( document.body ) {
      _mapFired = true;
      Popcorn.getScript( "//maps.google.com/maps/api/js?sensor=false&callback=googleCallback" );
    } else {
      setTimeout(function () {
        loadMaps();
      }, 1);
    }
  };

  function buildMap( options, location, mapDiv ) {
    var type = options.type ? options.type.toUpperCase() : "HYBRID",
      layer;

    // See if we need to make a custom Stamen map layer
    if ( type === "STAMEN-WATERCOLOR" ||
         type === "STAMEN-TERRAIN"    ||
         type === "STAMEN-TONER" ) {
      // Stamen types are lowercase
      layer = type.replace("STAMEN-", "").toLowerCase();
    }

    var map = new google.maps.Map( mapDiv, {
      // If a custom layer was specified, use that, otherwise use type
      mapTypeId: layer ? layer : google.maps.MapTypeId[ type ],
      // Hide the layer selection UI
      mapTypeControlOptions: { mapTypeIds: [] }
    });

    if ( layer ) {
      map.mapTypes.set( layer, new google.maps.StamenMapType( layer ));
    }
    map.getDiv().style.display = "none";

    return map;
  }

  /**
   * googlemap popcorn plug-in
   * Adds a map to the target div centered on the location specified by the user
   * Options parameter will need a start, end, target, type, zoom, lat and lng, and location
   * -Start is the time that you want this plug-in to execute
   * -End is the time that you want this plug-in to stop executing
   * -Target is the id of the DOM element that you want the map to appear in. This element must be in the DOM
   * -Type [optional] either: HYBRID (default), ROADMAP, SATELLITE, TERRAIN, STREETVIEW, or one of the
   *                          Stamen custom map types (http://http://maps.stamen.com): STAMEN-TONER,
   *                          STAMEN-WATERCOLOR, or STAMEN-TERRAIN.
   * -Zoom [optional] defaults to 0
   * -Heading [optional] STREETVIEW orientation of camera in degrees relative to true north (0 north, 90 true east, ect)
   * -Pitch [optional] STREETVIEW vertical orientation of the camera (between 1 and 3 is recommended)
   * -Lat and Lng: the coordinates of the map must be present if location is not specified.
   * -Height [optional] the height of the map, in "px" or "%". Defaults to "100%".
   * -Width [optional] the width of the map, in "px" or "%". Defaults to "100%".
   * -Location: the adress you want the map to display, must be present if lat and lng are not specified.
   * Note: using location requires extra loading time, also not specifying both lat/lng and location will
   * cause and error.
   *
   * Tweening works using the following specifications:
   * -location is the start point when using an auto generated route
   * -tween when used in this context is a string which specifies the end location for your route
   * Note that both location and tween must be present when using an auto generated route, or the map will not tween
   * -interval is the speed in which the tween will be executed, a reasonable time is 1000 ( time in milliseconds )
   * Heading, Zoom, and Pitch streetview values are also used in tweening with the autogenerated route
   *
   * -tween is an array of objects, each containing data for one frame of a tween
   * -position is an object with has two paramaters, lat and lng, both which are mandatory for a tween to work
   * -pov is an object which houses heading, pitch, and zoom paramters, which are all optional, if undefined, these values default to 0
   * -interval is the speed in which the tween will be executed, a reasonable time is 1000 ( time in milliseconds )
   *
   * @param {Object} options
   *
   * Example:
   var p = Popcorn("#video")
   .googlemap({
   start: 5, // seconds
   end: 15, // seconds
   type: "ROADMAP",
   target: "map",
   lat: 43.665429,
   lng: -79.403323
   } )
   *
   */
  Popcorn.plugin( "googlemap", function ( options ) {
    var newdiv, map, location,
        target = document.getElementById( options.target );

    options.type = options.type || "ROADMAP";
    options.zoom = options.zoom || 1;
    options.lat = options.lat || 0;
    options.lng = options.lng || 0;

    // if this is the firest time running the plugins
    // call the function that gets the sctipt
    if ( !_mapFired ) {
      loadMaps();
    }

    // create a new div this way anything in the target div is left intact
    // this is later passed on to the maps api
    newdiv = document.createElement( "div" );
    newdiv.id = "actualmap" + i;
    newdiv.style.width = options.width || "100%";

    // height is a little more complicated than width.
    if ( options.height ) {
      newdiv.style.height = options.height;
    } else if ( target && target.clientHeight ) {
      newdiv.style.height = target.clientHeight + "px";
    } else {
      newdiv.style.height = "100%";
    }

    i++;

    target && target.appendChild( newdiv );

    // ensure that google maps and its functions are loaded
    // before setting up the map parameters
    var isMapReady = function () {
      if ( _mapLoaded ) {
        if ( newdiv ) {
          if ( options.location ) {
            // calls an anonymous google function called on separate thread
            geocoder.geocode({
              "address": options.location
            }, function ( results, status ) {
              // second check for newdiv since it could have disappeared before
              // this callback is actual run
              if ( newdiv && status === google.maps.GeocoderStatus.OK ) {
                options.lat = results[ 0 ].geometry.location.lat();
                options.lng = results[ 0 ].geometry.location.lng();
                location = new google.maps.LatLng( options.lat, options.lng );
                map = buildMap( options, location, newdiv );
              }
            });
          } else {
            location = new google.maps.LatLng( options.lat, options.lng );
            map = buildMap( options, location, newdiv );
          }
        }
      } else {
          setTimeout(function () {
            isMapReady();
          }, 5);
        }
      };

    isMapReady();

    options.toString = function() {
      return options.location || ( ( options.lat && options.lng ) ? options.lat + ", " + options.lng : options._natives.manifest.options.location[ "default" ] );
    };

    return {
      /**
       * @member webpage
       * The start function will be executed when the currentTime
       * of the video reaches the start time provided by the
       * options variable
       */
      start: function( event, options ) {
        var that = this,
            sView;

        // ensure the map has been initialized in the setup function above
        var isMapSetup = function() {
          if ( map ) {
            options._map = map;

            map.getDiv().style.display = "block";
            // reset the location and zoom just in case the user plaid with the map
            google.maps.event.trigger( map, "resize" );
            map.setCenter( location );

            // make sure options.zoom is a number
            if ( options.zoom && typeof options.zoom !== "number" ) {
              options.zoom = +options.zoom;
            }

            map.setZoom( options.zoom );

            //Make sure heading is a number
            if ( options.heading && typeof options.heading !== "number" ) {
              options.heading = +options.heading;
            }
            //Make sure pitch is a number
            if ( options.pitch && typeof options.pitch !== "number" ) {
              options.pitch = +options.pitch;
            }

            if ( options.type === "STREETVIEW" ) {
              // Switch this map into streeview mode
              map.setStreetView(
              // Pass a new StreetViewPanorama instance into our map

                sView = new google.maps.StreetViewPanorama( newdiv, {
                  position: location,
                  pov: {
                    heading: options.heading = options.heading || 0,
                    pitch: options.pitch = options.pitch || 0,
                    zoom: options.zoom
                  }
                })
              );

              //  Function to handle tweening using a set timeout
              var tween = function( rM, t ) {

                var computeHeading = google.maps.geometry.spherical.computeHeading;
                setTimeout(function() {

                  var current_time = that.media.currentTime;

                  //  Checks whether this is a generated route or not
                  if ( typeof options.tween === "object" ) {

                    for ( var i = 0, m = rM.length; i < m; i++ ) {

                      var waypoint = rM[ i ];

                      //  Checks if this position along the tween should be displayed or not
                      if ( current_time >= ( waypoint.interval * ( i + 1 ) ) / 1000 &&
                         ( current_time <= ( waypoint.interval * ( i + 2 ) ) / 1000 ||
                           current_time >= waypoint.interval * ( m ) / 1000 ) ) {

                        sView3.setPosition( new google.maps.LatLng( waypoint.position.lat, waypoint.position.lng ) );

                        sView3.setPov({
                          heading: waypoint.pov.heading || computeHeading( waypoint, rM[ i + 1 ] ) || 0,
                          zoom: waypoint.pov.zoom || 0,
                          pitch: waypoint.pov.pitch || 0
                        });
                      }
                    }

                    //  Calls the tween function again at the interval set by the user
                    tween( rM, rM[ 0 ].interval );
                  } else {

                    for ( var k = 0, l = rM.length; k < l; k++ ) {

                      var interval = options.interval;

                      if( current_time >= (interval * ( k + 1 ) ) / 1000 &&
                        ( current_time <= (interval * ( k + 2 ) ) / 1000 ||
                          current_time >= interval * ( l ) / 1000 ) ) {

                        sView2.setPov({
                          heading: computeHeading( rM[ k ], rM[ k + 1 ] ) || 0,
                          zoom: options.zoom,
                          pitch: options.pitch || 0
                        });
                        sView2.setPosition( checkpoints[ k ] );
                      }
                    }

                    tween( checkpoints, options.interval );
                  }
                }, t );
              };

              //  Determines if we should use hardcoded values ( using options.tween ),
              //  or if we should use a start and end location and let google generate
              //  the route for us
              if ( options.location && typeof options.tween === "string" ) {

              //  Creating another variable to hold the streetview map for tweening,
              //  Doing this because if there was more then one streetview map, the tweening would sometimes appear in other maps
              var sView2 = sView;

                //  Create an array to store all the lat/lang values along our route
                var checkpoints = [];

                //  Creates a new direction service, later used to create a route
                var directionsService = new google.maps.DirectionsService();

                //  Creates a new direction renderer using the current map
                //  This enables us to access all of the route data that is returned to us
                var directionsDisplay = new google.maps.DirectionsRenderer( sView2 );

                var request = {
                  origin: options.location,
                  destination: options.tween,
                  travelMode: google.maps.TravelMode.DRIVING
                };

                //  Create the route using the direction service and renderer
                directionsService.route( request, function( response, status ) {

                  if ( status == google.maps.DirectionsStatus.OK ) {
                    directionsDisplay.setDirections( response );
                    showSteps( response, that );
                  }

                });

                var showSteps = function ( directionResult, that ) {

                  //  Push new google map lat and lng values into an array from our list of lat and lng values
                  var routes = directionResult.routes[ 0 ].overview_path;
                  for ( var j = 0, k = routes.length; j < k; j++ ) {
                    checkpoints.push( new google.maps.LatLng( routes[ j ].lat(), routes[ j ].lng() ) );
                  }

                  //  Check to make sure the interval exists, if not, set to a default of 1000
                  options.interval = options.interval || 1000;
                  tween( checkpoints, 10 );

                };
              } else if ( typeof options.tween === "object" ) {

                //  Same as the above to stop streetview maps from overflowing into one another
                var sView3 = sView;

                for ( var i = 0, l = options.tween.length; i < l; i++ ) {

                  //  Make sure interval exists, if not, set to 1000
                  options.tween[ i ].interval = options.tween[ i ].interval || 1000;
                  tween( options.tween, 10 );
                }
              }
            }

            if ( options.onmaploaded ) {
              options.onmaploaded( options, map );
            }

          } else {
            setTimeout(function () {
              isMapSetup();
            }, 13);
          }

        };
        isMapSetup();
      },
      /**
       * @member webpage
       * The end function will be executed when the currentTime
       * of the video reaches the end time provided by the
       * options variable
       */
      end: function ( event, options ) {
        // if the map exists hide it do not delete the map just in
        // case the user seeks back to time b/w start and end
        if ( map ) {
          map.getDiv().style.display = "none";
        }
      },
      _teardown: function ( options ) {

        var target = document.getElementById( options.target );

        // the map must be manually removed
        target && target.removeChild( newdiv );
        newdiv = map = location = null;

        options._map = null;
      }
    };
  }, {
    about: {
      name: "Popcorn Google Map Plugin",
      version: "0.1",
      author: "@annasob",
      website: "annasob.wordpress.com"
    },
    options: {
      start: {
        elem: "input",
        type: "start",
        label: "Start"
      },
      end: {
        elem: "input",
        type: "start",
        label: "End"
      },
      target: "map-container",
      type: {
        elem: "select",
        options: [ "ROADMAP", "SATELLITE", "STREETVIEW", "HYBRID", "TERRAIN", "STAMEN-WATERCOLOR", "STAMEN-TERRAIN", "STAMEN-TONER" ],
        label: "Map Type",
        optional: true
      },
      zoom: {
        elem: "input",
        type: "text",
        label: "Zoom",
        "default": 0,
        optional: true
      },
      lat: {
        elem: "input",
        type: "text",
        label: "Lat",
        optional: true
      },
      lng: {
        elem: "input",
        type: "text",
        label: "Lng",
        optional: true
      },
      location: {
        elem: "input",
        type: "text",
        label: "Location",
        "default": "Toronto, Ontario, Canada"
      },
      heading: {
        elem: "input",
        type: "text",
        label: "Heading",
        "default": 0,
        optional: true
      },
      pitch: {
        elem: "input",
        type: "text",
        label: "Pitch",
        "default": 1,
        optional: true
      }
    }
  });
})( Popcorn );

// PLUGIN: IMAGE

(function ( Popcorn ) {

/**
 * Images popcorn plug-in
 * Shows an image element
 * Options parameter will need a start, end, href, target and src.
 * Start is the time that you want this plug-in to execute
 * End is the time that you want this plug-in to stop executing
 * href is the url of the destination of a anchor - optional
 * Target is the id of the document element that the iframe needs to be attached to,
 * this target element must exist on the DOM
 * Src is the url of the image that you want to display
 * text is the overlayed text on the image - optional
 *
 * @param {Object} options
 *
 * Example:
   var p = Popcorn('#video')
      .image({
        start: 5, // seconds
        end: 15, // seconds
        href: 'http://www.drumbeat.org/',
        src: 'http://www.drumbeat.org/sites/default/files/domain-2/drumbeat_logo.png',
        text: 'DRUMBEAT',
        target: 'imagediv'
      } )
 *
 */

  var VIDEO_OVERLAY_Z = 2000,
      CHECK_INTERVAL_DURATION = 10;

  function trackMediaElement( mediaElement ) {
    var checkInterval = -1,
        container = document.createElement( "div" ),
        videoZ = getComputedStyle( mediaElement ).zIndex;

    container.setAttribute( "data-popcorn-helper-container", true );

    container.style.position = "absolute";

    if ( !isNaN( videoZ ) ) {
      container.style.zIndex = videoZ + 1;
    }
    else {
      container.style.zIndex = VIDEO_OVERLAY_Z;
    }

    document.body.appendChild( container );

    function check() {
      var mediaRect = mediaElement.getBoundingClientRect(),
          containerRect = container.getBoundingClientRect();

      if ( containerRect.left !== mediaRect.left ) {
        container.style.left = mediaRect.left + "px";
      }
      if ( containerRect.top !== mediaRect.top ) {
        container.style.top = mediaRect.top + "px";
      }
    }

    return {
      element: container,
      start: function() {
        checkInterval = setInterval( check, CHECK_INTERVAL_DURATION );
      },
      stop: function() {
        clearInterval( checkInterval );
        checkInterval = -1;
      },
      destroy: function() {
        document.body.removeChild( container );
        if ( checkInterval !== -1 ) {
          clearInterval( checkInterval );
        }
      }
    };
  }

  Popcorn.plugin( "image", {
      manifest: {
        about: {
          name: "Popcorn image Plugin",
          version: "0.1",
          author: "Scott Downe",
          website: "http://scottdowne.wordpress.com/"
        },
        options: {
          start: {
            elem: "input",
            type: "number",
            label: "Start"
          },
          end: {
            elem: "input",
            type: "number",
            label: "End"
          },
          src: {
            elem: "input",
            type: "url",
            label: "Image URL",
            "default": "http://mozillapopcorn.org/wp-content/themes/popcorn/images/for_developers.png"
          },
          href: {
            elem: "input",
            type: "url",
            label: "Link",
            "default": "http://mozillapopcorn.org/wp-content/themes/popcorn/images/for_developers.png",
            optional: true
          },
          target: "image-container",
          text: {
            elem: "input",
            type: "text",
            label: "Caption",
            "default": "Popcorn.js",
            optional: true
          }
        }
      },
      _setup: function( options ) {
        var img = document.createElement( "img" ),
            target = document.getElementById( options.target );

        options.anchor = document.createElement( "a" );
        options.anchor.style.position = "relative";
        options.anchor.style.textDecoration = "none";
        options.anchor.style.display = "none";

        // add the widget's div to the target div.
        // if target is <video> or <audio>, create a container and routinely 
        // update its size/position to be that of the media
        if ( target ) {
          if ( [ "VIDEO", "AUDIO" ].indexOf( target.nodeName ) > -1 ) {
            options.trackedContainer = trackMediaElement( target );
            options.trackedContainer.element.appendChild( options.anchor );
          }
          else {
            target && target.appendChild( options.anchor );
          }          
        }

        img.addEventListener( "load", function() {

          // borders look really bad, if someone wants it they can put it on their div target
          img.style.borderStyle = "none";

          options.anchor.href = options.href || options.src || "#";
          options.anchor.target = "_blank";

          var fontHeight, divText;

          img.style.height = target.style.height;
          img.style.width = target.style.width;

          options.anchor.appendChild( img );

          // If display text was provided, display it:
          if ( options.text ) {
            fontHeight = ( img.height / 12 ) + "px";
            divText = document.createElement( "div" );

            Popcorn.extend( divText.style, {
              color: "black",
              fontSize: fontHeight,
              fontWeight: "bold",
              position: "relative",
              textAlign: "center",
              width: img.style.width || img.width + "px",
              zIndex: "10"
            });

            divText.innerHTML = options.text || "";

            divText.style.top = ( ( img.style.height.replace( "px", "" ) || img.height ) / 2 ) - ( divText.offsetHeight / 2 ) + "px";
            options.anchor.insertBefore( divText, img );
          }
        }, false );

        img.src = options.src;

        options.toString = function() {
          var string = options.src || options._natives.manifest.options.src[ "default" ],
              match = string.replace( /.*\//g, "" );
          return match.length ? match : string;
        };
      },

      /**
       * @member image
       * The start function will be executed when the currentTime
       * of the video  reaches the start time provided by the
       * options variable
       */
      start: function( event, options ) {
        options.anchor.style.display = "inline";
        if ( options.trackedContainer ) {
          options.trackedContainer.start();
        }
      },
      /**
       * @member image
       * The end function will be executed when the currentTime
       * of the video  reaches the end time provided by the
       * options variable
       */
      end: function( event, options ) {
        options.anchor.style.display = "none";
        if ( options.trackedContainer ) {
          options.trackedContainer.stop();
        }
      },
      _teardown: function( options ) {
        if ( options.trackedContainer ) {
          options.trackedContainer.destroy();
        }
        else if ( options.anchor.parentNode ) {
          options.anchor.parentNode.removeChild( options.anchor );
        }
      }
  });
})( Popcorn );
// PLUGIN: mediaspawner
/**
  * mediaspawner Popcorn Plugin.
  * Adds Video/Audio to the page using Popcorns players
  * Start is the time that you want this plug-in to execute
  * End is the time that you want this plug-in to stop executing
  *
  * @param {HTML} options
  *
  * Example:
    var p = Popcorn('#video')
      .mediaspawner( {
        source: "http://www.youtube.com/watch?v=bUB1L3zGVvc",
        target: "mediaspawnerdiv",
        start: 1,
        end: 10,
        caption: "This is a test. We are assuming conrol. We are assuming control."
      })
  *
  */
(function ( Popcorn, global ) {
  var PLAYER_URL = "http://popcornjs.org/code/modules/player/popcorn.player.js",
      urlRegex = /(?:http:\/\/www\.|http:\/\/|www\.|\.|^)(youtu|vimeo|soundcloud|baseplayer)/,
      forEachPlayer,
      playerTypeLoading = {},
      playerTypesLoaded = {
        "vimeo": false,
        "youtube": false,
        "soundcloud": false,
        "module": false
      };

  Object.defineProperty( playerTypeLoading, forEachPlayer, {
    get: function() {
      return playerTypesLoaded[ forEachPlayer ];
    },
    set: function( val ) {
      playerTypesLoaded[ forEachPlayer ] = val;
    }
  });

  Popcorn.plugin( "mediaspawner", {
    manifest: {
      about: {
        name: "Popcorn Media Spawner Plugin",
        version: "0.1",
        author: "Matthew Schranz, @mjschranz",
        website: "mschranz.wordpress.com"
      },
      options: {
        source: {
          elem: "input",
          type: "text",
          label: "Media Source",
          "default": "http://www.youtube.com/watch?v=CXDstfD9eJ0"
        },
        caption: {
          elem: "input",
          type: "text",
          label: "Media Caption",
          "default": "Popcorn Popping",
          optional: true
        },
        target: "mediaspawner-container",
        start: {
          elem: "input",
          type: "number",
          label: "Start"
        },
        end: {
          elem: "input",
          type: "number",
          label: "End"
        },
        autoplay: {
          elem: "input",
          type: "checkbox",
          label: "Autoplay Video",
          optional: true
        },
        width: {
          elem: "input",
          type: "number",
          label: "Media Width",
          "default": 400,
          units: "px",
          optional: true
        },
        height: {
          elem: "input",
          type: "number",
          label: "Media Height",
          "default": 200,
          units: "px",
          optional: true
        }
      }
    },
    _setup: function( options ) {
      var target = document.getElementById( options.target ) || {},
          mediaType,
          container,
          capContainer,
          regexResult;

      regexResult = urlRegex.exec( options.source );
      if ( regexResult ) {
        mediaType = regexResult[ 1 ];
        // our regex only handles youtu ( incase the url looks something like youtu.be )
        if ( mediaType === "youtu" ) {
          mediaType = "youtube";
        }
      }
      else {
        // if the regex didn't return anything we know it's an HTML5 source
        mediaType = "HTML5";
      }

      // Store Reference to Type for use in end
      options._type = mediaType;

      // Create separate container for plugin
      options._container = document.createElement( "div" );
      container = options._container;
      container.id = "mediaSpawnerdiv-" + Popcorn.guid();

      // Default width and height of media
      options.width = options.width || 400;
      options.height = options.height || 200;

      // Captions now need to be in their own container, due to the problem with flash players
      // described in start/end
      if ( options.caption ) {
        capContainer = document.createElement( "div" );
        capContainer.innerHTML = options.caption;
        capContainer.style.display = "none";
        options._capCont = capContainer;
        container.appendChild( capContainer );
      }

      target && target.appendChild( container );

      function constructMedia(){

        function checkPlayerTypeLoaded() {
          if ( mediaType !== "HTML5" && !window.Popcorn[ mediaType ] ) {
            setTimeout( function() {
              checkPlayerTypeLoaded();
            }, 300 );
          } else {
            options.id = options._container.id;
            // Set the width/height of the container before calling Popcorn.smart
            // Allows youtube to pickup on the specified height an create the player
            // with specified dimensions
            options._container.style.width = options.width + "px";
            options._container.style.height = options.height + "px";
            options.popcorn = Popcorn.smart( "#" + options.id, options.source );

            if ( mediaType === "HTML5" ) {
              options.popcorn.controls( true );
            }
            
            // Set them to 0 now so it is hidden
            options._container.style.width = "0px";
            options._container.style.height = "0px";
            options._container.style.visibility = "hidden";
            options._container.style.overflow = "hidden";
          }
        }

        if ( mediaType !== "HTML5" && !window.Popcorn[ mediaType ] && !playerTypeLoading[ mediaType ] ) {
          playerTypeLoading[ mediaType ] = true;
          Popcorn.getScript( "http://popcornjs.org/code/players/" + mediaType + "/popcorn." + mediaType + ".js", function() {
            checkPlayerTypeLoaded();
          });
        }
        else {
          checkPlayerTypeLoaded();
        }

      }

      // If Player script needed to be loaded, keep checking until it is and then fire readycallback
      function isPlayerReady() {
        if ( !window.Popcorn.player ) {
          setTimeout( function () {
            isPlayerReady();
          }, 300 );
        } else {
          constructMedia();
        }
      }

      // If player script isn't present, retrieve script
      if ( !window.Popcorn.player && !playerTypeLoading.module ) {
        playerTypeLoading.module = true;
        Popcorn.getScript( PLAYER_URL, isPlayerReady );
      } else {
        isPlayerReady();
      }

      options.toString = function() {
        return options.source || options._natives.manifest.options.source[ "default" ];
      };
    },
    start: function( event, options ) {
      if( options._capCont ) {
        options._capCont.style.display = "";
      }

      /* Using this style for Start/End is required because of the flash players
       * Without it on end an internal cleanup is called, causing the flash players
       * to be out of sync with Popcorn, as they are then rebuilt.
       */
      options._container.style.width = options.width + "px";
      options._container.style.height = options.height + "px";
      options._container.style.visibility = "visible";
      options._container.style.overflow = "visible";

      if ( options.autoplay ) {
        options.popcorn.play();
      }
    },
    end: function( event, options ) {
      if( options._capCont ) {
        options._capCont.style.display = "none";
      }

      /* Using this style for Start/End is required because of the flash players
       * Without it on end an internal cleanup is called, causing the flash players
       * to be out of sync with Popcorn, as they are then rebuilt.
       */
      options._container.style.width = "0px";
      options._container.style.height = "0px";
      options._container.style.visibility = "hidden";
      options._container.style.overflow = "hidden";

      // Pause all popcorn instances on exit
      options.popcorn.pause();

    },
    _teardown: function( options ) {
      if ( options.popcorn && options.popcorn.destory ) {
        options.popcorn.destroy();
      }
      document.getElementById( options.target ) && document.getElementById( options.target ).removeChild( options._container );
    }
  });
})( Popcorn, this );
// PLUGIN: Mustache

(function ( Popcorn ) {

  /**
   * Mustache Popcorn Plug-in
   *
   * Adds the ability to render JSON using templates via the Mustache templating library.
   *
   * @param {Object} options
   *
   * Required parameters: start, end, template, data, and target.
   * Optional parameter: static.
   *
   *   start: the time in seconds when the mustache template should be rendered
   *          in the target div.
   *
   *   end: the time in seconds when the rendered mustache template should be
   *        removed from the target div.
   *
   *   target: a String -- the target div's id.
   *
   *   template: the mustache template for the plugin to use when rendering.  This can be
   *             a String containing the template, or a Function that returns the template's
   *             String.
   *
   *   data: the data to be rendered using the mustache template.  This can be a JSON String,
   *         a JavaScript Object literal, or a Function returning a String or Literal.
   *
   *   dynamic: an optional argument indicating that the template and json data are dynamic
   *            and need to be loaded dynamically on every use.  Defaults to True.
   *
   * Example:
     var p = Popcorn('#video')

        // Example using template and JSON strings.
        .mustache({
          start: 5, // seconds
          end:  15,  // seconds
          target: 'mustache',
          template: '<h1>{{header}}</h1>'                         +
                    '{{#bug}}'                                    +
                    '{{/bug}}'                                    +
                    ''                                            +
                    '{{#items}}'                                  +
                    '  {{#first}}'                                +
                    '    <li><strong>{{name}}</strong></li>'      +
                    '  {{/first}}'                                +
                    '  {{#link}}'                                 +
                    '    <li><a href="{{url}}">{{name}}</a></li>' +
                    '  {{/link}}'                                 +
                    '{{/items}}'                                  +
                    ''                                            +
                    '{{#empty}}'                                  +
                    '  <p>The list is empty.</p>'                 +
                    '{{/empty}}'                                  ,

          data:     '{'                                                        +
                    '  "header": "Colors", '                                   +
                    '  "items": [ '                                            +
                    '      {"name": "red", "first": true, "url": "#Red"}, '    +
                    '      {"name": "green", "link": true, "url": "#Green"}, ' +
                    '      {"name": "blue", "link": true, "url": "#Blue"} '    +
                    '  ],'                                                     +
                    '  'empty': false'                                         +
                    '}',
          dynamic: false // The json is not going to change, load it early.
        } )

        // Example showing Functions instead of Strings.
        .mustache({
          start: 20,  // seconds
          end:   25,  // seconds
          target: 'mustache',
          template: function(instance, options) {
                      var template = // load your template file here...
                      return template;
                    },
          data:     function(instance, options) {
                      var json = // load your json here...
                      return json;
                    }
        } );
  *
  */

  Popcorn.plugin( "mustache" , function( options ){

    var getData, data, getTemplate, template;

    Popcorn.getScript( "http://mustache.github.com/extras/mustache.js" );

    var shouldReload = !!options.dynamic,
        typeOfTemplate = typeof options.template,
        typeOfData = typeof options.data,
        target = document.getElementById( options.target );

    options.container = target || document.createElement( "div" );

    if ( typeOfTemplate === "function" ) {
      if ( !shouldReload ) {
        template = options.template( options );
      } else {
        getTemplate = options.template;
      }
    } else if ( typeOfTemplate === "string" ) {
      template = options.template;
    } else {
      template = "";
    }

    if ( typeOfData === "function" ) {
      if ( !shouldReload ) {
        data = options.data( options );
      } else {
        getData = options.data;
      }
    } else if ( typeOfData === "string" ) {
      data = JSON.parse( options.data );
    } else if ( typeOfData === "object" ) {
      data = options.data;
    } else {
      data = "";
    }

    return {
      start: function( event, options ) {

        var interval = function() {

          if( !window.Mustache ) {
            setTimeout( function() {
              interval();
            }, 10 );
          } else {

            // if dynamic, freshen json data on every call to start, just in case.
            if ( getData ) {
              data = getData( options );
            }

            if ( getTemplate ) {
              template = getTemplate( options );
            }

            var html = Mustache.to_html( template,
                                         data
                                       ).replace( /^\s*/mg, "" );
            options.container.innerHTML = html;
          }
        };

        interval();

      },

      end: function( event, options ) {
        options.container.innerHTML = "";
      },
      _teardown: function( options ) {
        getData = data = getTemplate = template = null;
      }
    };
  },
  {
    about: {
      name: "Popcorn Mustache Plugin",
      version: "0.1",
      author: "David Humphrey (@humphd)",
      website: "http://vocamus.net/dave"
    },
    options: {
      start: {
        elem: "input",
        type: "number",
        label: "Start"
      },
      end: {
        elem: "input",
        type: "number",
        label: "End"
      },
      target: "mustache-container",
      template: {
        elem: "input",
        type: "text",
        label: "Template"
      },
      data: {
        elem: "input",
        type: "text",
        label: "Data"
      },
      dynamic: {
        elem: "input",
        type: "checkbox",
        label: "Dynamic",
        "default": true
      }
    }
  });
})( Popcorn );
// PLUGIN: OPENMAP
( function ( Popcorn ) {

  /**
   * openmap popcorn plug-in
   * Adds an OpenLayers map and open map tiles (OpenStreetMap [default], NASA WorldWind, or USGS Topographic)
   * Based on the googlemap popcorn plug-in. No StreetView support
   * Options parameter will need a start, end, target, type, zoom, lat and lng
   * -Start is the time that you want this plug-in to execute
   * -End is the time that you want this plug-in to stop executing
   * -Target is the id of the DOM element that you want the map to appear in. This element must be in the DOM
   * -Type [optional] either: ROADMAP (OpenStreetMap), SATELLITE (NASA WorldWind / LandSat), or TERRAIN (USGS).
   *                          The Stamen custom map types can also be used (http://maps.stamen.com): STAMEN-TONER,
   *                          STAMEN-TERRAIN, or STAMEN-WATERCOLOR.
   * -Zoom [optional] defaults to 2
   * -Lat and Lng are the coordinates of the map if location is not named
   * -Location is a name of a place to center the map, geocoded to coordinates using TinyGeocoder.com
   * -Markers [optional] is an array of map marker objects, with the following properties:
   * --Icon is the URL of a map marker image
   * --Size [optional] is the radius in pixels of the scaled marker image (default is 14)
   * --Text [optional] is the HTML content of the map marker -- if your popcorn instance is named 'popped', use <script>popped.currentTime(10);</script> to control the video
   * --Lat and Lng are coordinates of the map marker if location is not specified
   * --Location is a name of a place for the map marker, geocoded to coordinates using TinyGeocoder.com
   *  Note: using location requires extra loading time, also not specifying both lat/lng and location will
   * cause a JavaScript error.
   * @param {Object} options
   *
   * Example:
     var p = Popcorn( '#video' )
        .openmap({
          start: 5,
          end: 15,
          type: 'ROADMAP',
          target: 'map',
          lat: 43.665429,
          lng: -79.403323
        })
   *
   */
  var newdiv,
      i = 1;

  function toggle( container, display ) {
    if ( container.map ) {
      container.map.div.style.display = display;
      return;
    }

    setTimeout(function() {
      toggle( container, display );
    }, 10 );
  }

  Popcorn.plugin( "openmap", function( options ){
    var newdiv,
        centerlonlat,
        projection,
        displayProjection,
        pointLayer,
        selectControl,
        popup,
        isGeoReady,
        target = document.getElementById( options.target );

    // create a new div within the target div
    // this is later passed on to the maps api
    newdiv = document.createElement( "div" );
    newdiv.id = "openmapdiv" + i;
    newdiv.style.width = "100%";
    newdiv.style.height = "100%";
    i++;

    target && target.appendChild( newdiv );

    // callback function fires when the script is run
    isGeoReady = function() {
      if ( ! ( window.OpenLayers && window.OpenLayers.Layer.Stamen ) ) {
        setTimeout(function() {
          isGeoReady();
        }, 50);
      } else {
        if ( options.location ) {
          // set a dummy center at start
          location = new OpenLayers.LonLat( 0, 0 );
          // query TinyGeocoder and re-center in callback
          Popcorn.getJSONP(
            "//tinygeocoder.com/create-api.php?q=" + options.location + "&callback=jsonp",
            function( latlng ) {
              centerlonlat = new OpenLayers.LonLat( latlng[ 1 ], latlng[ 0 ] );
            }
          );
        } else {
          centerlonlat = new OpenLayers.LonLat( options.lng, options.lat );
        }

        options.type = options.type || "ROADMAP";
        switch( options.type ) {
          case "SATELLITE" :
            // add NASA WorldWind / LANDSAT map
            options.map = new OpenLayers.Map({
              div: newdiv,
              maxResolution: 0.28125,
              tileSize: new OpenLayers.Size( 512, 512 )
            });
            var worldwind = new OpenLayers.Layer.WorldWind(
              "LANDSAT",
              "//worldwind25.arc.nasa.gov/tile/tile.aspx",
              2.25, 4,
              { T: "105" }
            );
            options.map.addLayer( worldwind );
            displayProjection = new OpenLayers.Projection( "EPSG:4326" );
            projection = new OpenLayers.Projection( "EPSG:4326" );
            break;
          case "TERRAIN":
            // add terrain map ( USGS )
            displayProjection = new OpenLayers.Projection( "EPSG:4326" );
            projection = new OpenLayers.Projection( "EPSG:4326" );
            options.map = new OpenLayers.Map({
              div: newdiv,
              projection: projection
            });
            var relief = new OpenLayers.Layer.WMS(
              "USGS Terraserver",
              "//terraserver-usa.org/ogcmap.ashx?",
              { layers: "DRG" }
            );
            options.map.addLayer( relief );
            break;
          case "STAMEN-TONER":
          case "STAMEN-WATERCOLOR":
          case "STAMEN-TERRAIN":
            var layerName = options.type.replace("STAMEN-", "").toLowerCase();
            var sLayer = new OpenLayers.Layer.Stamen( layerName );
            displayProjection = new OpenLayers.Projection( "EPSG:4326" );
            projection = new OpenLayers.Projection( 'EPSG:900913' );
            centerlonlat = centerlonlat.transform( displayProjection, projection );
            options.map = new OpenLayers.Map( {
              div: newdiv,
              projection: projection,
              displayProjection: displayProjection,
              controls: [
                new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.PanPanel(),
                new OpenLayers.Control.ZoomPanel()
              ]
            } );
            options.map.addLayer( sLayer );
            break;
          default: /* case "ROADMAP": */
            // add OpenStreetMap layer
            projection = new OpenLayers.Projection( 'EPSG:900913' );
            displayProjection = new OpenLayers.Projection( 'EPSG:4326' );
            centerlonlat = centerlonlat.transform( displayProjection, projection );
            options.map = new OpenLayers.Map({
              div: newdiv,
              projection: projection,
              "displayProjection": displayProjection
            });
            var osm = new OpenLayers.Layer.OSM();
            options.map.addLayer( osm );
            break;
        }

        if ( options.map ) {
          options.map.setCenter(centerlonlat, options.zoom || 10);
          options.map.div.style.display = "none";
        }
      }
    };

    isGeoReady();

    return {

      /**
       * @member openmap
       * The setup function will be executed when the plug-in is instantiated
       */
      _setup: function( options ) {

        // insert openlayers api script once
        if ( !window.OpenLayers ) {
          Popcorn.getScript( "//openlayers.org/api/OpenLayers.js", function() {
            Popcorn.getScript( "//maps.stamen.com/js/tile.stamen.js" );
          } );
        }

        var isReady = function() {
          // wait until OpenLayers has been loaded, and the start function is run, before adding map
          if ( !options.map ) {
            setTimeout(function() {
              isReady();
            }, 13 );
          } else {

            // default zoom is 2
            options.zoom = options.zoom || 2;

            // make sure options.zoom is a number
            if ( options.zoom && typeof options.zoom !== "number" ) {
              options.zoom = +options.zoom;
            }

            // reset the location and zoom just in case the user played with the map
            options.map.setCenter( centerlonlat, options.zoom );
            if ( options.markers ) {
              var layerStyle = OpenLayers.Util.extend( {} , OpenLayers.Feature.Vector.style[ "default" ] ),
                  featureSelected = function( clickInfo ) {
                    clickedFeature = clickInfo.feature;
                    if ( !clickedFeature.attributes.text ) {
                      return;
                    }
                    popup = new OpenLayers.Popup.FramedCloud(
                      "featurePopup",
                      clickedFeature.geometry.getBounds().getCenterLonLat(),
                      new OpenLayers.Size( 120, 250 ),
                      clickedFeature.attributes.text,
                      null,
                      true,
                      function( closeInfo ) {
                        selectControl.unselect( this.feature );
                      }
                    );
                    clickedFeature.popup = popup;
                    popup.feature = clickedFeature;
                    options.map.addPopup( popup );
                  },
                  featureUnSelected = function( clickInfo ) {
                    feature = clickInfo.feature;
                    if ( feature.popup ) {
                      popup.feature = null;
                      options.map.removePopup( feature.popup );
                      feature.popup.destroy();
                      feature.popup = null;
                    }
                  },
                  gcThenPlotMarker = function( myMarker ) {
                    Popcorn.getJSONP(
                      "//tinygeocoder.com/create-api.php?q=" + myMarker.location + "&callback=jsonp",
                      function( latlng ) {
                        var myPoint = new OpenLayers.Geometry.Point( latlng[1], latlng[0] ).transform( displayProjection, projection ),
                            myPointStyle = OpenLayers.Util.extend( {}, layerStyle );
                        if ( !myMarker.size || isNaN( myMarker.size ) ) {
                          myMarker.size = 14;
                        }
                        myPointStyle.pointRadius = myMarker.size;
                        myPointStyle.graphicOpacity = 1;
                        myPointStyle.externalGraphic = myMarker.icon;
                        var myPointFeature = new OpenLayers.Feature.Vector( myPoint, null, myPointStyle );
                        if ( myMarker.text ) {
                          myPointFeature.attributes = {
                            text: myMarker.text
                          };
                        }
                        pointLayer.addFeatures( [ myPointFeature ] );
                      }
                    );
                  };
              pointLayer = new OpenLayers.Layer.Vector( "Point Layer", { style: layerStyle } );
              options.map.addLayer( pointLayer );
              for ( var m = 0, l = options.markers.length; m < l ; m++ ) {
                var myMarker = options.markers[ m ];
                if( myMarker.text ){
                  if( !selectControl ){
                    selectControl = new OpenLayers.Control.SelectFeature( pointLayer );
                    options.map.addControl( selectControl );
                    selectControl.activate();
                    pointLayer.events.on({
                      "featureselected": featureSelected,
                      "featureunselected": featureUnSelected
                    });
                  }
                }
                if ( myMarker.location ) {
                  var geocodeThenPlotMarker = gcThenPlotMarker;
                  geocodeThenPlotMarker( myMarker );
                } else {
                  var myPoint = new OpenLayers.Geometry.Point( myMarker.lng, myMarker.lat ).transform( displayProjection, projection ),
                      myPointStyle = OpenLayers.Util.extend( {}, layerStyle );
                  if ( !myMarker.size || isNaN( myMarker.size ) ) {
                    myMarker.size = 14;
                  }
                  myPointStyle.pointRadius = myMarker.size;
                  myPointStyle.graphicOpacity = 1;
                  myPointStyle.externalGraphic = myMarker.icon;
                  var myPointFeature = new OpenLayers.Feature.Vector( myPoint, null, myPointStyle );
                  if ( myMarker.text ) {
                    myPointFeature.attributes = {
                      text: myMarker.text
                    };
                  }
                  pointLayer.addFeatures( [ myPointFeature ] );
                }
              }
            }
          }
        };

        isReady();
      },

      /**
       * @member openmap
       * The start function will be executed when the currentTime
       * of the video  reaches the start time provided by the
       * options variable
       */
      start: function( event, options ) {
        toggle( options, "block" );
      },

      /**
       * @member openmap
       * The end function will be executed when the currentTime
       * of the video reaches the end time provided by the
       * options variable
       */
      end: function( event, options ) {
          toggle( options, "none" );
      },

      _teardown: function( options ) {

        target && target.removeChild( newdiv );
        newdiv = map = centerlonlat = projection = displayProjection = pointLayer = selectControl = popup = null;
      }
    };
  },
  {
    about:{
      name: "Popcorn OpenMap Plugin",
      version: "0.3",
      author: "@mapmeld",
      website: "mapadelsur.blogspot.com"
    },
    options:{
      start: {
        elem: "input",
        type: "number",
        label: "Start"
      },
      end: {
        elem: "input",
        type: "number",
        label: "End"
      },
      target: "map-container",
      type: {
        elem: "select",
        options: [ "ROADMAP", "SATELLITE", "TERRAIN" ],
        label: "Map Type",
        optional: true
      },
      zoom: {
        elem: "input",
        type: "number",
        label: "Zoom",
        "default": 2
      },
      lat: {
        elem: "input",
        type: "text",
        label: "Lat",
        optional: true
      },
      lng: {
        elem: "input",
        type: "text",
        label: "Lng",
        optional: true
      },
      location: {
        elem: "input",
        type: "text",
        label: "Location",
        "default": "Toronto, Ontario, Canada"
      },
      markers: {
        elem: "input",
        type: "text",
        label: "List Markers",
        optional: true
      }
    }
  });
}) ( Popcorn );
/**
* Pause Popcorn Plug-in
*
* When this plugin is used, links on the webpage, when clicked, will pause
* popcorn videos that especified 'pauseOnLinkClicked' as an option. Links may
* cause a new page to display on a new window, or may cause a new page to
* display in the current window, in which case the videos won't be available
* anymore. It only affects anchor tags. It does not affect objects with click
* events that act as anchors.
*
* Example:
 var p = Popcorn('#video', { pauseOnLinkClicked : true } )
   .play();
*
*/

document.addEventListener( "click", function( event ) {

  var targetElement = event.target;

  //Some browsers use an element as the target, some use the text node inside
  if ( targetElement.nodeName === "A" || targetElement.parentNode && targetElement.parentNode.nodeName === "A" ) {
    Popcorn.instances.forEach( function( video ) {
      if ( video.options.pauseOnLinkClicked ) {
        video.pause();
      }
    });
  }
}, false );
// PLUGIN: Subtitle

(function ( Popcorn ) {

  var i = 0,
      createDefaultContainer = function( context, id ) {

        var ctxContainer = context.container = document.createElement( "div" ),
            style = ctxContainer.style,
            media = context.media;

        var updatePosition = function() {
          var position = context.position();
          // the video element must have height and width defined
          style.fontSize = "18px";
          style.width = media.offsetWidth + "px";
          style.top = position.top  + media.offsetHeight - ctxContainer.offsetHeight - 40 + "px";
          style.left = position.left + "px";

          setTimeout( updatePosition, 10 );
        };

        ctxContainer.id = id || Popcorn.guid();
        style.position = "absolute";
        style.color = "white";
        style.textShadow = "black 2px 2px 6px";
        style.fontWeight = "bold";
        style.textAlign = "center";

        updatePosition();

        context.media.parentNode.appendChild( ctxContainer );

        return ctxContainer;
      };

  /**
   * Subtitle popcorn plug-in
   * Displays a subtitle over the video, or in the target div
   * Options parameter will need a start, and end.
   * Optional parameters are target and text.
   * Start is the time that you want this plug-in to execute
   * End is the time that you want this plug-in to stop executing
   * Target is the id of the document element that the content is
   *  appended to, this target element must exist on the DOM
   * Text is the text of the subtitle you want to display.
   *
   * @param {Object} options
   *
   * Example:
     var p = Popcorn('#video')
        .subtitle({
          start:            5,                 // seconds, mandatory
          end:              15,                // seconds, mandatory
          text:             'Hellow world',    // optional
          target:           'subtitlediv',     // optional
        } )
   *
   */

  Popcorn.plugin( "subtitle" , {

      manifest: {
        about: {
          name: "Popcorn Subtitle Plugin",
          version: "0.1",
          author: "Scott Downe",
          website: "http://scottdowne.wordpress.com/"
        },
        options: {
          start: {
            elem: "input",
            type: "text",
            label: "Start"
          },
          end: {
            elem: "input",
            type: "text",
            label: "End"
          },
          target: "subtitle-container",
          text: {
            elem: "input",
            type: "text",
            label: "Text"
          }
        }
      },

      _setup: function( options ) {
        var newdiv = document.createElement( "div" );

        newdiv.id = "subtitle-" + i++;
        newdiv.style.display = "none";

        // Creates a div for all subtitles to use
        ( !this.container && ( !options.target || options.target === "subtitle-container" ) ) &&
          createDefaultContainer( this );

        // if a target is specified, use that
        if ( options.target && options.target !== "subtitle-container" ) {
          // In case the target doesn't exist in the DOM
          options.container = document.getElementById( options.target ) || createDefaultContainer( this, options.target );
        } else {
          // use shared default container
          options.container = this.container;
        }

        document.getElementById( options.container.id ) && document.getElementById( options.container.id ).appendChild( newdiv );
        options.innerContainer = newdiv;

        options.showSubtitle = function() {
          options.innerContainer.innerHTML = options.text || "";
        };
      },
      /**
       * @member subtitle
       * The start function will be executed when the currentTime
       * of the video  reaches the start time provided by the
       * options variable
       */
      start: function( event, options ){
        options.innerContainer.style.display = "inline";
        options.showSubtitle( options, options.text );
      },
      /**
       * @member subtitle
       * The end function will be executed when the currentTime
       * of the video  reaches the end time provided by the
       * options variable
       */
      end: function( event, options ) {
        options.innerContainer.style.display = "none";
        options.innerContainer.innerHTML = "";
      },

      _teardown: function ( options ) {
        options.container.removeChild( options.innerContainer );
      }

  });

})( Popcorn );
// PLUGIN: Text

(function ( Popcorn ) {

  /**
   * Text Popcorn plug-in
   *
   * Places text in an element on the page.  Plugin options include:
   * Options parameter will need a start, end.
   *   Start: Is the time that you want this plug-in to execute
   *   End: Is the time that you want this plug-in to stop executing
   *   Text: Is the text that you want to appear in the target
   *   Escape: {true|false} Whether to escape the text (e.g., html strings)
   *   Multiline: {true|false} Whether newlines should be turned into <br>s
   *   Target: Is the ID of the element where the text should be placed. An empty target
   *           will be placed on top of the media element
   *
   * @param {Object} options
   *
   * Example:
   *  var p = Popcorn('#video')
   *
   *    // Simple text
   *    .text({
   *      start: 5, // seconds
   *      end: 15, // seconds
   *      text: 'This video made exclusively for drumbeat.org',
   *      target: 'textdiv'
   *     })
   *
   *    // HTML text, rendered as HTML
   *    .text({
   *      start: 15, // seconds
   *      end: 20, // seconds
   *      text: '<p>This video made <em>exclusively</em> for drumbeat.org</p>',
   *      target: 'textdiv'
   *    })
   *
   *    // HTML text, escaped and rendered as plain text
   *    .text({
   *      start: 20, // seconds
   *      end: 25, // seconds
   *      text: 'This is an HTML p element: <p>paragraph</p>',
   *      escape: true,
   *      target: 'textdiv'
   *    })
   *
   *    // Multi-Line HTML text, escaped and rendered as plain text
   *    .text({
   *      start: 25, // seconds
   *      end: 30, // seconds
   *      text: 'This is an HTML p element: <p>paragraph</p>\nThis is an HTML b element: <b>bold</b>',
   *      escape: true,
   *      multiline: true,
   *      target: 'textdiv'
   *    });
   *
   *    // Subtitle text
   *    .text({
   *      start: 30, // seconds
   *      end: 40, // seconds
   *      text: 'This will be overlayed on the video',
   *     })
   **/

  /**
   * HTML escape code from mustache.js, used under MIT Licence
   * https://github.com/janl/mustache.js/blob/master/mustache.js
   **/
  var escapeMap = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': '&quot;',
    "'": '&#39;'
  };

  function escapeHTML( string, multiline ) {
    return String( string ).replace( /&(?!\w+;)|[<>"']/g, function ( s ) {
      return escapeMap[ s ] || s;
    });
  }

  function newlineToBreak( string ) {
    // Deal with both \r\n and \n
    return string.replace( /\r?\n/gm, "<br>" );
  }

  // Subtitle specific functionality
  function createSubtitleContainer( context, id ) {

    var ctxContainer = context.container = document.createElement( "div" ),
        style = ctxContainer.style,
        media = context.media;

    var updatePosition = function() {
      var position = context.position();
      // the video element must have height and width defined
      style.fontSize = "18px";
      style.width = media.offsetWidth + "px";
      style.top = position.top  + media.offsetHeight - ctxContainer.offsetHeight - 40 + "px";
      style.left = position.left + "px";

      setTimeout( updatePosition, 10 );
    };

    ctxContainer.id = id || "";
    style.position = "absolute";
    style.color = "white";
    style.textShadow = "black 2px 2px 6px";
    style.fontWeight = "bold";
    style.textAlign = "center";

    updatePosition();

    context.media.parentNode.appendChild( ctxContainer );

    return ctxContainer;
  }

  Popcorn.plugin( "text", {

    manifest: {
      about: {
        name: "Popcorn Text Plugin",
        version: "0.1",
        author: "@humphd"
      },
      options: {
        start: {
          elem: "input",
          type: "number",
          label: "Start"
        },
        end: {
          elem: "input",
          type: "number",
          label: "End"
        },
        text: {
          elem: "input",
          type: "text",
          label: "Text",
          "default": "Popcorn.js"
        },
        escape: {
          elem: "input",
          type: "checkbox",
          label: "Escape"
        },
        multiline: {
          elem: "input",
          type: "checkbox",
          label: "Multiline"
        }
      }
    },

    _setup: function( options ) {

      var target,
          text,
          container = options._container = document.createElement( "div" );

      container.style.display = "none";

      if ( options.target ) {
        // Try to use supplied target
        target = Popcorn.dom.find( options.target );

        if ( !target ) {
          target = createSubtitleContainer( this, options.target );
        }
        else if ( [ "VIDEO", "AUDIO" ].indexOf( target.nodeName ) > -1 ) {
          target = createSubtitleContainer( this, options.target + "-overlay" );
        }

      } else if ( !this.container ) {
        // Creates a div for all subtitles to use
        target = createSubtitleContainer( this );

      } else {
        // Use subtitle container
        target = this.container;
      }

      // cache reference to actual target container
      options._target = target;

      // Escape HTML text if requested
      text = !!options.escape ? escapeHTML( options.text ) :
                                    options.text;

      // Swap newline for <br> if requested
      text = !!options.multiline ? newlineToBreak ( text ) : text;
      container.innerHTML = text || "";

      target.appendChild( container );

      options.toString = function() {
        // use the default option if it doesn't exist
        return options.text || options._natives.manifest.options.text[ "default" ];
      };
    },

    /**
     * @member text
     * The start function will be executed when the currentTime
     * of the video  reaches the start time provided by the
     * options variable
     */
    start: function( event, options ) {
      options._container.style.display = "inline";
    },

    /**
     * @member text
     * The end function will be executed when the currentTime
     * of the video  reaches the end time provided by the
     * options variable
     */
    end: function( event, options ) {
      options._container.style.display = "none";
    },
    _teardown: function( options ) {
      var target = options._target;
      if ( target ) {
        target.removeChild( options._container );
      }
    }
  });
})( Popcorn );
// PLUGIN: Timeline
(function ( Popcorn ) {

  /**
     * timeline popcorn plug-in
     * Adds data associated with a certain time in the video, which creates a scrolling view of each item as the video progresses
     * Options parameter will need a start, target, title, and text
     * -Start is the time that you want this plug-in to execute
     * -End is the time that you want this plug-in to stop executing, tho for this plugin an end time may not be needed ( optional )
     * -Target is the id of the DOM element that you want the timeline to appear in. This element must be in the DOM
     * -Title is the title of the current timeline box
     * -Text is text is simply related text that will be displayed
     * -innerHTML gives the user the option to add things such as links, buttons and so on
     * -direction specifies whether the timeline will grow from the top or the bottom, receives input as "UP" or "DOWN"
     * @param {Object} options
     *
     * Example:
      var p = Popcorn("#video")
        .timeline( {
         start: 5, // seconds
         target: "timeline",
         title: "Seneca",
         text: "Welcome to seneca",
         innerHTML: "Click this link <a href='http://www.google.ca'>Google</a>"
      } )
    *
  */

  var i = 1;

  Popcorn.plugin( "timeline" , function( options ) {

    var target = document.getElementById( options.target ),
        contentDiv = document.createElement( "div" ),
        container,
        goingUp = true;

    if ( target && !target.firstChild ) {
      target.appendChild ( container = document.createElement( "div" ) );
      container.style.width = "inherit";
      container.style.height = "inherit";
      container.style.overflow = "auto";
    } else {
      container = target.firstChild;
    }

    contentDiv.style.display = "none";
    contentDiv.id = "timelineDiv" + i;

    //  Default to up if options.direction is non-existant or not up or down
    options.direction = options.direction || "up";
    if ( options.direction.toLowerCase() === "down" ) {

      goingUp = false;
    }

    if ( target && container ) {
      // if this isnt the first div added to the target div
      if( goingUp ){
        // insert the current div before the previous div inserted
        container.insertBefore( contentDiv, container.firstChild );
      }
      else {

        container.appendChild( contentDiv );
      }

    }

    i++;

    //  Default to empty if not used
    //options.innerHTML = options.innerHTML || "";

    contentDiv.innerHTML = "<p><span id='big' style='font-size:24px; line-height: 130%;' >" + options.title + "</span><br />" +
    "<span id='mid' style='font-size: 16px;'>" + options.text + "</span><br />" + options.innerHTML;

    return {

      start: function( event, options ) {
        contentDiv.style.display = "block";

        if( options.direction === "down" ) {
          container.scrollTop = container.scrollHeight;
        }
      },

      end: function( event, options ) {
        contentDiv.style.display = "none";
      },

      _teardown: function( options ) {

        ( container && contentDiv ) && container.removeChild( contentDiv ) && !container.firstChild && target.removeChild( container );
      }
    };
  },
  {

    about: {
      name: "Popcorn Timeline Plugin",
      version: "0.1",
      author: "David Seifried @dcseifried",
      website: "dseifried.wordpress.com"
    },

    options: {
      start: {
        elem: "input",
        type: "number",
        label: "Start"
      },
      end: {
        elem: "input",
        type: "number",
        label: "End"
      },
      target: "feed-container",
      title: {
        elem: "input",
        type: "text",
        label: "Title"
      },
      text: {
        elem: "input",
        type: "text",
        label: "Text"
      },
      innerHTML: {
        elem: "input",
        type: "text",
        label: "HTML Code",
        optional: true
      },
      direction: {
        elem: "select",
        options: [ "DOWN", "UP" ],
        label: "Direction",
        optional: true
      }
    }
  });

})( Popcorn );
// PLUGIN: TWITTER

(function ( Popcorn ) {
  var scriptLoading = false;

  /**
   * Twitter popcorn plug-in
   * Appends a Twitter widget to an element on the page.
   * Options parameter will need a start, end, target and source.
   * Optional parameters are height and width.
   * Start is the time that you want this plug-in to execute
   * End is the time that you want this plug-in to stop executing
   * Src is the hash tag or twitter user to get tweets from
   * Target is the id of the document element that the images are
   *  appended to, this target element must exist on the DOM
   * Height is the height of the widget, defaults to 200
   * Width is the width of the widget, defaults to 250
   *
   * @param {Object} options
   *
   * Example:
     var p = Popcorn('#video')
        .twitter({
          start:          5,                // seconds, mandatory
          end:            15,               // seconds, mandatory
          src:            '@stevesong',     // mandatory, also accepts hash tags
          height:         200,              // optional
          width:          250,              // optional
          target:         'twitterdiv'      // mandatory
        } )
   *
   */

  Popcorn.plugin( "twitter" , {

      manifest: {
        about: {
          name: "Popcorn Twitter Plugin",
          version: "0.1",
          author: "Scott Downe",
          website: "http://scottdowne.wordpress.com/"
        },
        options:{
          start: {
            elem: "input",
            type: "number",
            label: "Start"
          },
          end: {
            elem: "input",
            type: "number",
            label: "End"
          },
          src: {
            elem: "input",
            type: "text",
            label: "Tweet Source (# or @)",
            "default": "@popcornjs"
          },
          target: "twitter-container",
          height: {
            elem: "input",
            type: "number",
            label: "Height",
            "default": "200",
            optional: true
          },
          width: {
            elem: "input",
            type: "number",
            label: "Width",
            "default": "250",
            optional: true
          }
        }
      },

      _setup: function( options ) {

        if ( !window.TWTR && !scriptLoading ) {
          scriptLoading = true;
          Popcorn.getScript( "//widgets.twimg.com/j/2/widget.js" );
        }

        var target = document.getElementById( options.target );
        // create the div to store the widget
        // setup widget div that is unique per track
        options.container = document.createElement( "div" );
        // use this id to connect it to the widget
        options.container.setAttribute( "id", Popcorn.guid() );
        // display none by default
        options.container.style.display = "none";

         // add the widget's div to the target div
        target && target.appendChild( options.container );

        // setup info for the widget
        var src = options.src || "",
            width = options.width || 250,
            height = options.height || 200,
            profile = /^@/.test( src ),
            widgetOptions = {
              version: 2,
              // use this id to connect it to the div
              id: options.container.getAttribute( "id" ),
              rpp: 30,
              width: width,
              height: height,
              interval: 6000,
              theme: {
                shell: {
                  background: "#ffffff",
                  color: "#000000"
                },
                tweets: {
                  background: "#ffffff",
                  color: "#444444",
                  links: "#1985b5"
                }
              },
              features: {
                loop: true,
                timestamp: true,
                avatars: true,
                hashtags: true,
                toptweets: true,
                live: true,
                scrollbar: false,
                behavior: 'default'
              }
            };

        // create widget
        var isReady = function( that ) {
          if ( window.TWTR ) {
            if ( profile ) {

              widgetOptions.type = "profile";

              new TWTR.Widget( widgetOptions ).render().setUser( src ).start();

            } else {

              widgetOptions.type = "search";
              widgetOptions.search = src;
              widgetOptions.subject = src;

              new TWTR.Widget( widgetOptions ).render().start();

            }
          } else {
            setTimeout( function() {
              isReady( that );
            }, 1);
          }
        };

        options.toString = function() {
          return options.src || options._natives.manifest.options.src[ "default" ];
        };

        isReady( this );
      },

      /**
       * @member Twitter
       * The start function will be executed when the currentTime
       * of the video  reaches the start time provided by the
       * options variable
       */
      start: function( event, options ) {
        options.container.style.display = "inline";
      },

      /**
       * @member Twitter
       * The end function will be executed when the currentTime
       * of the video  reaches the end time provided by the
       * options variable
       */
      end: function( event, options ) {
        options.container.style.display = "none";
      },
      _teardown: function( options ) {

        document.getElementById( options.target ) && document.getElementById( options.target ).removeChild( options.container );
      }
    });

})( Popcorn );
// PLUGIN: WEBPAGE

(function ( Popcorn ) {

  /**
   * Webpages popcorn plug-in
   * Creates an iframe showing a website specified by the user
   * Options parameter will need a start, end, id, target and src.
   * Start is the time that you want this plug-in to execute
   * End is the time that you want this plug-in to stop executing
   * Id is the id that you want assigned to the iframe
   * Target is the id of the document element that the iframe needs to be attached to,
   * this target element must exist on the DOM
   * Src is the url of the website that you want the iframe to display
   *
   * @param {Object} options
   *
   * Example:
     var p = Popcorn('#video')
        .webpage({
          id: "webpages-a",
          start: 5, // seconds
          end: 15, // seconds
          src: 'http://www.webmademovies.org',
          target: 'webpagediv'
        } )
   *
   */
  Popcorn.plugin( "webpage" , {
    manifest: {
      about: {
        name: "Popcorn Webpage Plugin",
        version: "0.1",
        author: "@annasob",
        website: "annasob.wordpress.com"
      },
      options: {
        id: {
          elem: "input",
          type: "text",
          label: "Id",
          optional: true
        },
        start: {
          elem: "input",
          type: "number",
          label: "Start"
        },
        end: {
          elem: "input",
          type: "number",
          label: "End"
        },
        src: {
          elem: "input",
          type: "url",
          label: "Webpage URL",
          "default": "http://mozillapopcorn.org"
        },
        target: "iframe-container"
      }
    },
    _setup: function( options ) {

      var target = document.getElementById( options.target );

      // make src an iframe acceptable string
      options.src = options.src.replace( /^(https?:)?(\/\/)?/, "//" );

      // make an iframe
      options._iframe = document.createElement( "iframe" );
      options._iframe.setAttribute( "width", "100%" );
      options._iframe.setAttribute( "height", "100%" );
      options._iframe.id = options.id;
      options._iframe.src = options.src;
      options._iframe.style.display = "none";

      // add the hidden iframe to the DOM
      target && target.appendChild( options._iframe );

    },
    /**
     * @member webpage
     * The start function will be executed when the currentTime
     * of the video  reaches the start time provided by the
     * options variable
     */
    start: function( event, options ){
      // make the iframe visible
      options._iframe.src = options.src;
      options._iframe.style.display = "inline";
    },
    /**
     * @member webpage
     * The end function will be executed when the currentTime
     * of the video  reaches the end time provided by the
     * options variable
     */
    end: function( event, options ){
      // make the iframe invisible
      options._iframe.style.display = "none";
    },
    _teardown: function( options ) {

      document.getElementById( options.target ) && document.getElementById( options.target ).removeChild( options._iframe );
    }
  });
})( Popcorn );
// PLUGIN: WIKIPEDIA


var wikiCallback;

(function ( Popcorn ) {

  /**
   * Wikipedia popcorn plug-in
   * Displays a wikipedia aricle in the target specified by the user by using
   * new DOM element instead overwriting them
   * Options parameter will need a start, end, target, lang, src, title and numberofwords.
   * -Start is the time that you want this plug-in to execute
   * -End is the time that you want this plug-in to stop executing
   * -Target is the id of the document element that the text from the article needs to be
   * attached to, this target element must exist on the DOM
   * -Lang (optional, defaults to english) is the language in which the article is in.
   * -Src is the url of the article
   * -Title (optional) is the title of the article
   * -numberofwords (optional, defaults to 200) is  the number of words you want displaid.
   *
   * @param {Object} options
   *
   * Example:
     var p = Popcorn("#video")
        .wikipedia({
          start: 5, // seconds
          end: 15, // seconds
          src: "http://en.wikipedia.org/wiki/Cape_Town",
          target: "wikidiv"
        } )
   *
   */
  Popcorn.plugin( "wikipedia" , {

    manifest: {
      about:{
        name: "Popcorn Wikipedia Plugin",
        version: "0.1",
        author: "@annasob",
        website: "annasob.wordpress.com"
      },
      options:{
        start: {
          elem: "input",
          type: "number",
          label: "Start"
        },
        end: {
          elem: "input",
          type: "number",
          label: "End"
        },
        lang: {
          elem: "input",
          type: "text",
          label: "Language",
          "default": "english",
          optional: true
        },
        src: {
          elem: "input", 
          type: "url", 
          label: "Wikipedia URL",
          "default": "http://en.wikipedia.org/wiki/Cat"
        },
        title: {
          elem: "input",
          type: "text",
          label: "Title",
          "default": "Cats",
          optional: true
        },
        numberofwords: {
          elem: "input",
          type: "number",
          label: "Number of Words",
          "default": "200",
          optional: true
        },
        target: "wikipedia-container"
      }
    },
    /**
     * @member wikipedia
     * The setup function will get all of the needed
     * items in place before the start function is called.
     * This includes getting data from wikipedia, if the data
     * is not received and processed before start is called start
     * will not do anything
     */
    _setup : function( options ) {
      // declare needed variables
      // get a guid to use for the global wikicallback function
      var  _text, _guid = Popcorn.guid();

      // if the user didn't specify a language default to english
      if ( !options.lang ) {
        options.lang = "en";
      }

      // if the user didn't specify number of words to use default to 200
      options.numberofwords  = options.numberofwords || 200;

      // wiki global callback function with a unique id
      // function gets the needed information from wikipedia
      // and stores it by appending values to the options object
      window[ "wikiCallback" + _guid ]  = function ( data ) {

        options._link = document.createElement( "a" );
        options._link.setAttribute( "href", options.src );
        options._link.setAttribute( "target", "_blank" );

        // add the title of the article to the link
        options._link.innerHTML = options.title || data.parse.displaytitle;

        // get the content of the wiki article
        options._desc = document.createElement( "p" );

        // get the article text and remove any special characters
        _text = data.parse.text[ "*" ].substr( data.parse.text[ "*" ].indexOf( "<p>" ) );
        _text = _text.replace( /((<(.|\n)+?>)|(\((.*?)\) )|(\[(.*?)\]))/g, "" );

        _text = _text.split( " " );
        options._desc.innerHTML = ( _text.slice( 0, ( _text.length >= options.numberofwords ? options.numberofwords : _text.length ) ).join (" ") + " ..." ) ;

        options._fired = true;
      };

      if ( options.src ) {
        Popcorn.getScript( "//" + options.lang + ".wikipedia.org/w/api.php?action=parse&props=text&redirects&page=" +
          options.src.slice( options.src.lastIndexOf( "/" ) + 1 )  + "&format=json&callback=wikiCallback" + _guid );
      }

      options.toString = function() {
        return options.src || options._natives.manifest.options.src[ "default" ];
      };
    },
    /**
     * @member wikipedia
     * The start function will be executed when the currentTime
     * of the video  reaches the start time provided by the
     * options variable
     */
    start: function( event, options ){
      // dont do anything if the information didn't come back from wiki
      var isReady = function () {

        if ( !options._fired ) {
          setTimeout( function () {
            isReady();
          }, 13);
        } else {

          if ( options._link && options._desc ) {
            if ( document.getElementById( options.target ) ) {
              document.getElementById( options.target ).appendChild( options._link );
              document.getElementById( options.target ).appendChild( options._desc );
              options._added = true;
            }
          }
        }
      };

      isReady();
    },
    /**
     * @member wikipedia
     * The end function will be executed when the currentTime
     * of the video  reaches the end time provided by the
     * options variable
     */
    end: function( event, options ){
      // ensure that the data was actually added to the
      // DOM before removal
      if ( options._added ) {
        document.getElementById( options.target ).removeChild( options._link );
        document.getElementById( options.target ).removeChild( options._desc );
      }
    },

    _teardown: function( options ){

      if ( options._added ) {
        options._link.parentNode && document.getElementById( options.target ).removeChild( options._link );
        options._desc.parentNode && document.getElementById( options.target ).removeChild( options._desc );
        delete options.target;
      }
    }
  });

})( Popcorn );
// PLUGIN: Wordriver

(function ( Popcorn ) {

  var container = {},
      spanLocation = 0,
      setupContainer = function( target ) {

        container[ target ] = document.createElement( "div" );

        var t = document.getElementById( target );
        t && t.appendChild( container[ target ] );

        container[ target ].style.height = "100%";
        container[ target ].style.position = "relative";

        return container[ target ];
      },
      // creates an object of supported, cross platform css transitions
      span = document.createElement( "span" ),
      prefixes = [ "webkit", "Moz", "ms", "O", "" ],
      specProp = [ "Transform", "TransitionDuration", "TransitionTimingFunction" ],
      supports = {},
      prop;

  document.getElementsByTagName( "head" )[ 0 ].appendChild( span );

  for ( var sIdx = 0, sLen = specProp.length; sIdx < sLen; sIdx++ ) {

    for ( var pIdx = 0, pLen = prefixes.length; pIdx < pLen; pIdx++ ) {

      prop = prefixes[ pIdx ] + specProp[ sIdx ];

      if ( prop in span.style ) {

        supports[ specProp[ sIdx ].toLowerCase() ] = prop;
        break;
      }
    }
  }

  // Garbage collect support test span
  document.getElementsByTagName( "head" )[ 0 ].appendChild( span );

  /**
   * Word River popcorn plug-in
   * Displays a string of text, fading it in and out
   * while transitioning across the height of the parent container
   * for the duration of the instance  (duration = end - start)
   *
   * @param {Object} options
   *
   * Example:
     var p = Popcorn( '#video' )
        .wordriver({
          start: 5,                      // When to begin the Word River animation
          end: 15,                       // When to finish the Word River animation
          text: 'Hello World',           // The text you want to be displayed by Word River
          target: 'wordRiverDiv',        // The target div to append the text to
          color: "blue"                  // The color of the text. (can be Hex value i.e. #FFFFFF )
        } )
   *
   */

  Popcorn.plugin( "wordriver" , {

      manifest: {
        about:{
          name: "Popcorn WordRiver Plugin"
        },
        options: {
          start: {
            elem: "input",
            type: "number",
            label: "Start"
          },
          end: {
            elem: "input",
            type: "number",
            label: "End"
          },
          target: "wordriver-container",
          text: {
            elem: "input",
            type: "text",
            label: "Text",
            "default": "Popcorn.js"
          },
          color: {
            elem: "input",
            type: "text",
            label: "Color",
            "default": "Green",
            optional: true
          }
        }
      },

      _setup: function( options ) {

        options._duration = options.end - options.start;
        options._container = container[ options.target ] || setupContainer( options.target );

        options.word = document.createElement( "span" );
        options.word.style.position = "absolute";

        options.word.style.whiteSpace = "nowrap";
        options.word.style.opacity = 0;

        options.word.style.MozTransitionProperty = "opacity, -moz-transform";
        options.word.style.webkitTransitionProperty = "opacity, -webkit-transform";
        options.word.style.OTransitionProperty = "opacity, -o-transform";
        options.word.style.transitionProperty = "opacity, transform";

        options.word.style[ supports.transitionduration ] = 1 + "s, " + options._duration + "s";
        options.word.style[ supports.transitiontimingfunction ] = "linear";

        options.word.innerHTML = options.text;
        options.word.style.color = options.color || "black";
      },
      start: function( event, options ){

        options._container.appendChild( options.word );

        // Resets the transform when changing to a new currentTime before the end event occurred.
        options.word.style[ supports.transform ] = "";

        options.word.style.fontSize = ~~( 30 + 20 * Math.random() ) + "px";
        spanLocation = spanLocation % ( options._container.offsetWidth - options.word.offsetWidth );
        options.word.style.left = spanLocation + "px";
        spanLocation += options.word.offsetWidth + 10;
        options.word.style[ supports.transform ] = "translateY(" +
          ( options._container.offsetHeight - options.word.offsetHeight ) + "px)";

        options.word.style.opacity = 1;

        // automatically clears the word based on time
        setTimeout( function() {

		      options.word.style.opacity = 0;
        // ensures at least one second exists, because the fade animation is 1 second
		    }, ( ( (options.end - options.start) - 1 ) || 1 ) * 1000 );
      },
      end: function( event, options ){

        // manually clears the word based on user interaction
        options.word.style.opacity = 0;
      },
      _teardown: function( options ) {

        var target = document.getElementById( options.target );
        // removes word span from generated container
        options.word.parentNode && options._container.removeChild( options.word );

        // if no more word spans exist in container, remove container
        container[ options.target ] &&
          !container[ options.target ].childElementCount &&
          target && target.removeChild( container[ options.target ] ) &&
          delete container[ options.target ];
      }
  });

})( Popcorn );
// PARSER: 0.3 JSON

(function (Popcorn) {
  Popcorn.parser( "parseJSON", "JSON", function( data ) {

    // declare needed variables
    var retObj = {
          title: "",
          remote: "",
          data: []
        },
        manifestData = {}, 
        dataObj = data;
    
    
    /*
      TODO: add support for filling in source children of the video element
      
      
      remote: [
        { 
          src: "whatever.mp4", 
          type: 'video/mp4; codecs="avc1, mp4a"'
        }, 
        { 
          src: "whatever.ogv", 
          type: 'video/ogg; codecs="theora, vorbis"'
        }
      ]

    */
    
        
    Popcorn.forEach( dataObj.data, function ( obj, key ) {
      retObj.data.push( obj );
    });

    return retObj;
  });

})( Popcorn );
// PARSER: 0.1 SBV

(function (Popcorn) {

  /**
   * SBV popcorn parser plug-in 
   * Parses subtitle files in the SBV format.
   * Times are expected in H:MM:SS.MIL format, with hours optional
   * Subtitles which don't match expected format are ignored
   * Data parameter is given by Popcorn, will need a text.
   * Text is the file contents to be parsed
   * 
   * @param {Object} data
   * 
   * Example:
    0:00:02.400,0:00:07.200
    Senator, we're making our final approach into Coruscant.
   */
  Popcorn.parser( "parseSBV", function( data ) {
  
    // declare needed variables
    var retObj = {
          title: "",
          remote: "",
          data: []
        },
        subs = [],
        lines,
        i = 0,
        len = 0,
        idx = 0;
    
    // [H:]MM:SS.MIL string to SS.MIL
    // Will thrown exception on bad time format
    var toSeconds = function( t_in ) {
      var t = t_in.split( ":" ),
          l = t.length-1,
          time;
      
      try {
        time = parseInt( t[l-1], 10 )*60 + parseFloat( t[l], 10 );
        
        // Hours optionally given
        if ( l === 2 ) { 
          time += parseInt( t[0], 10 )*3600;
        }
      } catch ( e ) {
        throw "Bad cue";
      }
      
      return time;
    };
    
    var createTrack = function( name, attributes ) {
      var track = {};
      track[name] = attributes;
      return track;
    };
  
    // Here is where the magic happens
    // Split on line breaks
    lines = data.text.split( /(?:\r\n|\r|\n)/gm );
    len = lines.length;
    
    while ( i < len ) {
      var sub = {},
          text = [],
          time = lines[i++].split( "," );
      
      try {
        sub.start = toSeconds( time[0] );
        sub.end = toSeconds( time[1] );
        
        // Gather all lines of text
        while ( i < len && lines[i] ) {
          text.push( lines[i++] );
        }
        
        // Join line breaks in text
        sub.text = text.join( "<br />" );
        subs.push( createTrack( "subtitle", sub ) );
      } catch ( e ) {
        // Bad cue, advance to end of cue
        while ( i < len && lines[i] ) {
          i++;
        }
      }
      
      // Consume empty whitespace
      while ( i < len && !lines[i] ) {
        i++;
      }
    }
    
    retObj.data = subs;

    return retObj;
  });

})( Popcorn );
// PARSER: 0.3 SRT
(function (Popcorn) {
  /**
   * SRT popcorn parser plug-in 
   * Parses subtitle files in the SRT format.
   * Times are expected in HH:MM:SS,MIL format, though HH:MM:SS.MIL also supported
   * Ignore styling, which may occur after the end time or in-text
   * While not part of the "official" spec, majority of players support HTML and SSA styling tags
   * SSA-style tags are stripped, HTML style tags are left for the browser to handle:
   *    HTML: <font>, <b>, <i>, <u>, <s>
   *    SSA:  \N or \n, {\cmdArg1}, {\cmd(arg1, arg2, ...)}
   
   * Data parameter is given by Popcorn, will need a text.
   * Text is the file contents to be parsed
   * 
   * @param {Object} data
   * 
   * Example:
    1
    00:00:25,712 --> 00:00:30.399
    This text is <font color="red">RED</font> and has not been {\pos(142,120)} positioned.
    This takes \Nup three \nentire lines.
    This contains nested <b>bold, <i>italic, <u>underline</u> and <s>strike-through</s></u></i></b> HTML tags
    Unclosed but <b>supported tags are left in
    <ggg>Unsupported</ggg> HTML tags are left in, even if <hhh>not closed.
    SSA tags with {\i1} would open and close italicize {\i0}, but are stripped
    Multiple {\pos(142,120)\b1}SSA tags are stripped
   */
  Popcorn.parser( "parseSRT", function( data ) {

    // declare needed variables
    var retObj = {
          title: "",
          remote: "",
          data: []
        },
        subs = [],
        i = 0,
        idx = 0,
        lines,
        time,
        text,
        endIdx,
        sub;

    // Here is where the magic happens
    // Split on line breaks
    lines = data.text.split( /(?:\r\n|\r|\n)/gm );
    endIdx = lastNonEmptyLine( lines ) + 1;

    for( i=0; i < endIdx; i++ ) {
      sub = {};
      text = [];

      sub.id = parseInt( lines[i++], 10 );

      // Split on '-->' delimiter, trimming spaces as well
      time = lines[i++].split( /[\t ]*-->[\t ]*/ );

      sub.start = toSeconds( time[0] );

      // So as to trim positioning information from end
      idx = time[1].indexOf( " " );
      if ( idx !== -1) {
        time[1] = time[1].substr( 0, idx );
      }
      sub.end = toSeconds( time[1] );

      // Build single line of text from multi-line subtitle in file
      while ( i < endIdx && lines[i] ) {
        text.push( lines[i++] );
      }

      // Join into 1 line, SSA-style linebreaks
      // Strip out other SSA-style tags
      sub.text = text.join( "\\N" ).replace( /\{(\\[\w]+\(?([\w\d]+,?)+\)?)+\}/gi, "" );
      
      // Escape HTML entities
      sub.text = sub.text.replace( /</g, "&lt;" ).replace( />/g, "&gt;" );

      // Unescape great than and less than when it makes a valid html tag of a supported style (font, b, u, s, i)
      // Modified version of regex from Phil Haack's blog: http://haacked.com/archive/2004/10/25/usingregularexpressionstomatchhtml.aspx
      // Later modified by kev: http://kevin.deldycke.com/2007/03/ultimate-regular-expression-for-html-tag-parsing-with-php/
      sub.text = sub.text.replace( /&lt;(\/?(font|b|u|i|s))((\s+(\w|\w[\w\-]*\w)(\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)+\s*|\s*)(\/?)&gt;/gi, "<$1$3$7>" );
      sub.text = sub.text.replace( /\\N/gi, "<br />" );
      subs.push( createTrack( "subtitle", sub ) );
    }

    retObj.data = subs;
    return retObj;
  });

  function createTrack( name, attributes ) {
    var track = {};
    track[name] = attributes;
    return track;
  }

  // Simple function to convert HH:MM:SS,MMM or HH:MM:SS.MMM to SS.MMM
  // Assume valid, returns 0 on error
  function toSeconds( t_in ) {
    var t = t_in.split( ':' );

    try {
      var s = t[2].split( ',' );

      // Just in case a . is decimal seperator
      if ( s.length === 1 ) {
        s = t[2].split( '.' );
      }

      return parseFloat( t[0], 10 ) * 3600 + parseFloat( t[1], 10 ) * 60 + parseFloat( s[0], 10 ) + parseFloat( s[1], 10 ) / 1000;
    } catch ( e ) {
      return 0;
    }
  }

  function lastNonEmptyLine( linesArray ) {
    var idx = linesArray.length - 1;

    while ( idx >= 0 && !linesArray[idx] ) {
      idx--;
    }

    return idx;
  }
})( Popcorn );
// PARSER: 0.3 SSA/ASS

(function ( Popcorn ) {
  /**
   * SSA/ASS popcorn parser plug-in
   * Parses subtitle files in the identical SSA and ASS formats.
   * Style information is ignored, and may be found in these
   * formats: (\N    \n    {\pos(400,570)}     {\kf89})
   * Out of the [Script Info], [V4 Styles], [Events], [Pictures],
   * and [Fonts] sections, only [Events] is processed.
   * Data parameter is given by Popcorn, will need a text.
   * Text is the file contents to be parsed
   *
   * @param {Object} data
   *
   * Example:
     [Script Info]
      Title: Testing subtitles for the SSA Format
      [V4 Styles]
      Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
      Style: Default,Arial,20,65535,65535,65535,-2147483640,-1,0,1,3,0,2,30,30,30,0,0
      [Events]
      Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
      Dialogue: 0,0:00:02.40,0:00:07.20,Default,,0000,0000,0000,,Senator, {\kf89}we're \Nmaking our final \napproach into Coruscant.
      Dialogue: 0,0:00:09.71,0:00:13.39,Default,,0000,0000,0000,,{\pos(400,570)}Very good, Lieutenant.
      Dialogue: 0,0:00:15.04,0:00:18.04,Default,,0000,0000,0000,,It's \Na \ntrap!
   *
   */

  // Register for SSA extensions
  Popcorn.parser( "parseSSA", function( data ) {
    // declare needed variables
    var retObj = {
          title: "",
          remote: "",
          data: [  ]
        },
        rNewLineFile = /(?:\r\n|\r|\n)/gm,
        subs = [  ],
        lines,
        headers,
        i = 0,
        len;

    // Here is where the magic happens
    // Split on line breaks
    lines = data.text.split( rNewLineFile );
    len = lines.length;

    // Ignore non-textual info
    while ( i < len && lines[ i ] !== "[Events]" ) {
      i++;
    }

    headers = parseFieldHeaders( lines[ ++i ] );

    while ( ++i < len && lines[ i ] && lines[ i ][ 0 ] !== "[" ) {
      try {
        subs.push( createTrack( "subtitle", parseSub( lines[ i ], headers ) ) );
      } catch ( e ) {}
    }

    retObj.data = subs;
    return retObj;
  });

  function parseSub( line, headers ) {
    // Trim beginning 'Dialogue: ' and split on delim
    var fields = line.substr( 10 ).split( "," ),
        rAdvancedStyles = /\{(\\[\w]+\(?([\w\d]+,?)+\)?)+\}/gi,
        rNewLineSSA = /\\N/gi,
        sub;

    sub = {
      start: toSeconds( fields[ headers.start ] ),
      end: toSeconds( fields[ headers.end ] )
    };

    // Invalid time, skip
    if ( sub.start === -1 || sub.end === -1 ) {
      throw "Invalid time";
    }

    // Eliminate advanced styles and convert forced line breaks
    sub.text = getTextFromFields( fields, headers.text ).replace( rAdvancedStyles, "" ).replace( rNewLineSSA, "<br />" );

    return sub;
  }

  // h:mm:ss.cc (centisec) string to SS.mmm
  // Returns -1 if invalid
  function toSeconds( t_in ) {
    var t = t_in.split( ":" );

    // Not all there
    if ( t_in.length !== 10 || t.length < 3 ) {
      return -1;
    }

    return parseInt( t[ 0 ], 10 ) * 3600 + parseInt( t[ 1 ], 10 ) * 60 + parseFloat( t[ 2 ], 10 );
  }

  function getTextFromFields( fields, startIdx ) {
    var fieldLen = fields.length,
        text = [  ],
        i = startIdx;

    // There may be commas in the text which were split, append back together into one line
    for( ; i < fieldLen; i++ ) {
      text.push( fields[ i ] );
    }

    return text.join( "," );
  }

  function createTrack( name, attributes ) {
    var track = {};
    track[ name ] = attributes;
    return track;
  }

  function parseFieldHeaders( line ) {
    // Trim 'Format: ' off front, split on delim
    var fields = line.substr( 8 ).split( ", " ),
        result = {},
        len,
        i;

     //Find where in Dialogue string the start, end and text info is
    for ( i = 0, len = fields.length; i < len; i++ ) {
      if ( fields[ i ] === "Start" ) {
        result.start = i;
      } else if ( fields[ i ] === "End" ) {
        result.end = i;
      } else if ( fields[ i ] === "Text" ) {
        result.text = i;
      }
    }

    return result;
  }
})( Popcorn );
// PARSER: 1.0 TTML
(function ( Popcorn ) {
  /**
   * TTML popcorn parser plug-in
   * Parses subtitle files in the TTML format.
   * Times may be absolute to the timeline or relative
   *   Absolute times are ISO 8601 format (hh:mm:ss[.mmm])
   *   Relative times are a fraction followed by a unit metric (d.ddu)
   *     Relative times are relative to the time given on the parent node
   * Styling information is ignored
   * Data parameter is given by Popcorn, will need an xml.
   * Xml is the file contents to be processed
   *
   * @param {Object} data
   *
   * Example:
    <tt xmlns:tts="http://www.w3.org/2006/04/ttaf1#styling" xmlns="http://www.w3.org/2006/04/ttaf1">
      <body region="subtitleArea">
        <div>
          <p xml:id="subtitle1" begin="0.76s" end="3.45s">
            It seems a paradox, does it not,
          </p>
        </div>
      </body>
    </tt>
   */

  var rWhitespace = /^[\s]+|[\s]+$/gm,
      rLineBreak = /(?:\r\n|\r|\n)/gm;

  Popcorn.parser( "parseTTML", function( data ) {
    var returnData = {
          title: "",
          remote: "",
          data: []
        },
        node;

    // Null checks
    if ( !data.xml || !data.xml.documentElement ) {
      return returnData;
    }

    node = data.xml.documentElement.firstChild;

    if ( !node ) {
      return returnData;
    }

    // Find body tag
    while ( node.nodeName !== "body" ) {
      node = node.nextSibling;
    }

    if ( node ) {
      returnData.data = parseChildren( node, 0 );
    }

    return returnData;
  });

  // Parse the children of the given node
  function parseChildren( node, timeOffset, region ) {
    var currNode = node.firstChild,
        currRegion = getNodeRegion( node, region ),
        retVal = [],
        newOffset;

    while ( currNode ) {
      if ( currNode.nodeType === 1 ) {
        if ( currNode.nodeName === "p" ) {
          // p is a textual node, process contents as subtitle
          retVal.push( parseNode( currNode, timeOffset, currRegion ) );
        } else if ( currNode.nodeName === "div" ) {
          // div is container for subtitles, recurse
          newOffset = toSeconds( currNode.getAttribute( "begin" ) );

          if (newOffset < 0 ) {
            newOffset = timeOffset;
          }

          retVal.push.apply( retVal, parseChildren( currNode, newOffset, currRegion ) );
        }
      }

      currNode = currNode.nextSibling;
    }

    return retVal;
  }

  // Get the "region" attribute of a node, to know where to put the subtitles
  function getNodeRegion( node, defaultTo ) {
    var region = node.getAttribute( "region" );

    if ( region !== null ) {
      return region;
    } else {
      return defaultTo || "";
    }
  }

  // Parse a node for text content
  function parseNode( node, timeOffset, region ) {
    var sub = {};

    // Trim left and right whitespace from text and convert non-explicit line breaks
    sub.text = ( node.textContent || node.text ).replace( rWhitespace, "" ).replace( rLineBreak, "<br />" );
    sub.id = node.getAttribute( "xml:id" ) || node.getAttribute( "id" );
    sub.start = toSeconds ( node.getAttribute( "begin" ), timeOffset );
    sub.end = toSeconds( node.getAttribute( "end" ), timeOffset );
    sub.target = getNodeRegion( node, region );

    if ( sub.end < 0 ) {
      // No end given, infer duration if possible
      // Otherwise, give end as MAX_VALUE
      sub.end = toSeconds( node.getAttribute( "duration" ), 0 );

      if ( sub.end >= 0 ) {
        sub.end += sub.start;
      } else {
        sub.end = Number.MAX_VALUE;
      }
    }

    return { subtitle : sub };
  }

  // Convert time expression to SS.mmm
  // Expression may be absolute to timeline (hh:mm:ss.ms)
  //   or relative ( decimal followed by metric ) ex: 3.4s, 5.7m
  // Returns -1 if invalid
  function toSeconds( t_in, offset ) {
    var i;

    if ( !t_in ) {
      return -1;
    }

    try {
      return Popcorn.util.toSeconds( t_in );
    } catch ( e ) {
      i = getMetricIndex( t_in );
      return parseFloat( t_in.substring( 0, i ) ) * getMultipler( t_in.substring( i ) ) + ( offset || 0 );
    }
  }

  // In a time string such as 3.4ms, get the index of the first character (m) of the time metric (ms)
  function getMetricIndex( t_in ) {
    var i = t_in.length - 1;

    while ( i >= 0 && t_in[ i ] <= "9" && t_in[ i ] >= "0" ) {
      i--;
    }

    return i;
  }

  // Determine multiplier for metric relative to seconds
  function getMultipler( metric ) {
    return {
      "h" : 3600,
      "m" : 60,
      "s" : 1,
      "ms" : 0.001
    }[ metric ] || -1;
  }
})( Popcorn );
// PARSER: 0.1 TTXT

(function (Popcorn) {

  /**
   * TTXT popcorn parser plug-in 
   * Parses subtitle files in the TTXT format.
   * Style information is ignored.
   * Data parameter is given by Popcorn, will need an xml.
   * Xml is the file contents to be parsed as a DOM tree
   * 
   * @param {Object} data
   * 
   * Example:
     <TextSample sampleTime="00:00:00.000" text=""></TextSample>
   */
  Popcorn.parser( "parseTTXT", function( data ) {

    // declare needed variables
    var returnData = {
          title: "",
          remote: "",
          data: []
        };

    // Simple function to convert HH:MM:SS.MMM to SS.MMM
    // Assume valid, returns 0 on error
    var toSeconds = function(t_in) {
      var t = t_in.split(":");
      var time = 0;
      
      try {        
        return parseFloat(t[0], 10)*60*60 + parseFloat(t[1], 10)*60 + parseFloat(t[2], 10);
      } catch (e) { time = 0; }
      
      return time;
    };

    // creates an object of all atrributes keyed by name
    var createTrack = function( name, attributes ) {
      var track = {};
      track[name] = attributes;
      return track;
    };

    // this is where things actually start
    var node = data.xml.lastChild.lastChild; // Last Child of TextStreamHeader
    var lastStart = Number.MAX_VALUE;
    var cmds = [];
    
    // Work backwards through DOM, processing TextSample nodes
    while (node) {
      if ( node.nodeType === 1 && node.nodeName === "TextSample") {
        var sub = {};
        sub.start = toSeconds(node.getAttribute('sampleTime'));
        sub.text = node.getAttribute('text');
      
        if (sub.text) { // Only process if text to display
          // Infer end time from prior element, ms accuracy
          sub.end = lastStart - 0.001;
          cmds.push( createTrack("subtitle", sub) );
        }
        lastStart = sub.start;
      }
      node = node.previousSibling;
    }
    
    returnData.data = cmds.reverse();

    return returnData;
  });

})( Popcorn );
// PARSER: 0.3 WebSRT/VTT

(function ( Popcorn ) {
  /**
   * WebVTT popcorn parser plug-in
   * Parses subtitle files in the WebVTT format.
   * Specification here: http://www.whatwg.org/specs/web-apps/current-work/webvtt.html
   * Styles which appear after timing information are presently ignored.
   * Inline styling tags follow HTML conventions and are left in for the browser to handle (or ignore if VTT-specific)
   * Data parameter is given by Popcorn, text property holds file contents.
   * Text is the file contents to be parsed
   *
   * @param {Object} data
   *
   * Example:
    00:32.500 --> 00:00:33.500 A:start S:50% D:vertical L:98%
    <v Neil DeGrass Tyson><i>Laughs</i>
   */
  Popcorn.parser( "parseVTT", function( data ) {

    // declare needed variables
    var retObj = {
          title: "",
          remote: "",
          data: []
        },
        subs = [],
        i = 0,
        len = 0,
        lines,
        text,
        sub,
        rNewLine = /(?:\r\n|\r|\n)/gm;

    // Here is where the magic happens
    // Split on line breaks
    lines = data.text.split( rNewLine );
    len = lines.length;

    // Check for BOF token
    if ( len === 0 || lines[ 0 ] !== "WEBVTT" ) {
      return retObj;
    }

    i++;

    while ( i < len ) {
      text = [];

      try {
        i = skipWhitespace( lines, len, i );
        sub = parseCueHeader( lines[ i++ ] );

        // Build single line of text from multi-line subtitle in file
        while ( i < len && lines[ i ] ) {
          text.push( lines[ i++ ] );
        }

        // Join lines together to one and build subtitle text
        sub.text = text.join( "<br />" );
        subs.push( createTrack( "subtitle", sub ) );
      } catch ( e ) {
        i = skipNonWhitespace( lines, len, i );
      }
    }

    retObj.data = subs;
    return retObj;
  });

  // [HH:]MM:SS.mmm string to SS.mmm float
  // Throws exception if invalid
  function toSeconds ( t_in ) {
    var t = t_in.split( ":" ),
        l = t_in.length,
        time;

    // Invalid time string provided
    if ( l !== 12 && l !== 9 ) {
      throw "Bad cue";
    }

    l = t.length - 1;

    try {
      time = parseInt( t[ l-1 ], 10 ) * 60 + parseFloat( t[ l ], 10 );

      // Hours were given
      if ( l === 2 ) {
        time += parseInt( t[ 0 ], 10 ) * 3600;
      }
    } catch ( e ) {
      throw "Bad cue";
    }

    return time;
  }

  function createTrack( name, attributes ) {
    var track = {};
    track[ name ] = attributes;
    return track;
  }

  function parseCueHeader ( line ) {
    var lineSegments,
        args,
        sub = {},
        rToken = /-->/,
        rWhitespace = /[\t ]+/;

    if ( !line || line.indexOf( "-->" ) === -1 ) {
      throw "Bad cue";
    }

    lineSegments = line.replace( rToken, " --> " ).split( rWhitespace );

    if ( lineSegments.length < 2 ) {
      throw "Bad cue";
    }

    sub.id = line;
    sub.start = toSeconds( lineSegments[ 0 ] );
    sub.end = toSeconds( lineSegments[ 2 ] );

    return sub;
  }

  function skipWhitespace ( lines, len, i ) {
    while ( i < len && !lines[ i ] ) {
      i++;
    }

    return i;
  }

  function skipNonWhitespace ( lines, len, i ) {
    while ( i < len && lines[ i ] ) {
      i++;
    }

    return i;
  }
})( Popcorn );
// PARSER: 0.1 XML

(function (Popcorn) {

  /**
   *
   *
   */
  Popcorn.parser( "parseXML", "XML", function( data ) {

    // declare needed variables
    var returnData = {
          title: "",
          remote: "",
          data: []
        },
        manifestData = {};

    // Simple function to convert 0:05 to 0.5 in seconds
    // acceptable formats are HH:MM:SS:MM, MM:SS:MM, SS:MM, SS
    var toSeconds = function(time) {
      var t = time.split(":");
      if (t.length === 1) {
        return parseFloat(t[0], 10);
      } else if (t.length === 2) {
        return parseFloat(t[0], 10) + parseFloat(t[1] / 12, 10);
      } else if (t.length === 3) {
        return parseInt(t[0] * 60, 10) + parseFloat(t[1], 10) + parseFloat(t[2] / 12, 10);
      } else if (t.length === 4) {
        return parseInt(t[0] * 3600, 10) + parseInt(t[1] * 60, 10) + parseFloat(t[2], 10) + parseFloat(t[3] / 12, 10);
      }
    };

    // turns a node tree element into a straight up javascript object
    // also converts in and out to start and end
    // also links manifest data with ids
    var objectifyAttributes = function ( nodeAttributes ) {

      var returnObject = {};

      for ( var i = 0, nal = nodeAttributes.length; i < nal; i++ ) {

        var key  = nodeAttributes.item(i).nodeName,
            data = nodeAttributes.item(i).nodeValue,
            manifestItem = manifestData[ data ];

        // converts in into start
        if (key === "in") {
          returnObject.start = toSeconds( data );
        // converts out into end
        } else if ( key === "out" ){
          returnObject.end = toSeconds( data );
        // this is where ids in the manifest are linked
        } else if ( key === "resourceid" ) {
          for ( var item in manifestItem ) {
            if ( manifestItem.hasOwnProperty( item ) ) {
              if ( !returnObject[ item ] && item !== "id" ) {
                returnObject[ item ] = manifestItem[ item ];
              }
            }
          }
        // everything else
        } else {
          returnObject[key] = data;
        }

      }

      return returnObject;
    };

    // creates an object of all atrributes keyd by name
    var createTrack = function( name, attributes ) {
      var track = {};
      track[name] = attributes;
      return track;
    };

    // recursive function to process a node, or process the next child node
    var parseNode = function ( node, allAttributes, manifest ) {
      var attributes = {};
      Popcorn.extend( attributes, allAttributes, objectifyAttributes( node.attributes ), { text: node.textContent || node.text } );

      var childNodes = node.childNodes;

      // processes the node
      if ( childNodes.length < 1 || ( childNodes.length === 1 && childNodes[0].nodeType === 3 ) ) {

        if ( !manifest ) {
          returnData.data.push( createTrack( node.nodeName, attributes ) );
        } else {
          manifestData[attributes.id] = attributes;
        }

      // process the next child node
      } else {

        for ( var i = 0; i < childNodes.length; i++ ) {

          if ( childNodes[i].nodeType === 1 ) {
            parseNode( childNodes[i], attributes, manifest );
          }

        }
      }
    };

    // this is where things actually start
    var x = data.documentElement.childNodes;

    for ( var i = 0, xl = x.length; i < xl; i++ ) {

      if ( x[i].nodeType === 1 ) {

        // start the process of each main node type, manifest or timeline
        if ( x[i].nodeName === "manifest" ) {
          parseNode( x[i], {}, true );
        } else { // timeline
          parseNode( x[i], {}, false );
        }

      }
    }

    return returnData;
  });

})( Popcorn );
(function( window, Popcorn ) {

  Popcorn.player( "soundcloud", {
    _canPlayType: function( nodeName, url ) {
      return ( typeof url === "string" &&
               Popcorn.HTMLSoundCloudAudioElement._canPlaySrc( url ) &&
               nodeName.toLowerCase() !== "audio" );
    }
  });

  Popcorn.soundcloud = function( container, url, options ) {
    if ( typeof console !== "undefined" && console.warn ) {
      console.warn( "Deprecated player 'soundcloud'. Please use Popcorn.HTMLSoundCloudAudioElement directly." );
    }

    var media = Popcorn.HTMLSoundCloudAudioElement( container ),
        popcorn = Popcorn( media, options );

    // Set the src "soon" but return popcorn instance first, so
    // the caller can get get error events.
    setTimeout( function() {
      media.src = url;
    }, 0 );

    return popcorn;
  };

}( window, Popcorn ));
(function() {

  // parseUri 1.2.2
  // http://blog.stevenlevithan.com/archives/parseuri
  // (c) Steven Levithan <stevenlevithan.com>
  // MIT License

  function parseUri (str) {
    var	o   = parseUri.options,
        m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
        uri = {},
        i   = 14;

    while (i--) {
      uri[o.key[i]] = m[i] || "";
    }

    uri[o.q.name] = {};
    uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
      if ($1) {
        uri[o.q.name][$1] = $2;
      }
    });

    return uri;
  }

  parseUri.options = {
    strictMode: false,
    key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
    q:   {
      name:   "queryKey",
      parser: /(?:^|&)([^&=]*)=?([^&]*)/g
    },
    parser: {
      strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
      loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
    }
  };

  function canPlayType( nodeName, url ) {
    return ( /player.vimeo.com\/video\/\d+/ ).test( url ) ||
           ( /vimeo.com\/\d+/ ).test( url );
  }

  Popcorn.player( "vimeo", {

    _canPlayType: canPlayType,
    _setup: function( options ) {

      var TIMEUPDATE_INTERVAL_MS  = 250,
          CURRENT_TIME_MONITOR_MS = 16,
          MediaErrorInterface = {
            MEDIA_ERR_ABORTED: 1,
            MEDIA_ERR_NETWORK: 2,
            MEDIA_ERR_DECODE: 3,
            MEDIA_ERR_SRC_NOT_SUPPORTED: 4
          },
          guid,
          media = this,
          commands = {
            q: [],
            queue: function queue( fn ) {
              this.q.push( fn );
              this.process();
            },
            process: function process() {
              if ( !vimeoReady ) {
                return;
              }

              while ( this.q.length ) {
                var fn = this.q.shift();
                fn();
              }
            }
          },
          currentTimeId,
          timeUpdateId,
          vimeoReady,
          vimeoContainer = document.createElement( "iframe" ),
          // Loosely based on HTMLMediaElement + HTMLVideoElement IDL
          impl = {
            // error state
            error: null,

            // network state
            src: media.src,
            NETWORK_EMPTY: 0,
            NETWORK_IDLE: 1,
            NETWORK_LOADING: 2,
            NETWORK_NO_SOURCE: 3,
            networkState: 0,

            // ready state
            HAVE_NOTHING: 0,
            HAVE_METADATA: 1,
            HAVE_CURRENT_DATA: 2,
            HAVE_FUTURE_DATA: 3,
            HAVE_ENOUGH_DATA: 4,
            readyState: 0,
            seeking: false,

            // playback state
            currentTime: 0,
            duration: NaN,
            paused: true,
            ended: false,
            autoplay: false,
            loop: false,

            // controls
            volume: 1,
            muted: false,

            // Video attributes
            width: 0,
            height: 0
          };

      var readOnlyAttrs = "error networkState readyState seeking duration paused ended";
      Popcorn.forEach( readOnlyAttrs.split(" "), function( value ) {
        Object.defineProperty( media, value, {
          get: function() {
            return impl[ value ];
          }
        });
      });

      Object.defineProperties( media, {
        "src": {
          get: function() {
            return impl.src;
          },
          set: function( value ) {
            // Is there any sort of logic that determines whether to load the video or not?
            impl.src = value;
            media.load();
          }
        },
        "currentTime": {
          get: function() {
            return impl.currentTime;
          },
          set: function( value ) {
            commands.queue(function() {
              sendMessage( "seekTo", value );
            });
            impl.seeking = true;
            media.dispatchEvent( "seeking" );
          }
        },
        "autoplay": {
          get: function() {
            return impl.autoplay;
          },
          set: function( value ) {
            impl.autoplay = !!value;
          }
        },
        "loop": {
          get: function() {
            return impl.loop;
          },
          set: function( value) {
            impl.loop = !!value;
            commands.queue(function() {
              sendMessage( "setLoop", loop );
            });
          }
        },
        "volume": {
          get: function() {
            return impl.volume;
          },
          set: function( value ) {
            impl.volume = value;
            commands.queue(function() {
              sendMessage( "setVolume", impl.muted ? 0 : impl.volume );
            });
            media.dispatchEvent( "volumechange" );
          }
        },
        "muted": {
          get: function() {
            return impl.muted;
          },
          set: function( value ) {
            impl.muted = !!value;
            commands.queue(function() {
              sendMessage( "setVolume", impl.muted ? 0 : impl.volume );
            });
            media.dispatchEvent( "volumechange" );
          }
        },
        "width": {
          get: function() {
            return vimeoContainer.width;
          },
          set: function( value ) {
            vimeoContainer.width = value;
          }
        },
        "height": {
          get: function() {
            return vimeoContainer.height;
          },
          set: function( value ) {
            vimeoContainer.height = value;
          }
        }
      });

      function sendMessage( method, params ) {
        var url = vimeoContainer.src.split( "?" )[ 0 ],
            data = JSON.stringify({
              method: method,
              value: params
            });

        if ( url.substr( 0, 2 ) === "//" ) {
          url = window.location.protocol + url;
        }

        // The iframe has been destroyed, it just doesn't know it
        if ( !vimeoContainer.contentWindow ) {
          media.unload();
          return;
        }

        vimeoContainer.contentWindow.postMessage( data, url );
      }

      var vimeoAPIMethods = {
        "getCurrentTime": function( data ) {
          impl.currentTime = parseFloat( data.value );
        },
        "getDuration": function( data ) {
          impl.duration = parseFloat( data.value );
          maybeReady();
        },
        "getVolume": function( data ) {
          impl.volume = parseFloat( data.value );
        }
      };

      var vimeoAPIEvents = {
        "ready": function( data ) {
          sendMessage( "addEventListener", "loadProgress" );
          sendMessage( "addEventListener", "playProgress" );
          sendMessage( "addEventListener", "play" );
          sendMessage( "addEventListener", "pause" );
          sendMessage( "addEventListener", "finish" );
          sendMessage( "addEventListener", "seek" );
          sendMessage( "getDuration" );
          vimeoReady = true;
          commands.process();
          media.dispatchEvent( "loadstart" );
        },
        "loadProgress": function( data ) {
          media.dispatchEvent( "progress" );
          // loadProgress has a more accurate duration than getDuration
          impl.duration = parseFloat( data.data.duration );
        },
        "playProgress": function( data ) {
          impl.currentTime = parseFloat( data.data.seconds );
        },
        "play": function( data ) {
          // Vimeo plays video if seeking from an unloaded state
          if ( impl.seeking ) {
            impl.seeking = false;
            media.dispatchEvent( "seeked" );
          }
          impl.paused = false;
          impl.ended = false;
          startUpdateLoops();
          media.dispatchEvent( "play" );
        },
        "pause": function( data ) {
          impl.paused = true;
          stopUpdateLoops();
          media.dispatchEvent( "pause" );
        },
        "finish": function( data ) {
          impl.ended = true;
          stopUpdateLoops();
          media.dispatchEvent( "ended" );
        },
        "seek": function( data ) {
          impl.currentTime = parseFloat( data.data.seconds );
          impl.seeking = false;
          impl.ended = false;
          media.dispatchEvent( "timeupdate" );
          media.dispatchEvent( "seeked" );
        }
      };

      function messageListener( event ) {
        if ( event.origin !== "http://player.vimeo.com" ) {
          return;
        }

        var data;
        try {
          data = JSON.parse( event.data );
        } catch ( ex ) {
          console.warn( ex );
        }

        if ( data.player_id != guid ) {
          return;
        }

        // Methods
        if ( data.method && vimeoAPIMethods[ data.method ] ) {
          vimeoAPIMethods[ data.method ]( data );
        }

        // Events
        if ( data.event && vimeoAPIEvents[ data.event ] ) {
          vimeoAPIEvents[ data.event ]( data );
        }
      }

      media.load = function() {
        vimeoReady = false;
        guid = Popcorn.guid();

        var src = parseUri( impl.src ),
            combinedOptions = {},
            optionsArray = [],
            vimeoAPIOptions = {
              api: 1,
              player_id: guid
            };

        if ( !canPlayType( media.nodeName, src.source ) ) {
          setErrorAttr( impl.MEDIA_ERR_SRC_NOT_SUPPORTED );
          return;
        }

        // Add Popcorn ctor options, url options, then the Vimeo API options
        Popcorn.extend( combinedOptions, options );
        Popcorn.extend( combinedOptions, src.queryKey );
        Popcorn.extend( combinedOptions, vimeoAPIOptions );

        // Create the base vimeo player string. It will always have query string options
        src = "http://player.vimeo.com/video/" + ( /\d+$/ ).exec( src.path ) + "?";

        for ( var key in combinedOptions ) {
          if ( combinedOptions.hasOwnProperty( key ) ) {
            optionsArray.push( encodeURIComponent( key ) + "=" + encodeURIComponent( combinedOptions[ key ] ) );
          }
        }
        src += optionsArray.join( "&" );

        impl.loop = !!src.match( /loop=1/ );
        impl.autoplay = !!src.match( /autoplay=1/ );

        vimeoContainer.width = media.style.width ? media.style.width : 500;
        vimeoContainer.height = media.style.height ? media.style.height : 281;
        vimeoContainer.frameBorder = 0;
        vimeoContainer.webkitAllowFullScreen = true;
        vimeoContainer.mozAllowFullScreen = true;
        vimeoContainer.allowFullScreen = true;
        vimeoContainer.src = src;
        media.appendChild( vimeoContainer );
      };

      function setErrorAttr( value ) {
        impl.error = {};
        Popcorn.extend( impl.error, MediaErrorInterface );
        impl.error.code = value;
        media.dispatchEvent( "error" );
      }

      function maybeReady() {
        if ( !isNaN( impl.duration ) ) {
          impl.readyState = 4;
          media.dispatchEvent( "durationchange" );
          media.dispatchEvent( "loadedmetadata" );
          media.dispatchEvent( "loadeddata" );
          media.dispatchEvent( "canplay" );
          media.dispatchEvent( "canplaythrough" );
        }
      }

      function startUpdateLoops() {
        if ( !timeUpdateId ) {
          timeUpdateId = setInterval(function() {
            media.dispatchEvent( "timeupdate" );
          }, TIMEUPDATE_INTERVAL_MS );
        }

        if ( !currentTimeId ) {
          currentTimeId = setInterval(function() {
            sendMessage( "getCurrentTime" );
          }, CURRENT_TIME_MONITOR_MS );
        }
      }

      function stopUpdateLoops() {
        if ( timeUpdateId ) {
          clearInterval( timeUpdateId );
          timeUpdateId = 0;
        }

        if ( currentTimeId ) {
          clearInterval( currentTimeId );
          currentTimeId = 0;
        }
      }

      media.unload = function() {
        stopUpdateLoops();
        window.removeEventListener( "message", messageListener, false );
      };

      media.play = function() {
        commands.queue(function() {
          sendMessage( "play" );
        });
      };

      media.pause = function() {
        commands.queue(function() {
          sendMessage( "pause" );
        });
      };

      // Start the load process now, players behave like `preload="metadata"` is set
      // Do it asynchronously so that users can attach event listeners
      setTimeout(function() {
        window.addEventListener( "message", messageListener, false );
        media.load();
      }, 0 );
    },
    _teardown: function( options ) {
      // If the baseplayer doesn't call _setup
      if ( this.unload ) {
        this.unload();
      }
    }
  });
})();
(function( window, Popcorn ) {
  // A global callback for youtube... that makes me angry
  window.onYouTubePlayerAPIReady = function() {

    onYouTubePlayerAPIReady.ready = true;
    for ( var i = 0; i < onYouTubePlayerAPIReady.waiting.length; i++ ) {
      onYouTubePlayerAPIReady.waiting[ i ]();
    }
  };

  // existing youtube references can break us.
  // remove it and use the one we can trust.
  if ( window.YT ) {
    window.quarantineYT = window.YT;
    window.YT = null;
  }

  onYouTubePlayerAPIReady.waiting = [];

  var _loading = false;

  Popcorn.player( "youtube", {
    _canPlayType: function( nodeName, url ) {

      return typeof url === "string" && (/(?:http:\/\/www\.|http:\/\/|www\.|\.|^)(youtu)/).test( url ) && nodeName.toLowerCase() !== "video";
    },
    _setup: function( options ) {
      if ( !window.YT && !_loading ) {
        _loading = true;
        Popcorn.getScript( "//youtube.com/player_api" );
      }

      var media = this,
          autoPlay = false,
          container = document.createElement( "div" ),
          currentTime = 0,
          paused = true,
          seekTime = 0,
          firstGo = true,
          seeking = false,
          fragmentStart = 0,

          // state code for volume changed polling
          lastMuted = false,
          lastVolume = 100,
          playerQueue = Popcorn.player.playerQueue();

      var createProperties = function() {

        Popcorn.player.defineProperty( media, "currentTime", {
          set: function( val ) {

            if ( options.destroyed ) {
              return;
            }

            val = Number( val );
            
            if ( isNaN ( val ) ) {
              return;
            }
            
            currentTime = val;
            
            seeking = true;
            media.dispatchEvent( "seeking" );
            
            options.youtubeObject.seekTo( val );
          },
          get: function() {

            return currentTime;
          }
        });

        Popcorn.player.defineProperty( media, "paused", {
          get: function() {

            return paused;
          }
        });

        Popcorn.player.defineProperty( media, "muted", {
          set: function( val ) {

            if ( options.destroyed ) {

              return val;
            }

            if ( options.youtubeObject.isMuted() !== val ) {

              if ( val ) {

                options.youtubeObject.mute();
              } else {

                options.youtubeObject.unMute();
              }

              lastMuted = options.youtubeObject.isMuted();
              media.dispatchEvent( "volumechange" );
            }

            return options.youtubeObject.isMuted();
          },
          get: function() {

            if ( options.destroyed ) {

              return 0;
            }

            return options.youtubeObject.isMuted();
          }
        });

        Popcorn.player.defineProperty( media, "volume", {
          set: function( val ) {

            if ( options.destroyed ) {

              return val;
            }

            if ( options.youtubeObject.getVolume() / 100 !== val ) {

              options.youtubeObject.setVolume( val * 100 );
              lastVolume = options.youtubeObject.getVolume();
              media.dispatchEvent( "volumechange" );
            }

            return options.youtubeObject.getVolume() / 100;
          },
          get: function() {

            if ( options.destroyed ) {

              return 0;
            }

            return options.youtubeObject.getVolume() / 100;
          }
        });

        media.play = function() {

          if ( options.destroyed ) {

            return;
          }

          paused = false;
          playerQueue.add(function() {

            if ( options.youtubeObject.getPlayerState() !== 1 ) {

              seeking = false;
              options.youtubeObject.playVideo();
            } else {
              playerQueue.next();
            }
          });
        };

        media.pause = function() {

          if ( options.destroyed ) {

            return;
          }

          paused = true;
          playerQueue.add(function() {

            if ( options.youtubeObject.getPlayerState() !== 2 ) {

              options.youtubeObject.pauseVideo();
            } else {
              playerQueue.next();
            }
          });
        };
      };

      container.id = media.id + Popcorn.guid();
      options._container = container;
      media.appendChild( container );

      var youtubeInit = function() {

        var src, query, params, playerVars, queryStringItem, firstPlay = true, seekEps = 0.1;

        var timeUpdate = function() {

          if ( options.destroyed ) {
            return;
          }

          var ytTime = options.youtubeObject.getCurrentTime();

          if ( !seeking ) {
            currentTime = ytTime;
          } else if ( currentTime >= ytTime - seekEps && currentTime <= ytTime + seekEps ) {
            seeking = false;
            seekEps = 0.1;
            media.dispatchEvent( "seeked" );
          } else {
            // seek didn't work very well, try again with higher tolerance
            seekEps *= 2;
            options.youtubeObject.seekTo( currentTime );
          }
          
          media.dispatchEvent( "timeupdate" );
          
          setTimeout( timeUpdate, 200 );
        };

        // delay is in seconds
        var fetchDuration = function( delay ) {
          var ytDuration = options.youtubeObject.getDuration();

          if ( isNaN( ytDuration ) || ytDuration === 0 ) {
            setTimeout( function() {
              fetchDuration( delay * 2 );
            }, delay*1000 );
          } else {
            // set duration and dispatch ready events
            media.duration = ytDuration;
            media.dispatchEvent( "durationchange" );
            
            media.dispatchEvent( "loadedmetadata" );
            media.dispatchEvent( "loadeddata" );
            
            media.readyState = 4;

            timeUpdate();

            media.dispatchEvent( "canplay" );
            media.dispatchEvent( "canplaythrough" );
          }
        };

        options.controls = +options.controls === 0 || +options.controls === 1 ? options.controls : 1;
        options.annotations = +options.annotations === 1 || +options.annotations === 3 ? options.annotations : 1;

        src = /^.*(?:\/|v=)(.{11})/.exec( media.src )[ 1 ];

        query = ( media.src.split( "?" )[ 1 ] || "" )
                           .replace( /v=.{11}/, "" );
        query = query.replace( /&t=(?:(\d+)m)?(?:(\d+)s)?/, function( all, minutes, seconds ) {

          // Make sure we have real zeros
          minutes = minutes | 0; // bit-wise OR
          seconds = seconds | 0; // bit-wise OR

          fragmentStart = ( +seconds + ( minutes * 60 ) );
          return "";
        });
        query = query.replace( /&start=(\d+)?/, function( all, seconds ) {

          // Make sure we have real zeros
          seconds = seconds | 0; // bit-wise OR

          fragmentStart = seconds;
          return "";
        });

        autoPlay = ( /autoplay=1/.test( query ) );

        params = query.split( /[\&\?]/g );
        playerVars = { wmode: "transparent" };

        for( var i = 0; i < params.length; i++ ) {
          queryStringItem = params[ i ].split( "=" );
          playerVars[ queryStringItem[ 0 ] ] = queryStringItem[ 1 ];
        }
        
        options.youtubeObject = new YT.Player( container.id, {
          height: "100%",
          width: "100%",
          wmode: "transparent",
          playerVars: playerVars,
          videoId: src,
          events: {
            "onReady": function(){

              // pulling initial volume states form baseplayer
              lastVolume = media.volume;
              lastMuted = media.muted;

              volumeupdate();

              paused = media.paused;
              createProperties();
              options.youtubeObject.playVideo();

              media.currentTime = fragmentStart;

              media.dispatchEvent( "loadstart" );

              // wait to dispatch ready events until we get a duration
            },
            "onStateChange": function( state ){

              if ( options.destroyed || state.data === -1 ) {
                return;
              }

              // state.data === 2 is for pause events
              // state.data === 1 is for play events
              if ( state.data === 2 ) {
                paused = true;
                media.dispatchEvent( "pause" );
                playerQueue.next();
              } else if ( state.data === 1 && !firstPlay ) {
                paused = false;
                media.dispatchEvent( "play" );
                media.dispatchEvent( "playing" );
                playerQueue.next();
              } else if ( state.data === 0 ) {
                media.dispatchEvent( "ended" );
              } else if ( state.data === 1 && firstPlay ) {
                firstPlay = false;

                // pulling initial paused state from autoplay or the baseplayer
                // also need to explicitly set to paused otherwise.
                if ( autoPlay || !media.paused ) {
                  paused = false;
                }

                if ( paused ) {
                  options.youtubeObject.pauseVideo();
                }
                
                fetchDuration( 0.025 );
              }
            },
            "onError": function( error ) {

              if ( [ 2, 100, 101, 150 ].indexOf( error.data ) !== -1 ) {
                media.error = {
                  customCode: error.data
                };
                media.dispatchEvent( "error" );
              }
            }
          }
        });

        var volumeupdate = function() {

          if ( options.destroyed ) {

            return;
          }

          if ( lastMuted !== options.youtubeObject.isMuted() ) {

            lastMuted = options.youtubeObject.isMuted();
            media.dispatchEvent( "volumechange" );
          }

          if ( lastVolume !== options.youtubeObject.getVolume() ) {

            lastVolume = options.youtubeObject.getVolume();
            media.dispatchEvent( "volumechange" );
          }

          setTimeout( volumeupdate, 250 );
        };
      };

      if ( onYouTubePlayerAPIReady.ready ) {

        youtubeInit();
      } else {

        onYouTubePlayerAPIReady.waiting.push( youtubeInit );
      }
    },
    _teardown: function( options ) {

      options.destroyed = true;

      var youtubeObject = options.youtubeObject;
      if( youtubeObject ){
        youtubeObject.stopVideo();
        youtubeObject.clearVideo && youtubeObject.clearVideo();
      }

      this.removeChild( document.getElementById( options._container.id ) );
    }
  });
}( window, Popcorn ));
// EFFECT: applyclass

(function (Popcorn) {

  /**
   * apply css class to jquery selector
   * selector is relative to plugin target's id
   * so .overlay is actually jQuery( "#target .overlay")
   *
   * @param {Object} options
   * 
   * Example:
     var p = Popcorn('#video')
        .footnote({
          start: 5, // seconds
          end: 15, // seconds
          text: 'This video made exclusively for drumbeat.org',
          target: 'footnotediv',
          effect: 'applyclass',
          applyclass: 'selector: class'
        })
   *
   */

  var toggleClass = function( event, options ) {

    var idx = 0, len = 0, elements;

    Popcorn.forEach( options.classes, function( key, val ) {

      elements = [];

      if ( key === "parent" ) {

        elements[ 0 ] = document.querySelectorAll("#" + options.target )[ 0 ].parentNode;
      } else {

        elements = document.querySelectorAll("#" + options.target + " " + key );
      }

      for ( idx = 0, len = elements.length; idx < len; idx++ ) {

        elements[ idx ].classList.toggle( val );
      }
    });
  };

  Popcorn.compose( "applyclass", {
    
    manifest: {
      about: {
        name: "Popcorn applyclass Effect",
        version: "0.1",
        author: "@scottdowne",
        website: "scottdowne.wordpress.com"
      },
      options: {}
    },
    _setup: function( options ) {

      options.classes = {};
      options.applyclass = options.applyclass || "";

      var classes = options.applyclass.replace( /\s/g, "" ).split( "," ),
          item = [],
          idx = 0, len = classes.length;

      for ( ; idx < len; idx++ ) {

        item = classes[ idx ].split( ":" );

        if ( item[ 0 ] ) {
          options.classes[ item[ 0 ] ] = item[ 1 ] || "";
        }
      }
    },
    start: toggleClass,
    end: toggleClass
  });
})( Popcorn );
(function (Popcorn) {
    Popcorn.plugin( 'amaratranscript' , {
        _setup : function(options) {

            options.pop = this;
            options.lineHtml = document.createElement('a');
            options.lineHtml.href = '#';
            options.lineHtml.classList.add('amara-group');
            options.lineHtml.classList.add('amara-transcript-line');
            options.lineHtml.innerHTML = options.text;

            if (options.start_of_paragraph) {
                options.container.appendChild(document.createElement('br'));
                options.container.appendChild(document.createElement('br'));
            }

            options.container.appendChild(options.lineHtml);

            options.lineHtml.addEventListener('click', function(e) {
                options.pop.currentTime(options.start);
                e.preventDefault();
                e.stopPropagation();
            }, false);

        },
        start: function(event, options){
            options.lineHtml.classList.add('current-subtitle');
        },
        end: function(event, options){
            options.lineHtml.classList.remove('current-subtitle');
        },
        frame: function(event, options) {

        },
        toString: function(event, options) {

        } 
    });
})(Popcorn);
// PLUGIN: Amara Subtitle (ported from the Subtitle plugin)

(function (Popcorn) {

    var i = 0,
    createDefaultContainer = function(context, id) {

    var ctxContainer = context.container = document.createElement('div'),
        style = ctxContainer.style,
        media = context.media;

        var updatePosition = function() {
            var position = context.position();

            style.fontSize = '16px';
            style.width = media.offsetWidth + 'px';
            style.top = position.top  + media.offsetHeight - ctxContainer.offsetHeight - 63 + 'px';
            style.left = position.left + 'px';

            setTimeout(updatePosition, 10);
        };

        ctxContainer.id = id || Popcorn.guid();
        ctxContainer.className = 'amara-popcorn-subtitles';
        style.position = 'absolute';
        style.color = 'white';
        style.textShadow = 'black 2px 2px 6px';
        style.fontWeight = 'bold';
        style.textAlign = 'center';

        updatePosition();

        context.media.parentNode.appendChild(ctxContainer);

        return ctxContainer;
    };

    /**
     * Subtitle popcorn plug-in
     * Displays a subtitle over the video, or in the target div
     * Options parameter will need a start, and end.
     * Optional parameters are target and text.
     * Start is the time that you want this plug-in to execute
     * End is the time that you want this plug-in to stop executing
     * Target is the id of the document element that the content is
     *  appended to, this target element must exist on the DOM
     * Text is the text of the subtitle you want to display.
     *
     * @param {Object} options
     *
     * Example:
       var p = Popcorn('#video')
           .subtitle({
               start:  5,              // seconds, mandatory
               end:    15,             // seconds, mandatory
               text:   'Hellow world', // optional
               target: 'subtitlediv',  // optional
           })
     **/

Popcorn.plugin('amarasubtitle', {
        manifest: {
            about: {
                name: 'Popcorn Subtitle Plugin',
                version: '0.1',
                author: 'Scott Downe',
                website: 'http://scottdowne.wordpress.com/'
            },
            options: {
                start: {
                    elem: 'input',
                    type: 'text',
                    label: 'Start'
                },
                end: {
                    elem: 'input',
                    type: 'text',
                    label: 'End'
                },
                target: 'subtitle-container',
                text: {
                    elem: 'input',
                    type: 'text',
                    label: 'Text'
                }
            }
        },

        _setup: function(options) {
            var newdiv = document.createElement('div');

            newdiv.id = 'subtitle-' + i++;
            newdiv.style.display = 'none';

            // Creates a div for all subtitles to use
            if (!this.container && (!options.target || options.target === 'subtitle-container')) {
                createDefaultContainer(this);
            }

            // if a target is specified, use that
            if (options.target && options.target !== 'subtitle-container') {
                // In case the target doesn't exist in the DOM
                options.container = document.getElementById(options.target) || createDefaultContainer(this, options.target);
            } else {
                // use shared default container
                options.container = this.container;
            }

            if (document.getElementById(options.container.id)) {
                document.getElementById(options.container.id).appendChild(newdiv);
            }
            options.innerContainer = newdiv;

            options.showSubtitle = function() {
                options.innerContainer.innerHTML = options.text || '';
            };
        },

        /**
         * @member subtitle
         * The start function will be executed when the currentTime
         * of the video  reaches the start time provided by the
         * options variable
         */
        start: function(event, options){
            options.innerContainer.style.display = 'inline';
            options.showSubtitle(options, options.text);
        },

        /**
         * @member subtitle
         * The end function will be executed when the currentTime
         * of the video  reaches the end time provided by the
         * options variable
         */
        end: function(event, options) {
            options.innerContainer.style.display = 'none';
            options.innerContainer.innerHTML = '';
        },

        _teardown: function (options) {
            options.container.removeChild(options.innerContainer);
        }
    });
})(Popcorn);
(function(window, document, undefined) {

    // When the embedder is compiled, dependencies will be loaded directly before this
    // function. Set dependencies to use no-conflict mode to avoid destroying any
    // original objects.
    var __ = _.noConflict();
    var _$ = Zepto;
    var _Backbone = Backbone.noConflict();
    var _Popcorn = Popcorn.noConflict();

    // _amara may exist with a queue of actions that need to be processed after the
    // embedder has finally loaded. Store the queue in toPush for processing in init().
    var toPush = window._amara || [];

    var Amara = function(Amara) {

        // For reference in inner functions.
        var that = this;

        // This will store all future instances of Amara-powered videos.
        // I'm trying really hard here to not use the word "widget".
        this.amaraInstances = [];

        // Private methods that are called via the push() method.
        var actions = {

            // The core function for constructing an entire video with Amara subtitles from
            // just a video URL. This includes DOM creation for the video, etc.
            embedVideo: function(options) {

                // Make sure we have a URL to work with.
                // If we do, init a new Amara view.
                if (__.has(options, 'url') && __.has(options, 'div')) {

                    that.amaraInstances.push(
                        new that.AmaraView({

                            // TODO: This needs to support a node OR ID string.
                            el: _$(options.div)[0],
                            model: new VideoModel(options)
                        })
                    );
                }
            }
        };

        // Utilities.
        var utils = {
            parseFloatAndRound: function(val) {
                return (Math.round(parseFloat(val) * 100) / 100).toFixed(2);
            }
        };

        // Video model.
        var VideoModel = _Backbone.Model.extend({

            // The initialization of these vars is unnecessary, but it's nice to know
            // what vars will *eventually* be on the video model.

            // This var will be true once we've retrieved the rest of the model attrs
            // from the Amara API.
            is_complete: false,

            // Set from within the embedder.
            div: '',
            height: '',
            initial_language: null,
            is_on_amara: null,
            subtitles: [], // Backbone collection
            url: '',
            width: '',

            // Set from the Amara API
            all_urls: [],
            created: null,
            description: null,
            duration: null,
            id: null,
            languages: [],
            original_language: null,
            project: null,
            resource_uri: null,
            team: null,
            thumbnail: null,
            title: null,

            // Every time a video model is created, do this.
            initialize: function() {

                var video = this;
                var apiURL = 'https://staging.universalsubtitles.org/api2/partners/videos/?&video_url=';

                this.subtitles = new that.Subtitles();

                // Make a call to the Amara API to get attributes like available languages,
                // internal ID, description, etc.
                _$.ajax({
                    url: apiURL + this.get('url'),
                    dataType: 'jsonp',
                    success: function(resp) {

                        if (resp.objects.length) {

                            // The video exists on Amara.
                            video.set('is_on_amara', true);

                            // There should only be one object.
                            if (resp.objects.length === 1) {

                                // Set all of the API attrs as attrs on the video model.
                                video.set(resp.objects[0]);

                                // Set the initial language to either the one provided by the initial
                                // options, or the original language from the API.
                                video.set('initial_language',
                                    video.get('initial_language') ||
                                    video.get('original_language')
                                );
                            }

                        } else {

                            // The video does not exist on Amara.
                            video.set('is_on_amara', false);

                        }

                        // Mark that the video model has been completely populated.
                        video.set('is_complete', true);
                    }
                });
            }
        });

        // SubtitleSet model.
        var SubtitleSet = _Backbone.Model.extend({

            // Set from the Amara API
            description: null,
            language: null,
            note: null,
            resource_uri: null,
            site_url: null,
            sub_format: null,
            subtitles: [],
            title: null,
            version_no: null,
            video: null,
            video_description: null,
            video_title: null

        });

        // Subtitles collection.
        this.Subtitles = _Backbone.Collection.extend({
            model: SubtitleSet
        });

        // Amara view. This contains all of the events and logic for a single instance of
        // an Amara-powered video.
        this.AmaraView = _Backbone.View.extend({

            initialize: function() {
                this.model.view = this;
                this.template = __.template(this.templateHTML);
                this.render();
            },

            events: {
                'click ul.amara-languages-list a': 'changeLanguage',
                'click a.amara-current-language':  'languageButtonClicked',
                'click a.amara-share-button':      'shareButtonClicked',
                'click a.amara-transcript-button': 'toggleTranscriptDisplay',
                'click a.amara-subtitles-button':  'toggleSubtitlesDisplay'
            },

            render: function() {
                
                var that = this;

                // Create a container that we will use to inject the Popcorn video.
                this.$el.prepend('<div class="amara-popcorn"></div>');

                this.$popContainer = $('div.amara-popcorn', this.$el);

                // Copy the width and height to the new Popcorn container.
                this.$popContainer.width(this.$el.width());
                this.$popContainer.height(this.$el.height());

                // This is a hack until Popcorn.js supports passing a DOM elem to
                // its smart() method. See: http://bit.ly/L0Lb7t
                var id = 'amara-popcorn-' + Math.floor(Math.random() * 100000000);
                this.$popContainer.attr('id', id);

                // Reset the height on the parent amara-embed div. If we don't do this,
                // our amara-tools div won't be visible.
                this.$el.height('auto');

                // Init the Popcorn video.
                this.pop = _Popcorn.smart(this.$popContainer.attr('id'), this.model.get('url'));

                this.pop.on('loadedmetadata', function() {

                    // Set the video model's height and width, now that we know it.
                    that.model.set('height', that.pop.position().height);
                    that.model.set('width', that.pop.position().width);

                    // Create the actual core DOM for the Amara container.
                    that.$el.append(that.template({
                        video_url: 'http://staging.universalsubtitles.org/en/videos/' + that.model.get('id'),
                        width: that.model.get('width')
                    }));

                    // Just set some cached Zepto selections for later use.
                    that.cacheNodes();

                    // Wait until we have a complete video model (the API was hit as soon as
                    // the video instance was created), and then retrieve the initial set
                    // of subtitles, so we can begin building out the transcript viewer
                    // and the subtitle display.
                    //
                    // We could just make this a callback on the model's initialize() for
                    // after we get a response, but there may be cases where we want to init
                    // a VideoModel separately from an AmaraView.
                    that.waitUntilVideoIsComplete(
                        function() {

                            // Grab the subtitles for the initial language and do yo' thang.
                            if (that.model.get('is_on_amara')) {

                                // Build the language selection dropdown menu.
                                that.buildLanguageSelector();

                                // Make the request to fetch the initial subtitles.
                                //
                                // TODO: This needs to be an option.
                                that.fetchSubtitles(that.model.get('initial_language'), function() {

                                    // When we've got a response with the subtitles, start building
                                    // out the transcript viewer and subtitles.
                                    that.buildTranscript(that.model.get('initial_language'));
                                    that.buildSubtitles(that.model.get('initial_language'));
                                });
                            } else {
                                // Do some other stuff for videos that aren't yet on Amara.
                            }
                        }
                    );
                });

                return this;

            },

            // View utilities. I would like to make these utilities as independent as possible.
            // If someone wants to create a "headless" AmaraView, they should be able to use
            // these utilities without a DOM structure. There's work to be done here to
            // support that cause.
            buildLanguageSelector: function() {
                var langs = this.model.get('languages');
                if (langs.length) {
                    for (var i = 0; i < langs.length; i++) {
                        this.$amaraLanguagesList.append('' +
                            '<li>' +
                                '<a href="#" data-language="' + langs[i].code + '">' +
                                    langs[i].name +
                                '</a>' +
                            '</li>');
                    }
                } else {
                    // We have no languages.
                }
            },
            buildSubtitles: function(language) {

                // Remove any existing subtitle events.
                this.pop.removeTrackEvent('amarasubtitle');

                // Get the subtitle sets for this language.
                var subtitleSets = this.model.subtitles.where({'language': language});

                if (subtitleSets.length) {
                    var subtitleSet = subtitleSets[0];

                    // Get the actual subtitles for this language.
                    var subtitles = subtitleSet.get('subtitles');

                    // For each subtitle, init the Popcorn subtitle plugin.
                    for (var i = 0; i < subtitles.length; i++) {
                        this.pop.amarasubtitle({
                            start: subtitles[i].start,
                            end: subtitles[i].end,
                            text: subtitles[i].text
                        });
                    }

                    this.$popSubtitlesContainer = $('div.amara-popcorn-subtitles', this.$el);

                    this.$amaraCurrentLang.text(this.getLanguageNameForCode(subtitleSet.get('language')));
                }
            },
            buildTranscript: function(language) {

                // Remove any existing transcript events.
                this.pop.removeTrackEvent('amaratranscript');

                var subtitleSet;

                // Get the subtitle sets for this language.
                var subtitleSets = this.model.subtitles.where({'language': language});

                if (subtitleSets.length) {
                    subtitleSet = subtitleSets[0];
                } else {
                    $('.amara-transcript-line-right', this.$transcriptBody).text('No subtitles available.');
                }

                // Get the actual subtitles for this language.
                var subtitles = subtitleSet.get('subtitles');

                if (subtitles.length) {

                    // Remove the loading indicator.
                    this.$transcriptBody.html('');

                    // For each subtitle, init the Popcorn transcript plugin.
                    for (var i = 0; i < subtitles.length; i++) {
                        this.pop.amaratranscript({
                            start: subtitles[i].start,
                            start_clean: utils.parseFloatAndRound(subtitles[i].start),
                            start_of_paragraph: subtitles[i].start_of_paragraph,
                            end: subtitles[i].end,
                            text: subtitles[i].text,
                            container: this.$transcriptBody.get(0)
                        });
                    }

                    this.$amaraCurrentLang.text(this.getLanguageNameForCode(subtitleSet.get('language')));

                } else {
                    $('.amara-transcript-line-right', this.$transcriptBody).text('No subtitles available.');
                }
            },

            // This is a temporary utility function to grab a language's name from a language
            // code. We won't need this once we update our API to return the language name
            // with the subtitles.
            // See https://unisubs.sifterapp.com/projects/12298/issues/722972/comments
            getLanguageNameForCode: function(languageCode) {
                var languages = this.model.get('languages');
                var language = __.find(languages, function(l) { return l.code === languageCode; });
                return language.name;
            },

            // Make a call to the Amara API and retrieve a set of subtitles for a specific
            // video in a specific language. When we get a response, add the subtitle set
            // to the video model's 'subtitles' collection for later retrieval by language code.
            fetchSubtitles: function(language, callback) {
                var that = this;

                var apiURL = ''+
                    'https://staging.universalsubtitles.org/api2/partners/videos/' +
                    this.model.get('id') + '/languages/' + language + '/subtitles/';

                // Make a call to the Amara API to retrieve subtitles for this language.
                //
                // TODO: If we already have subtitles in this language, don't do anything.
                _$.ajax({
                    url: apiURL,
                    dataType: 'jsonp',
                    success: function(resp) {

                        // Save these subtitles to the video's 'subtitles' collection.

                        // TODO: Placeholder until we have the API return the language code.
                        resp.language = language;
                        that.model.subtitles.add(
                            new SubtitleSet(resp)
                        );

                        // Call the callback.
                        callback(resp);
                    }
                });
            },

            // View methods. These are methods that are used with the full AmaraView.
            changeLanguage: function(e) {

                var that = this;
                var lang = $(e.target).data('language');

                this.fetchSubtitles(lang, function() {
                    that.buildTranscript(lang);
                    that.buildSubtitles(lang);
                });

                this.$amaraLanguagesList.hide();
                return false;
            },
            languageButtonClicked: function() {
                this.$amaraLanguagesList.toggle();
                return false;
            },
            shareButtonClicked: function() {
                return false;
            },
            toggleSubtitlesDisplay: function() {

                // TODO: This button needs to be disabled unless we have subtitles to toggle.
                this.$popSubtitlesContainer.toggle();
                this.$subtitlesButton.toggleClass('amara-button-enabled');
                return false;
            },
            toggleTranscriptDisplay: function() {

                // TODO: This button needs to be disabled unless we have a transcript to toggle.
                this.$amaraTranscript.toggle();
                this.$transcriptButton.toggleClass('amara-button-enabled');
                return false;
            },

            waitUntilVideoIsComplete: function(callback) {

                var that = this;

                // is_complete gets set as soon as the initial API call to build out the video
                // instance has finished.
                if (!this.model.get('is_complete')) {
                    setTimeout(function() { that.waitUntilVideoIsComplete(callback); }, 100);
                } else {
                    callback();
                }
            },

            templateHTML: '' +
                '<div class="amara-tools" style="width: {{ width }}px;">' +
                '    <div class="amara-bar amara-group">' +
                //'        <a href="#" class="amara-share-button amara-button"></a>' +
                '        <a href="{{ video_url }}" target="blank" class="amara-logo amara-button">Amara</a>' +
                '        <ul class="amara-displays amara-group">' +
                '            <li><a href="#" class="amara-transcript-button amara-button"></a></li>' +
                '            <li><a href="#" class="amara-subtitles-button amara-button"></a></li>' +
                '        </ul>' +
                '        <div class="amara-languages">' +
                '            <a href="#" class="amara-current-language">Loading&hellip;</a>' +
                '            <ul class="amara-languages-list"></ul>' +
                '        </div>' +
                '    </div>' +
                '    <div class="amara-transcript">' +
                '        <div class="amara-transcript-header amara-group">' +
                //'            <div class="amara-transcript-header-left">' +
                //'                Auto-stream <span>OFF</span>' +
                //'            </div>' +
                //'            <div class="amara-transcript-header-right">' +
                //'                <form action="" class="amara-transcript-search">' +
                //'                    <input class="amara-transcript-search-input" placeholder="Search transcript" />' +
                //'                </form>' +
                //'            </div>' +
                '        </div>' +
                '        <div class="amara-transcript-body">' +
                '            <a href="#" class="amara-transcript-line amara-group">' +
                '                <span class="amara-transcript-line">' +
                '                    Loading transcript&hellip;' +
                '                </span>' +
                '            </a>' +
                '        </div>' +
                '    </div>' +
                '</div>',

            cacheNodes: function() {
                this.$amaraTools         = $('div.amara-tools',      this.$el);
                this.$amaraBar           = $('div.amara-bar',        this.$amaraTools);
                this.$amaraTranscript    = $('div.amara-transcript', this.$amaraTools);

                this.$amaraDisplays      = $('ul.amara-displays',         this.$amaraTools);
                this.$transcriptButton   = $('a.amara-transcript-button', this.$amaraDisplays);
                this.$subtitlesButton    = $('a.amara-subtitles-button',  this.$amaraDisplays);

                this.$amaraLanguages     = $('div.amara-languages',       this.$amaraTools);
                this.$amaraCurrentLang   = $('a.amara-current-language',  this.$amaraLanguages);
                this.$amaraLanguagesList = $('ul.amara-languages-list',  this.$amaraLanguages);

                this.$transcriptBody     = $('div.amara-transcript-body', this.$amaraTranscript);
            }

        });

        // push() handles all action calls before and after the embedder is loaded.
        // Aside from init(), this is the only function that may be called from the
        // parent document.
        //
        // Must send push() an object with only two items:
        //     * Action  (string)
        //     * Options (object)
        //
        // Note: we don't use traditional function arguments because before the
        // embedder is loaded, _amara is just an array with a normal push() method.
        this.push = function(args) {
            
            // No arguments? Don't do anything.
            if (!arguments.length) { return; }

            // Must send push() an object with only two items.
            if (__.size(arguments[0]) === 2) {

                var action = args[0];
                var options = args[1];

                // If a method exists for this action, call it with the options.
                if (actions[action]) {
                    actions[action](options);
                }
            }

        };

        // init() gets called as soon as the embedder has finished loading.
        // Simply processes the existing _amara queue if we have one.
        this.init = function() {

            // Load the Amara CSS.
            var tag = document.getElementsByTagName('script')[0];
            var style = document.createElement('link');
            style.rel = 'stylesheet';
            style.type = 'text/css';

            // TODO: This needs to be a production URL based on DEBUG or not.
            style.href = '/site_media/css/embedder/amara.css';
            tag.parentNode.insertBefore(style, tag);

            // Change the template delimiter for Underscore templates.
            __.templateSettings = { interpolate : /\{\{(.+?)\}\}/g };

            // If we have a queue from before the embedder loaded, process the actions.
            if (toPush) {
                for (var i = 0; i < toPush.length; i++) {
                    that.push(toPush[i]);
                }
                toPush = [];
            }

            // Check to see if we have any amara-embed's to initilize.
            var amaraEmbeds = _$('div.amara-embed');

            if (amaraEmbeds.length) {
                amaraEmbeds.each(function() {

                    var $div = $(this);

                    // Call embedVideo with this div and URL.
                    that.push(['embedVideo', {
                        'div': this,
                        'initial_language': $div.data('initial-language'),
                        'url': $div.data('url')
                    }]);
                });
            }

        };

    };

    window._amara = new Amara();
    window._amara.init();

}(window, document));
