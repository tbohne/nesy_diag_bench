#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-
# @author Tim Bohne

# required packages
packages <- c("ggplot2", "gridExtra", "dplyr", "latex2exp", "cowplot", "scales")
# check for missing packages + installation
new_packages <- packages[!(packages %in% installed.packages()[, "Package"])]
if (length(new_packages)) {
  install.packages(new_packages)
}
# load packages
lapply(packages, library, character.only = TRUE)

BAR_COLOR <- c(rgb(32, 43, 50, maxColorValue = 255))
BAR_DEF <- geom_bar(stat = "identity", fill = BAR_COLOR, width = 0.75)
COLOR_VALS <- c("#d44345", "#ffb641", "#ffff00", "#ccff99", "#00ff00")

GENERAL_THEME <- theme(
    axis.title.x = element_text(size = 16),
    axis.title.y = element_text(size = 16),
    axis.text.x = element_text(size = 13),
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

# extract legend from a ggplot
extract_legend <- function(plot) {
    tmp <- ggplot_gtable(ggplot_build(plot))
    leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box")
    legend <- tmp$grobs[[leg]]
    return(legend)
}

gen_multi_plot_four <- function(pp1, pp2, pp3, pp4, y, x1, x2, x3, x4, filename, group_name) {
    fpp1 <- pp1 + BAR_DEF + coord_flip() + xlab(y) + ylab(x1) + scale_color_manual(values = color_mapping) + labs(color = group_name) + GENERAL_THEME
    fpp2 <- pp2 + BAR_DEF + coord_flip() + xlab(NULL) + ylab(x2) + scale_color_manual(values = color_mapping) + labs(color = group_name) + SHARED_Y_THEME
    fpp3 <- pp3 + BAR_DEF + coord_flip() + xlab(NULL) + ylab(x3) + scale_color_manual(values = color_mapping) + labs(color = group_name) + SHARED_Y_THEME
    fpp4 <- pp4 + BAR_DEF + coord_flip() + xlab(NULL) + ylab(x4) + scale_color_manual(values = color_mapping) + labs(color = group_name) + SHARED_Y_THEME

    # extract legend from one of the plots (avoid redundant legends)
    legend <- extract_legend(fpp1 + theme(legend.position = "bottom"))

    combined_plot <- plot_grid(
        fpp1, fpp2, fpp3, fpp4, ncol = 4, align = 'h', axis = 'h', rel_widths = c(1, 0.65, 0.65, 0.65)
    )
    # add shared legend
    final_plot <- plot_grid(
        combined_plot, legend, ncol = 1, rel_heights = c(1, 0.05)
    ) + theme(plot.background = element_rect(fill = "white", color = NA))

    ggsave(final_plot, file = filename, width = 12, height = 9)
}

gen_multi_plot_three <- function(pp1, pp2, pp3, y, x1, x2, x3, filename, group_name) {
    fpp1 <- pp1 + BAR_DEF + coord_flip() + xlab(y) + ylab(x1) + scale_color_manual(values = color_mapping) + labs(color = group_name) + GENERAL_THEME
    fpp2 <- pp2 + BAR_DEF + coord_flip() + xlab(NULL) + ylab(x2) + scale_color_manual(values = color_mapping) + labs(color = group_name) + SHARED_Y_THEME
    fpp3 <- pp3 + BAR_DEF + coord_flip() + xlab(NULL) + ylab(x3) + scale_color_manual(values = color_mapping) + labs(color = group_name) + SHARED_Y_THEME

    # extract legend from one of the plots (avoid redundant legends)
    legend <- extract_legend(fpp1 + theme(legend.position = "bottom"))

    combined_plot <- plot_grid(
        fpp1, fpp2, fpp3, ncol = 3, align = 'h', axis = 'h', rel_widths = c(1, 0.65, 0.65)
    )
    # add shared legend
    final_plot <- plot_grid(
        combined_plot, legend, ncol = 1, rel_heights = c(1, 0.05)
    ) + theme(plot.background = element_rect(fill = "white", color = NA))

    ggsave(final_plot, file = filename, width = 12, height = 9)
}

gen_multi_plot_two <- function(pp1, pp2, y, x1, x2, filename, group_name) {
    fpp1 <- pp1 + BAR_DEF + coord_flip() + xlab(y) + ylab(x1) + scale_color_manual(values = color_mapping) + labs(color = group_name) + GENERAL_THEME
    fpp2 <- pp2 + BAR_DEF + coord_flip() + xlab(NULL) + ylab(x2) + scale_color_manual(values = color_mapping) + labs(color = group_name) + SHARED_Y_THEME

    # extract legend from one of the plots (avoid redundant legends)
    legend <- extract_legend(fpp1 + theme(legend.position = "bottom"))

    combined_plot <- plot_grid(
        fpp1, fpp2, ncol = 2, align = 'h', axis = 'h', rel_widths = c(1, 0.65)
    )

    # add shared legend
    final_plot <- plot_grid(
        combined_plot, legend, ncol = 1, rel_heights = c(1, 0.05)
    ) + theme(plot.background = element_rect(fill = "white", color = NA))

    ggsave(final_plot, file = filename, width = 12, height = 9)
}

input <- read.csv(file = "results/compact_cumulative_res.csv", header = TRUE, sep = ",", check.name = FALSE)

# instead of the percentage value factor(gt_match_perc) for which I'd need 100
# colors, I only want to color / group them into 5 groups
LABELS <- c("[0,5)%", "[5, 50)%", "[50,75)%", "[75,100)%", "100%")
color_mapping <- setNames(COLOR_VALS, LABELS)

input$gt_match <- cut(
    input$gt_match_perc,
    breaks = c(0, 5, 50, 75, 100, Inf),
    labels = LABELS,
    include.lowest = TRUE,
    right = FALSE
)

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_tp", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_tn", color = "gt_match", group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_fp", color = "gt_match", group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_fn", color = "gt_match", group = "gt_match"
    )
)

