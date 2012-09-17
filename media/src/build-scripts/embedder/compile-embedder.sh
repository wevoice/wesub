#!/bin/bash

jshint media/src/js/embedder/embedder.js

cat media/src/js/third-party/json2.min.js \
    media/src/js/third-party/underscore.min.js \
    media/src/js/third-party/zepto.min.js \
    media/src/js/third-party/backbone.min.js \
    media/src/js/third-party/popcorn.js \
    media/src/js/embedder/popcorn.amaratranscript.js \
    media/src/js/embedder/popcorn.amarasubtitle.js \
    media/src/js/embedder/embedder.js \
    > media/src/js/embedder/embedder-dev.js

scss -t compressed media/src/css/embedder/embedder.scss media/src/css/embedder/embedder-dev.css

cp media/src/js/embedder/embedder-dev.js media/build/public/embedder/embedder.js
cp media/src/css/embedder/embedder-dev.css media/build/public/embedder/embedder.css

#sed -i -e 's/amara-dev/amara/g' media/build/public/embedder/amara.js
#sed -i -e 's/\/site_media/https:\/\/staging.universalsubtitles.org\/site_media/g' media/js/embedder/amara.js
#sed -i -e 's/\/site_media/https:\/\/staging.universalsubtitles.org\/site_media/g' media/build/public/embedder/embedder.css

#rm media/src/css/embedder/embedder.css-e
#rm media/js/embedder/amara.js-e
