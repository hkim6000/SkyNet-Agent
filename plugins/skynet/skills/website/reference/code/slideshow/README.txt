Home page slideshow - a developer option offered in the plan.

Files (namespace MySite, page prefix hm, editor prefix pg; keep your own):
  Home.hero.cs.txt      the Hero() renderer: a single picture, or a slideshow when the block has slides
  Home.slides.js.txt    autoplay every 7 seconds, dots, arrows, swipe, pause while the pointer is on the controls, still under prefers-reduced-motion, paused while the tab is hidden
  Home.slides.css.txt   the slide, caption and control rules for desktop, tablet and phone, plus the editor's Slides list
  Editor.slides.txt     Blocks.cs and AdminPages.cs changes: the hero spec gets items (media + caption), kept only on the home page
  site.hero.json.txt    the data shape

Rules:
  - The block's own picture is the first slide; the caption of the first slide is the picture's Caption in media.json. Items are the other slides, each a photo (never a video) with a caption of up to 60 characters.
  - Paint the slides as the place of business: the building from outside, then the rooms (classroom, kitchen, studio, library; salon floor, treatment room; shop floor, workshop). 1600 x 640, WebP.
  - Only the Home page keeps slides; a hero on another page stays a single picture.
  - The text panel stays readable over every slide: test every slide at 1440, 820 and 390 (cycle with HomeJs.slideTo(k) in the test) and check that the wash gradient covers the text column.
  - Test: the first change happens about 7 seconds after load and the next 7 seconds later; prev/next and dots move; hovering the controls holds; leaving resumes; with reducedMotion: 'reduce' the slide never changes; no horizontal overflow at 390.
