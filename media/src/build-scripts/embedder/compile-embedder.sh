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

sed -i -e 's/embedder-dev/embedder/g' media/build/public/embedder/embedder.js
sed -i -e 's/\/site_media\/src\/css\//\/\/s3.amazonaws.com\/s3.www.universalsubtitles.org\/build\/public\//g' media/build/public/embedder/embedder.js
sed -i -e 's/\/site_media\/images\//\/\/s3.amazonaws.com\/s3.www.universalsubtitles.org\/site_media\/images\//g' media/build/public/embedder/embedder.css

rm media/build/public/embedder/embedder.js-e
rm media/build/public/embedder/embedder.css-e
