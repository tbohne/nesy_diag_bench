library(ggplot2)
library(gridExtra)
library(latex2exp)
library(cowplot)

BAR_COLOR <- c(rgb(32, 43, 50, maxColorValue = 255))
COLOR_VALS <- scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
BAR_DEF <- geom_bar(stat = "identity", fill = BAR_COLOR, width = 0.75)

GENERAL_THEME <- theme(
  axis.title.x = element_text(size = 16),
  axis.title.y = element_text(size = 16),
  axis.text.x = element_text(size = 13),
  axis.text.y = element_text(size = 13),
  legend.title = element_text(size = 16),
  legend.text = element_text(size = 16),
  legend.position = "none"  # remove legend for individual plots
)

GENERAL_THEME_HORI <- theme(
  axis.title.x = element_text(size = 16),
  axis.title.y = element_text(size = 16),
  axis.text.x = element_text(size = 7),
  axis.text.y = element_text(size = 13),
  legend.title = element_text(size = 16),
  legend.text = element_text(size = 16),
  legend.position = "none"  # remove legend for individual plots
)

SHARED_Y_THEME <- theme(
  axis.title.x = element_text(size = 16),
  axis.title.y = element_blank(),
  axis.text.x = element_text(size = 13),
  axis.text.y = element_blank(),
  legend.position = "none"  # remove legend for individual plots
)

SHARED_X_THEME <- theme(
  axis.title.y = element_text(size = 16),
  axis.title.x = element_blank(),
  axis.text.y = element_text(size = 13),
  axis.text.x = element_blank(),
  legend.position = "none"  # remove legend for individual plots
)

# extract legend from a ggplot
extract_legend <- function(plot) {
  tmp <- ggplot_gtable(ggplot_build(plot))
  leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box")
  legend <- tmp$grobs[[leg]]
  return(legend)
}

gen_plot <- function(plot_points_pre, y_name, x_name, filename) {
  final_plot <- plot_points_pre +
    BAR_DEF +
    coord_flip() +
    xlab(x_name) +
    ylab(y_name) +
    COLOR_VALS
  ggsave(final_plot, file = filename, width = 6, height = 12)
}

gen_multi_plot_four <- function(
  pp1, pp2, pp3, pp4, y, x1, x2, x3, x4, filename, group_name
) {
  fpp1 <- pp1 +
    BAR_DEF +
    coord_flip() +
    xlab(y) +
    ylab(x1) +
    COLOR_VALS +
    labs(color = group_name) +
    GENERAL_THEME
  fpp2 <- pp2 +
    BAR_DEF +
    coord_flip() +
    xlab(NULL) +
    ylab(x2) +
    COLOR_VALS +
    labs(color = group_name) +
    SHARED_Y_THEME
  fpp3 <- pp3 +
    BAR_DEF +
    coord_flip() +
    xlab(NULL) +
    ylab(x3) +
    COLOR_VALS +
    labs(color = group_name) +
    SHARED_Y_THEME
  fpp4 <- pp4 +
    BAR_DEF +
    coord_flip() +
    xlab(NULL) +
    ylab(x4) +
    COLOR_VALS +
    labs(color = group_name) +
    SHARED_Y_THEME

  # extract legend from one of the plots (avoid redundant legends)
  legend <- extract_legend(fpp1 + theme(legend.position = "bottom"))

  combined_plot <- plot_grid(
    fpp1, fpp2, fpp3, fpp4, ncol = 4, align = 'h', axis = 'h', rel_widths = c(0.85, 0.65, 0.65, 0.65)
  )

  # add shared legend
  final_plot <- plot_grid(
    combined_plot, legend, ncol = 1, rel_heights = c(1, 0.05)
  ) + theme(plot.background = element_rect(fill = "white", color = NA))

  ggsave(final_plot, file = filename, width = 18, height = 20)
}

gen_multi_plot_two_shared_x <- function(pp1, pp2, y, x1, x2, filename) {
  fpp1 <- pp1 +
    BAR_DEF +
    xlab(NULL) +
    ylab(x1) +
    SHARED_X_THEME
  fpp2 <- pp2 +
    BAR_DEF +
    xlab(y) +
    ylab(x2) +
    GENERAL_THEME_HORI
  combined_plot <- plot_grid(
    fpp1, fpp2, ncol = 1, nrow = 2, align = 'v', axis = 'v', rel_heights = c(0.65, 0.85)
  )
  ggsave(combined_plot, file = filename, width = 15, height = 3)
}

gen_fault_path_multi_plot <- function(
  pp1, pp2, pp3, pp4, y1, y2, y3, x1, x2, x3, x4, filename, group_name
) {
  fpp1 <- pp1 +
    BAR_DEF +
    xlab(y1) +
    ylab(x1) +
    COLOR_VALS +
    labs(color = group_name) +
    SHARED_X_THEME
  fpp2 <- pp2 +
    BAR_DEF +
    xlab(y1) +
    ylab(x2) +
    COLOR_VALS +
    labs(color = group_name) +
    GENERAL_THEME_HORI
  fpp3 <- pp3 +
    geom_point(size = 3) +
    xlab(x3) +
    ylab(y2) +
    COLOR_VALS +
    labs(color = group_name) +
    GENERAL_THEME_HORI
  fpp4 <- pp4 +
    geom_point(size = 3) +
    xlab(x4) +
    ylab(y3) +
    COLOR_VALS +
    labs(color = group_name) +
    GENERAL_THEME_HORI

  # # extract legend from one of the plots (avoid redundant legends)
  # legend <- extract_legend(fpp1 + theme(legend.position = "bottom"))

  combined_plot <- plot_grid(
    fpp1, fpp2, fpp3, fpp4, nrow = 4, align = 'v', axis = 'v', rel_heights = c(0.65, 0.65, 0.65, 0.65)
  )

  # # add shared legend
  # final_plot <- plot_grid(
  #     combined_plot, legend, ncol = 1, rel_heights = c(1, 0.05)
  # ) + theme(plot.background = element_rect(fill = "white", color = NA))

  ggsave(combined_plot, file = filename, width = 15, height = 7)
}