# confusion matrix multiplot
gen_multi_plot_four(
    p1, p2, p3, p4,
    TeX("instance set ($i \\in I$)"),
    TeX("$\\bar{TP}$"),
    TeX("$\\bar{TN}$"),
    TeX("$\\bar{FP}$"),
    TeX("$\\bar{FN}$"),
    "confusion_matrix.png",
    TeX("$p_2^i$")
)

# avoid log(0)
input <- input %>%
    mutate(fp_dev_max = ifelse(fp_dev_max == 0, 1e-1, fp_dev_max))
input <- input %>%
    mutate(fp_dev_mean = ifelse(fp_dev_mean == 0, 1e-1, fp_dev_mean))

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "fp_dev_mean", color = "gt_match", group = "gt_match"
    )
) + scale_y_log10(labels = scales::trans_format("log10", scales::math_format(10^.x)), limits=c(1e-1, 1e3))

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "fp_dev_max", color = "gt_match", group = "gt_match"
    )
) + scale_y_log10(labels = scales::trans_format("log10", scales::math_format(10^.x)), limits=c(1e-1, 1e5))

# fault path dev multiplot
gen_multi_plot_two(
    p1, p2,
    TeX("instance set ($i \\in I$)"),
    TeX("$\\tilde{f^a_i}$"),
    TeX("$\\tilde{f^{max}_i}$"),
    "fault_path_dev.png",
    TeX("$p_2^i$")
)

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_acc", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_prec", color = "gt_match", group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_rec", color = "gt_match", group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_f1", color = "gt_match", group = "gt_match"
    )
)

# common eval metrics
gen_multi_plot_four(
    p1, p2, p3, p4,
    TeX("instance set ($i \\in I$)"),
    TeX("$\\bar{accuracy}$"),
    TeX("$\\bar{precision}$"),
    TeX("$\\bar{recall}$"),
    TeX("$\\bar{F1}$"),
    "eval_metrics.png",
    TeX("$p_2^i$")
)

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_ano_link_perc", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_fp", color = "gt_match", group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_ratio_of_found_gtfp", color = "gt_match", group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_fn", color = "gt_match", group = "gt_match"
    )
)

