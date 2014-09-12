The Subtitle Editor
===================

The subtitle editor is one of the larger features of amara.  It's implemented
using several components in a couple different areas:

  - The view `subtitles.views.subtitle_editor` serves up the page
  - The page runs javascript that lives in
    :file:`media/src/js/subtitle-editor`
  - We save subtitles using the API code (currently in a private repository,
    but we plan to merge it in to the main one soon)

.. seealso::

    :doc:`subtitle-workflows`