input <- read.csv(file = "compact_res.csv", header = TRUE, sep = ",", check.name = FALSE)

instance_idx_regex <- ".*_(.*)$"

# \\1 -> replace matched string with text captured by first group "()"
instance_indices <- sub(instance_idx_regex, "\\1", input$instance)

input$instance_suffix <- factor(
  instance_indices, levels = instance_indices[order(as.numeric(instance_indices))]
)

# fault path plots

p1 <- ggplot(
  data = input, aes_string(
    x = "instance_suffix", y = "avg_fp_len", color = "gt_match", group = "gt_match"
  )
)

p2 <- ggplot(
  data = input, aes_string(
    x = "instance_suffix", y = "`#fault_paths`", color = "gt_match", group = "gt_match"
  )
)

p3 <- ggplot(
  data = input, aes_string(
    x = "`#fault_paths`", y = "avg_fp_len", color = "gt_match", group = "gt_match",
    ymin = min("avg_fp_len"), ymax = max("avg_fp_len")
  )
)

p4 <- ggplot(
  data = input, aes_string(
    x = "`#fault_paths`", y = "`runtime (s)`", color = "gt_match", group = "gt_match",
    ymin = min("`runtime (s)`"), ymax = max("`runtime (s)`")
  )
)

gen_fault_path_multi_plot(
  p1, p2, p3, p4,
  TeX("instance ($i_\\eta \\in i, i \\in I$)"),
  TeX("$l^a_{i_\\eta}$"),
  TeX("runtime (s)"),
  TeX("$l^a_{i_\\eta}$"),
  "num fault paths",
  "num fault paths",
  "num fault paths",
  "fault_paths.png",
  TeX("$p_2$")
)

# confusion matrix plots

p1 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "TP", color = "gt_match", group = "gt_match"
  )
)

p2 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "TN", color = "gt_match", group = "gt_match"
  )
)

p3 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "FP", color = "gt_match", group = "gt_match"
  )
)

p4 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "FN", color = "gt_match", group = "gt_match"
  )
)

gen_multi_plot_four(
  p1, p2, p3, p4,
  TeX("instance set ($i \\in I$)"),
  TeX("$TP$"),
  TeX("$TN$"),
  TeX("$FP$"),
  TeX("$FN$"),
  "confusion_matrix.png",
  TeX("$p_2$")
)

# classic metrics

p1 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "acc", color = "gt_match", group = "gt_match"
  )
)

p2 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "prec", color = "gt_match", group = "gt_match"
  )
)

p3 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "rec", color = "gt_match", group = "gt_match"
  )
)

p4 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "F1", color = "gt_match", group = "gt_match"
  )
)

gen_multi_plot_four(
  p1, p2, p3, p4,
  TeX("instance set ($i \\in I$)"),
  TeX("$accuracy$"),
  TeX("$precision$"),
  TeX("$recall$"),
  TeX("$F1$"),
  "metrics.png",
  TeX("$p_2$")
)

# runtime, classification ratio and FP / FN

p1 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "classification_ratio", color = "gt_match", group = "gt_match"
  )
)

p2 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "FP", color = "gt_match", group = "gt_match"
  )
)

p3 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "`runtime (s)`", color = "gt_match", group = "gt_match"
  )
)

p4 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "FN", color = "gt_match", group = "gt_match"
  )
)

gen_multi_plot_four(
  p1, p2, p3, p4,
  TeX("instance set ($i \\in I$)"),
  TeX("$c_r$"),
  TeX("$FP$"),
  "runtime (s)",
  TeX("$FN$"),
  "class_ratio.png",
  TeX("$p_2$")
)

# comparing runtime and deviations

p1 <- ggplot(
  data = input, aes_string(
    x = "instance_suffix", y = "`runtime (s)`", color = "gt_match", group = "gt_match"
  )
)

p2 <- ggplot(
  data = input, aes_string(
    x = "instance_suffix", y = "`#fp_dev`", color = "gt_match", group = "gt_match"
  )
)

gen_multi_plot_two_shared_x(
  p1, p2,
  TeX("instance ($i_\\eta \\in i, i \\in I$)"),
  "runtime (s)",
  "deviations",
  "dev_runtime.png"
)

# fault path dev

p1 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "`#fp_dev`", color = "gt_match", group = "gt_match"
  )
)

p2 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "ano_link_perc", color = "gt_match", group = "gt_match"
  )
)

p3 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "avg_fp_len", color = "gt_match", group = "gt_match"
  )
)

p4 <- ggplot(
  data = input, aes_string(
    x = "instance", y = "ratio_of_found_gtfp", color = "gt_match", group = "gt_match"
  )
)

gen_multi_plot_four(
  p1, p2, p3, p4,
  TeX("instance set ($i \\in I$)"),
  "number of fault path deviations",
  TeX("$p_0$"),
  TeX("$l^a_i$"),
  "ratio of found ground truth fault paths",
  "fp_dev.png",
  TeX("$p_2$")
)