# ground truth analysis
gen_multi_plot_four(
    p1, p2, p3, p4,
    TeX("instance set ($i \\in I$)"),
    TeX("$\\bar{p_0}^i$"),
    TeX("$\\bar{FP}$"),
    TeX("$\\bar{p_1}^i$"),
    TeX("$\\bar{FN}$"),
    "gt_analysis.png",
    TeX("$p_2^i$")
)

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_num_fault_paths", color = "gt_match", group = "gt_match"
    )
)

# # avoid log(0)
input <- input %>%
    mutate(max_num_fault_paths = ifelse(max_num_fault_paths == 0, 1e-1, max_num_fault_paths))

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "max_num_fault_paths", color = "gt_match", group = "gt_match"
    )
) + scale_y_log10(labels = scales::trans_format("log10", scales::math_format(10^.x)), limits=c(1, 3 * 1e3))

p3 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_fault_path_len", color = "gt_match", group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "max_fault_path_len", color = "gt_match", group = "gt_match"
    )
)

# fault path plot
gen_multi_plot_four(
    p1, p2, p3, p4,
    TeX("instance set ($i \\in I$)"),
    TeX("$f^a_i$"),
    TeX("$f^{max}_i$"),
    TeX("$l^a_i$"),
    TeX("$l^{max}_i$"),
    "fault_paths.png",
    TeX("$p_2^i$")
)

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_classification_ratio", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_fp", color = "gt_match", group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "`avg_runtime (s)`", color = "gt_match", group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_fn", color = "gt_match", group = "gt_match"
    )
)

# classification ratio, etc.
gen_multi_plot_four(
    p1, p2, p3, p4,
    TeX("instance set ($i \\in I$)"),
    TeX("$\\bar{c_r}^i$"),
    TeX("$\\bar{FP}$"),
    TeX("$r^a_i$ (s)"),
    TeX("$\\bar{FN}$"),
    "classification_ratio.png",
    TeX("$p_2^i$")
)

# visualize compensation capability

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_f1", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_acc", color = "gt_match", group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_ano_link_perc", color = "gt_match", group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_ratio_of_found_gtfp", color = "gt_match", group = "gt_match"
    )
)

gen_multi_plot_four(
    p1, p2, p3, p4,
    TeX("instance set ($i \\in I$)"),
    TeX("$\\bar{F1}$"),
    TeX("$\\bar{accuracy}$"),
    TeX("$\\bar{p_0}^i$"),
    TeX("$\\bar{p_1}^i$"),
    "compensation.png",
    TeX("$p_2^i$")
)

# visualize actual compensation (!) and missed chances

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_compensation_by_aff_by_savior", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_missed_chances", color = "gt_match", group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_no_second_chance", color = "gt_match", group = "gt_match"
    )
)

gen_multi_plot_three(
    p1, p2, p3,
    TeX("instance set ($i \\in I$)"),
    TeX("$\\bar{c_1}^i$"),
    TeX("$\\bar{c_2}^i$"),
    TeX("$\\bar{c_3}^i$"),
    "compensation_metrics.png",
    TeX("$p_2^i$")
)

# visualize "best of" plots

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_classification_ratio", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_ano_link_perc", color = "gt_match", group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_ratio_of_found_gtfp", color = "gt_match", group = "gt_match"
    )
)

# avoid log(0)
input <- input %>%
    mutate(fp_dev_max = ifelse(fp_dev_max == 0, 1e-1, fp_dev_max))

p4 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "fp_dev_max", color = "gt_match", group = "gt_match"
    )
) + scale_y_log10(labels = scales::trans_format("log10", scales::math_format(10^.x)), limits=c(1e-1, 4 * 1e4))

gen_multi_plot_four(
    p1, p2, p3, p4,
    TeX("instance set ($i \\in I$)"),
    TeX("$\\bar{c_r}$"),
    TeX("$\\bar{p_0}$"),
    TeX("$p_1$"),
    TeX("$\\tilde{f^{max}_i}$"),
    "bestof.png",
    TeX("$p_2$")
)
