# Helper functions for ENGR-3027 Process Engineering Book
# These functions provide conditional output for HTML vs PDF rendering

#' Attach jQuery as an HTML dependency
#'
#' Quarto's Bootstrap 5 HTML theme does not ship jQuery, but kableExtra's
#' kePrint.js (used by kable_styling() for tooltips/popovers) assumes it is
#' present and otherwise throws "$ is not defined" in the browser console.
#' Call this once per chapter (in the setup chunk) to pull in the copy of
#' jQuery bundled with the rmarkdown package, offline, ahead of any table.
#'
#' @return An htmltools::tagList carrying the jQuery HTML dependency
inject_jquery <- function() {
  if (knitr::is_html_output(excludes = "epub")) {
    htmltools::tagList(rmarkdown::html_dependency_jquery())
  }
}

#' Central control for chart/diagram text sizing
#'
#' Figures are authored wide (fig.width ~9-12in) but displayed in a much
#' narrower book column, so text baked into the image (ggplot2's default
#' base_size = 11) ends up visually tiny once the browser scales the image
#' down to fit. Bump this ONE number to make all chart text larger or
#' smaller across the whole book at once, instead of hand-editing every
#' chunk. Every geom_text()/geom_label()/annotate("text", ...)/element_text()
#' call in the book's .qmd files multiplies its size by this value.
#' @export
diagram_text_scale <- 1.4

#' theme_minimal()/theme_void() wrappers with a larger default base_size
#'
#' Shadow ggplot2's versions so every existing bare theme_minimal()/
#' theme_void() call in the book picks up diagram_text_scale automatically,
#' without needing base_size passed explicitly at each call site.
theme_minimal <- function(base_size = 11 * diagram_text_scale, ...) {
  ggplot2::theme_minimal(base_size = base_size, ...)
}
theme_void <- function(base_size = 11 * diagram_text_scale, ...) {
  ggplot2::theme_void(base_size = base_size, ...)
}

# Also scale the default size of geom_text()/annotate("text", ...) layers
# that don't pass their own explicit `size =` (ggplot2's own default is
# 3.88). Layers that DO pass an explicit size (as `size = N * diagram_text_scale`)
# are unaffected by this and controlled directly by their own literal.
ggplot2::update_geom_defaults("text", list(size = 3.88 * diagram_text_scale))

#' Embed a YouTube video with conditional output
#'
#' In HTML output, displays a responsive iframe embed.
#' In PDF/LaTeX output, displays a formatted link to the video.
#'
#' @param video_id The YouTube video ID (e.g., "dQw4w9WgXcQ")
#' @param title The title to display (used in PDF link text)
#' @return NULL (outputs directly via cat)
#' @examples
#' embed_youtube("dQw4w9WgXcQ", "Example Video")
embed_youtube <- function(video_id, title = "Watch Video") {
  # Clean video ID (remove any URL parts if full URL passed)
  if (grepl("youtube.com|youtu.be", video_id)) {
    # Extract video ID from URL
    video_id <- gsub(".*(?:youtube\\.com/embed/|youtube\\.com/watch\\?v=|youtu\\.be/)([^&?/]+).*", "\\1", video_id)
  }

  if (knitr::is_html_output()) {
    # HTML output - responsive iframe
    cat(sprintf('
<div style="position: relative; padding-bottom: 56.25%%; height: 0; overflow: hidden; max-width: 100%%;">
  <iframe
    style="position: absolute; top: 0; left: 0; width: 100%%; height: 100%%;"
    src="https://www.youtube.com/embed/%s"
    title="%s"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
  </iframe>
</div>
', video_id, title))
  } else {
    # PDF/LaTeX output - formatted link
    cat(sprintf('\n\n**%s:** [https://www.youtube.com/watch?v=%s](https://www.youtube.com/watch?v=%s)\n\n',
                title, video_id, video_id))
  }
}

#' Create a styled info box with conditional output
#'
#' In HTML output, displays a colored box.
#' In PDF output, displays a simple formatted block.
#'
#' @param content The content to display
#' @param type The type of box: "info", "warning", "tip", "note"
#' @return NULL (outputs directly via cat)
info_box <- function(content, type = "info") {
  colors <- list(
    info = "#3498DB",
    warning = "#E74C3C",
    tip = "#2ECC71",
    note = "#F39C12"
  )

  icons <- list(
    info = "Info",
    warning = "Warning",
    tip = "Tip",
    note = "Note"
  )

  color <- colors[[type]]
  icon <- icons[[type]]

  if (knitr::is_html_output()) {
    cat(sprintf('
<div style="padding: 15px; margin: 10px 0; border-left: 5px solid %s; background-color: %s20;">
<strong>%s:</strong> %s
</div>
', color, color, icon, content))
  } else {
    cat(sprintf('\n\n**%s:** %s\n\n', icon, content))
  }
}
