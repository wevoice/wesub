Data model refactor notes
=========================

API
===

Deprecated fields
-----------------

Video Language Resource, fields to deprecate:

* completion
* description
* is_original
* is_translation
* num_versions
* original_language_code
* percent_done
* subtitle_count
* title

New data model fields:

* created
* id
* language_code
* official_signoff_count
* resource_uri
