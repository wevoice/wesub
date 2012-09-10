#!/bin/bash

jshint media/js/embedder/embedder.js

cat media/js/embedder/json2.min.js \
    media/js/embedder/underscore.min.js \
    media/js/embedder/zepto.min.js \
    media/js/embedder/backbone.min.js \
    media/js/embedder/popcorn.js \
    media/js/embedder/popcorn.amaratranscript.js \
    media/js/embedder/popcorn.amarasubtitle.js \
    media/js/embedder/embedder.js \
    > media/js/embedder/amara-dev.js

scss -t compressed media/css/embedder/amara.scss media/css/embedder/amara-dev.css

cp media/js/embedder/amara-dev.js media/js/embedder/amara.js
cp media/css/embedder/amara-dev.css media/css/embedder/amara.css

sed -i -e 's/amara-dev/amara/g' media/js/embedder/amara.js
sed -i -e 's/\/site_media/http:\/\/staging.universalsubtitles.org\/site_media/g' media/js/embedder/amara.js
sed -i -e 's/\/site_media/http:\/\/staging.universalsubtitles.org\/site_media/g' media/css/embedder/amara.css

rm media/css/embedder/amara.css-e
rm media/js/embedder/amara.js-e
