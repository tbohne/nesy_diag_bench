library(ggplot2)
library(gridExtra)
library(dplyr)
library(latex2exp)
library(cowplot)

PT_DEF <- geom_point(size=5)
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

# extract legend from a ggplot
extract_legend <- function(plot) {
    tmp <- ggplot_gtable(ggplot_build(plot))
    leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box")
    legend <- tmp$grobs[[leg]]
    return(legend)
}

gen_multi_plot_six <- function(
        pp1, pp2, pp3, pp4, pp5, pp6,
        y1, y2, y3, y4, y5, y6,
        x1, x2, x3, x4, x5, x6,
        filename, group_name
    ) {
    fpp1 <- pp1 + PT_DEF + xlab(x1) + ylab(y1) + scale_color_manual(values = color_mapping) + labs(color = group_name) + GENERAL_THEME
    fpp2 <- pp2 + PT_DEF + xlab(x2) + ylab(y2) + scale_color_manual(values = color_mapping) + labs(color = group_name) + GENERAL_THEME
    fpp3 <- pp3 + PT_DEF + xlab(x3) + ylab(y3) + scale_color_manual(values = color_mapping) + labs(color = group_name) + GENERAL_THEME
    fpp4 <- pp4 + PT_DEF + xlab(x4) + ylab(y4) + scale_color_manual(values = color_mapping) + labs(color = group_name) + GENERAL_THEME
    fpp5 <- pp5 + PT_DEF + xlab(x5) + ylab(y5) + scale_color_manual(values = color_mapping) + labs(color = group_name) + GENERAL_THEME
    fpp6 <- pp6 + PT_DEF + xlab(x6) + ylab(y6) + scale_color_manual(values = color_mapping) + labs(color = group_name) + GENERAL_THEME

    # extract legend from one of the plots (avoid redundant legends)
    legend <- extract_legend(fpp1 + theme(legend.position = "bottom"))

    combined_plot <- plot_grid(
        fpp1, fpp2, fpp3, fpp4, fpp5, fpp6, ncol = 3, align = 'h', axis = 'h',
        rel_widths = c(1, 1, 1)
    )

    # add shared legend
    final_plot <- plot_grid(
        combined_plot, legend, ncol = 1, rel_heights = c(1, 0.05)
    ) + theme(plot.background = element_rect(fill = "white", color = NA))

    ggsave(final_plot, file = filename, width = 12, height = 8)
}

gen_multi_plot_two <- function(
        pp1, pp2, y1, y2, x1, x2, filename, group_name
    ) {
    fpp1 <- pp1 + PT_DEF + xlab(x1) + ylab(y1) + scale_color_manual(values = color_mapping) + labs(color = group_name)
    fpp2 <- pp2 + PT_DEF + xlab(x2) + ylab(y2) + scale_color_manual(values = color_mapping) + labs(color = group_name)
    combined_plot <- grid.arrange(fpp1, fpp2, ncol = 2)
    ggsave(combined_plot, file = filename, width = 12, height = 6)
}

# actual compensation insights

input <- read.csv(
    file = "meta_analysis.csv", header = TRUE, sep = ",", check.name = FALSE
)

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
        x = "anomaly_link_perc_scores",
        y = "avg_ratio_gtfp",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "compensation_ano_link",
        y = "anomaly_perc_aff_by_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "anomaly_perc_aff_by_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "anomaly_perc_aff_by_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "compensation_ano_link",
        y = "compensation_gtfp",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "compensation_gtfp",
        y = "anomaly_perc_aff_by_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\bar{p_1}^i$"), # y1
    TeX("$\\alpha / \\beta$"), # y2
    TeX("$\\alpha / \\beta$"), # y3
    TeX("$\\alpha / \\beta$"), # y4
    TeX("$|\\bar{p_1}^i - \\bar{F1}|$"), # y5
    TeX("$\\alpha / \\beta$"), # y6
    TeX("$\\bar{p_0}^i$"), # x1
    TeX("$|\\bar{p_0}^i - \\bar{F1}|$"), # x2
    TeX("$\\bar{p_0}^i$"), # x3
    TeX("$\\bar{p_1}^i$"), # x4
    TeX("$|\\bar{p_0}^i - \\bar{F1}|$"), # x5
    TeX("$|\\bar{p_1}^i - \\bar{F1}|$"), # x6
    "compensation_analysis.png",
    TeX("$p_2^i$")
)

# same with prod #############################

p1 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "avg_ratio_gtfp",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "compensation_ano_link",
        y = "anomaly_perc_aff_by_prod",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "anomaly_perc_aff_by_prod",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "anomaly_perc_aff_by_prod",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "compensation_ano_link",
        y = "compensation_gtfp",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "compensation_gtfp",
        y = "anomaly_perc_aff_by_prod",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\bar{p_1}^i$"), # y1
    TeX("$\\alpha \\beta$"), # y2
    TeX("$\\alpha \\beta$"), # y3
    TeX("$\\alpha \\beta$"), # y4
    TeX("$|\\bar{p_1}^i - \\bar{F1}|$"), # y5
    TeX("$\\alpha \\beta$"), # y6
    TeX("$\\bar{p_0}^i$"), # x1
    TeX("$|\\bar{p_0}^i - \\bar{F1}|$"), # x2
    TeX("$\\bar{p_0}^i$"), # x3
    TeX("$\\bar{p_1}^i$"), # x4
    TeX("$|\\bar{p_0}^i - \\bar{F1}|$"), # x5
    TeX("$|\\bar{p_1}^i - \\bar{F1}|$"), # x6
    "compensation_analysis_prod.png",
    TeX("$p_2^i$")
)

##############################################

p1 <- ggplot(
    data = input, aes_string(
        x = "f1_scores",
        y = "anomaly_link_perc_scores",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "f1_scores",
        y = "avg_ratio_gtfp",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "f1_scores",
        y = "num_classifications",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "gt_match_perc",
        y = "sum_of_avg_fault_paths_and_dev",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "sum_of_avg_fault_paths_and_dev",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "sum_of_avg_fault_paths_and_dev",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\bar{p_0}^i$"), # y1
    TeX("$\\bar{p_1}^i$"), # y2
    TeX("$\\bar{n_c}^i$"), # y3
    TeX("$f^a_i + \\tilde{f^a_i}$"), # y4
    TeX("$f^a_i + \\tilde{f^a_i}$"), # y5
    TeX("$f^a_i + \\tilde{f^a_i}$"), # y6
    TeX("$\\bar{F1}$"), # x1
    TeX("$\\bar{F1}$"), # x2
    TeX("$\\bar{F1}$"), # x3
    TeX("$p_2^i$"), # x4
    TeX("$\\bar{p_1}^i$"), # x5
    TeX("$\\bar{p_0}^i$"), # x6
    "f1_end_res_corr.png",
    TeX("$p_2^i$")
)

# model acc - connectivity - performance

p1 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "model_acc_connectivity_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "model_acc_connectivity_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "gt_match_perc",
        y = "model_acc_connectivity_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "diag_success_percentage",
        y = "model_acc_connectivity_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_mean",
        y = "model_acc_connectivity_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_max",
        y = "model_acc_connectivity_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\gamma / \\beta $"), # y1
    TeX("$\\gamma / \\beta $"), # y2
    TeX("$\\gamma / \\beta $"), # y3
    TeX("$\\gamma / \\beta $"), # y4
    TeX("$\\gamma / \\beta $"), # y5
    TeX("$\\gamma / \\beta $"), # y6
    TeX("$\\bar{p_0}^i$"), # x1
    TeX("$\\bar{p_1}^i$"), # x2
    TeX("$p_2^i$"), # x3
    TeX("$d_s^i$"), # x4
    TeX("$\\tilde{f^a_i}$"), # x5
    TeX("$\\tilde{f^{max}_i}$"), # x6
    "modelacc_connectivity_performance.png",
    TeX("$p_2^i$")
)

# how many classifications and how acc models

p1 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "num_classifications_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "num_classifications_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "gt_match_perc",
        y = "num_classifications_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "diag_success_percentage",
        y = "num_classifications_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_mean",
        y = "num_classifications_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_max",
        y = "num_classifications_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\bar{n_c}^i / \\gamma$"), # y1
    TeX("$\\bar{n_c}^i / \\gamma$"), # y2
    TeX("$\\bar{n_c}^i / \\gamma$"), # y3
    TeX("$\\bar{n_c}^i / \\gamma$"), # y4
    TeX("$\\bar{n_c}^i / \\gamma$"), # y5
    TeX("$\\bar{n_c}^i / \\gamma$"), # y6
    TeX("$\\bar{p_0}^i$"), # x1
    TeX("$\\bar{p_1}^i$"), # x2
    TeX("$p_2^i$"), # x3
    TeX("$d_s^i$"), # x4
    TeX("$\\tilde{f^a_i}$"), # x5
    TeX("$\\tilde{f^{max}_i}$"), # x6
    "num_classifications_model_acc.png",
    TeX("$p_2^i$")
)

# affected_by against perf

p1 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "gt_match_perc",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "diag_success_percentage",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_mean",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_max",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\beta$"), # y1
    TeX("$\\beta$"), # y2
    TeX("$\\beta$"), # y3
    TeX("$\\beta$"), # y4
    TeX("$\\beta$"), # y5
    TeX("$\\beta$"), # y6
    TeX("$\\bar{p_0}^i$"), # x1
    TeX("$\\bar{p_1}^i$"), # x2
    TeX("$p_2^i$"), # x3
    TeX("$d_s^i$"), # x4
    TeX("$\\tilde{f^a_i}$"), # x5
    TeX("$\\tilde{f^{max}_i}$"), # x6
    "aff_by_perf.png",
    TeX("$p_2^i$")
)

# model_acc against perf

p1 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "gt_match_perc",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "diag_success_percentage",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_mean",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_max",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\gamma$"), # y1
    TeX("$\\gamma$"), # y2
    TeX("$\\gamma$"), # y3
    TeX("$\\gamma$"), # y4
    TeX("$\\gamma$"), # y5
    TeX("$\\gamma$"), # y6
    TeX("$\\bar{p_0}^i$"), # x1
    TeX("$\\bar{p_1}^i$"), # x2
    TeX("$p_2^i$"), # x3
    TeX("$d_s^i$"), # x4
    TeX("$\\tilde{f^a_i}$"), # x5
    TeX("$\\tilde{f^{max}_i}$"), # x6
    "model_acc_perf.png",
    TeX("$p_2^i$")
)

# anomaly_perc against perf

p1 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "gt_match_perc",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "diag_success_percentage",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_mean",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_max",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\alpha$"), # y1
    TeX("$\\alpha$"), # y2
    TeX("$\\alpha$"), # y3
    TeX("$\\alpha$"), # y4
    TeX("$\\alpha$"), # y5
    TeX("$\\alpha$"), # y6
    TeX("$p_0$"), # x1
    TeX("$p_1$"), # x2
    TeX("$p_2$"), # x3
    TeX("$d_s$"), # x4
    TeX("$\\tilde{f^a_i}$"), # x5
    TeX("$\\tilde{f^{max}_i}$"), # x6
    "anomaly_perc_perf.png",
    TeX("$p_2$")
)

# anomaly_perc - model acc ratio against perf

p1 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "anomaly_perc_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "anomaly_perc_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "gt_match_perc",
        y = "anomaly_perc_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "diag_success_percentage",
        y = "anomaly_perc_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_mean",
        y = "anomaly_perc_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_max",
        y = "anomaly_perc_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\alpha / \\gamma$"), # y1
    TeX("$\\alpha / \\gamma$"), # y2
    TeX("$\\alpha / \\gamma$"), # y3
    TeX("$\\alpha / \\gamma$"), # y4
    TeX("$\\alpha / \\gamma$"), # y5
    TeX("$\\alpha / \\gamma$"), # y6
    TeX("$\\bar{p_0}^i$"), # x1
    TeX("$\\bar{p_1}^i$"), # x2
    TeX("$p_2^i$"), # x3
    TeX("$d_s^i$"), # x4
    TeX("$\\tilde{f^a_i}$"), # 5
    TeX("$\\tilde{f^{max}_i}$"), # x6
    "anomaly_perc_model_acc_ratio_perf.png",
    TeX("$p_2^i$")
)

# num classifications against perf

p1 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "num_classifications",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "num_classifications",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "gt_match_perc",
        y = "num_classifications",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "diag_success_percentage",
        y = "num_classifications",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_mean",
        y = "num_classifications",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "fp_dev_max",
        y = "num_classifications",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$n_c$"), # y1
    TeX("$n_c$"), # y2
    TeX("$n_c$"), # y3
    TeX("$n_c$"), # y4
    TeX("$n_c$"), # y5
    TeX("$n_c$"), # y6
    TeX("$p_0$"), # x1
    TeX("$p_1$"), # x2
    TeX("$p_2$"), # x3
    TeX("$d_s$"), # x4
    TeX("$\\tilde{f^a_i}$"), # x5
    TeX("$\\tilde{f^{max}_i}$"), # x6
    "num_classifications_perf.png",
    TeX("$p_2$")
)

# num classifications - model acc -- filtered based on avg_ratio_gtfp

p1 <- ggplot(
    data = input, aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, avg_ratio_gtfp >= 0.7)

p2 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, avg_ratio_gtfp >= 0.75)

p3 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, avg_ratio_gtfp >= 0.8)

p4 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, avg_ratio_gtfp >= 0.9)

p5 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- input %>%
  group_by(avg_model_acc) %>%
  filter(avg_ratio_gtfp == max(avg_ratio_gtfp))

p6 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\gamma$"), #y1
    TeX("$\\gamma$"), #y2
    TeX("$\\gamma$"), #y3
    TeX("$\\gamma$"), #y4
    TeX("$\\gamma$"), #y5
    TeX("$\\gamma$"), #y6
    TeX("$\\bar{n_c}^i$"), #x1
    # filtered based on diff p1 thresholds
    TeX("$\\bar{n_c}^i (\\bar{p_1}^i \\geq 0.7)$"), #x2
    TeX("$\\bar{n_c}^i (\\bar{p_1}^i \\geq 0.75)$"), #x3
    TeX("$\\bar{n_c}^i (\\bar{p_1}^i \\geq 0.8)$"), #x4
    TeX("$\\bar{n_c}^i (\\bar{p_1}^i \\geq 0.9)$"), #x5
    TeX("$\\bar{n_c}^i (\\max \\bar{p_1}^i)$"), #x6
    "model_acc_classifications.png",
    TeX("$p_2^i$")
)

# num classifications - model acc -- filtered based on anomaly_link_perc_scores

p1 <- ggplot(
    data = input, aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, anomaly_link_perc_scores >= 0.7)

p2 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, anomaly_link_perc_scores >= 0.75)

p3 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, anomaly_link_perc_scores >= 0.8)

p4 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, anomaly_link_perc_scores >= 0.9)

p5 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- input %>%
  group_by(avg_model_acc) %>%
  filter(anomaly_link_perc_scores == max(anomaly_link_perc_scores))

p6 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\gamma$"), #y1
    TeX("$\\gamma$"), #y2
    TeX("$\\gamma$"), #y3
    TeX("$\\gamma$"), #y4
    TeX("$\\gamma$"), #y5
    TeX("$\\gamma$"), #y6
    TeX("$\\bar{n_c}^i$"), #x1
    TeX("$\\bar{n_c}^i (\\bar{p_0}^i \\geq 0.7)$"), #x2
    TeX("$\\bar{n_c}^i (\\bar{p_0}^i \\geq 0.75)$"), #x3
    TeX("$\\bar{n_c}^i (\\bar{p_0}^i \\geq 0.8)$"), #x4
    TeX("$\\bar{n_c}^i (\\bar{p_0}^i \\geq 0.9)$"), #x5
    TeX("$\\bar{n_c}^i (\\max \\bar{p_0}^i)$"), #x6
    "model_acc_classifications_ano_link.png",
    TeX("$p_2^i$")
)

# num classifications - model acc -- filtered based on gt_match_perc

p1 <- ggplot(
    data = input, aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, gt_match_perc >= 70)

p2 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, gt_match_perc >= 75)

p3 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, gt_match_perc >= 80)

p4 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, gt_match_perc >= 90)

p5 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- input %>%
  group_by(avg_model_acc) %>%
  filter(gt_match_perc == max(gt_match_perc))

p6 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "num_classifications",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\gamma$"), #y1
    TeX("$\\gamma$"), #y2
    TeX("$\\gamma$"), #y3
    TeX("$\\gamma$"), #y4
    TeX("$\\gamma$"), #y5
    TeX("$\\gamma$"), #y6
    TeX("$\\bar{n_c}^i$"), #x1
    TeX("$\\bar{n_c}^i (p_2^i \\geq 0.7)$"), #x2
    TeX("$\\bar{n_c}^i (p_2^i \\geq 0.75)$"), #x3
    TeX("$\\bar{n_c}^i (p_2^i \\geq 0.8)$"), #x4
    TeX("$\\bar{n_c}^i (p_2^i \\geq 0.9)$"), #x5
    TeX("$\\bar{n_c}^i (\\max p_2^i)$"), #x6
    "model_acc_classifications_gt_match_perc.png",
    TeX("$p_2^i$")
)

# correlation affected-by and fault path len / num fault paths

p1 <- ggplot(
    data = input, aes_string(
        x = "avg_num_fault_paths",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_fault_path_len",
        y = "avg_num_fault_paths",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "avg_num_fault_paths",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "avg_fault_path_len",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "avg_num_fault_paths",
        y = "anomaly_perc_aff_by_prod",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "avg_fault_path_len",
        y = "anomaly_perc_aff_by_prod",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\beta$"), # y1
    TeX("$f^a_i$"), # y2
    TeX("$\\alpha$"), # y3
    TeX("$\\alpha$"), # y4
    TeX("$\\alpha \\beta$"), # y5
    TeX("$\\alpha \\beta$"), # y6
    TeX("$f^a_i$"), # x1
    TeX("$l^a_i$"), # x2
    TeX("$f^a_i$"), # x3
    TeX("$l^a_i$"), # x4
    TeX("$f^a_i$"), # x5
    TeX("$l^a_i$"), # x6
    "correlation_anomaly_perc_aff_by_prod_fault_paths.png",
    TeX("$p_2^i$")
)

# correlation (median + mean) runtime and fault path len / num fault paths

p1 <- ggplot(
    data = input, aes_string(
        x = "avg_num_fault_paths",
        y = "`avg_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_fault_path_len",
        y = "`avg_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "avg_num_fault_paths",
        y = "`median_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "avg_fault_path_len",
        y = "`median_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "median_fault_path_len",
        y = "`median_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "median_num_fault_paths",
        y = "`median_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$r^a_i$ (s)"), # y1
    TeX("$r^a_i$ (s)"), # y2
    TeX("$r^m_i$ (s)"), # y3
    TeX("$r^m_i$ (s)"), # y4
    TeX("$r^m_i$ (s)"), # y5
    TeX("$r^m_i$ (s)"), # y6
    TeX("$f^a_i$"), # x1
    TeX("$l^a_i$"), # x2
    TeX("$f^a_i$"), # x3
    TeX("$l^a_i$"), # x4
    TeX("$l^m_i$"), # x5
    TeX("$f^m_i$"), # x6
    "correlation_runtime_fault_paths.png",
    TeX("$p_2^i$")
)

# correlation (median + mean + max) runtime and sum of (mean + max) fp + fp dev

p1 <- ggplot(
    data = input, aes_string(
        x = "sum_of_avg_fault_paths_and_dev",
        y = "`avg_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "sum_of_max_fault_paths_and_dev",
        y = "`max_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "sum_of_avg_fault_paths_and_dev",
        y = "`median_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "sum_of_avg_fault_paths_and_dev",
        y = "`max_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "sum_of_max_fault_paths_and_dev",
        y = "`avg_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "sum_of_max_fault_paths_and_dev",
        y = "`median_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$r^a_i$ (s)"), # y1
    TeX("$r^{max}_i$ (s)"), # y2
    TeX("$r^m_i$ (s)"), # y3
    TeX("$r^{max}_i$ (s)"), # y4
    TeX("$r^a_i$ (s)"), # y5
    TeX("$r^m_i$ (s)"), # y6
    TeX("$f^a_i + \\tilde{f^a_i}$"), # x1
    TeX("$f^{max}_i + \\tilde{f^{max}_i}$"), # x2
    TeX("$f^a_i + \\tilde{f^a_i}$"), # x3
    TeX("$f^a_i + \\tilde{f^a_i}$"), # x4
    TeX("$f^{max}_i + \\tilde{f^{max}_i}$"), # x5
    TeX("$f^{max}_i + \\tilde{f^{max}_i}$"), # x6
    "correlation_runtime_fault_paths_sum.png",
    TeX("$p_2^i$")
)

# correlation alpha, beta, gamma vs. FPs

p1 <- ggplot(
    data = input, aes_string(
        x = "avg_fp",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_fp",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "avg_fp",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "avg_fp",
        y = "anomaly_perc_aff_by_model_acc_aggregation",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, avg_model_acc < 1)

p5 <- ggplot(
    data = filtered_data, aes_string(
        x = "avg_fp",
        y = "anomaly_perc_aff_by_model_acc_aggregation",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "avg_fp",
        y = "num_classifications_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\alpha$"), # y1
    TeX("$\\beta$"), # y2
    TeX("$\\gamma$"), # y3
    TeX("$(\\alpha + \\beta) / \\gamma$"), # y4
    TeX("$(\\alpha + \\beta) / \\gamma$"), # y5
    TeX("$\\bar{n_c}^i / \\gamma$"), # y6
    TeX("$\\bar{FP}$"), # x1
    TeX("$\\bar{FP}$"), # x2
    TeX("$\\bar{FP}$"), # x3
    TeX("$\\bar{FP}$"), # x4
    TeX("$\\bar{FP} (\\gamma \\neq 1.0)$"), # x5
    TeX("$\\bar{FP}$"), # x6
    "anomaly_perc_aff_by_model_acc_aggregation.png",
    TeX("$p_2^i$")
)

# correlation alpha, beta, gamma vs. FNs

p1 <- ggplot(
    data = input, aes_string(
        x = "avg_fn",
        y = "anomaly_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_fn",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "avg_fn",
        y = "avg_model_acc",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "avg_fn",
        y = "anomaly_perc_model_acc_aggregation",
        color = "gt_match",
        group = "gt_match"
    )
)

filtered_data <- subset(input, avg_model_acc < 1)

p5 <- ggplot(
    data = filtered_data, aes_string(
        x = "avg_fn",
        y = "anomaly_perc_model_acc_aggregation",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "avg_fn",
        y = "num_classifications_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\alpha$"), # y1
    TeX("$\\beta$"), # y2
    TeX("$\\gamma$"), # y3
    TeX("$\\alpha / \\gamma$"), # y4
    TeX("$\\alpha / \\gamma$"), # y5
    TeX("$\\bar{n_c}^i / \\gamma$"), # y6
    TeX("$\\bar{FN}$"), # x1
    TeX("$\\bar{FN}$"), # x2
    TeX("$\\bar{FN}$"), # x3
    TeX("$\\bar{FN}$"), # x4
    TeX("$\\bar{FN} (\\gamma \\neq 1.0)$"), # x5
    TeX("$\\bar{FN}$"), # x6
    "anomaly_perc_aff_by_model_acc_aggregation_fn.png",
    TeX("$p_2^i$")
)

# correlation missed anomalies vs. performance

p1 <- ggplot(
    data = input, aes_string(
        x = "all_missed_anomalies",
        y = "anomaly_link_perc_scores",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "missed_anomalies_unclassified",
        y = "anomaly_link_perc_scores",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "miss_due_to_class_iss",
        y = "anomaly_link_perc_scores",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "all_missed_anomalies",
        y = "avg_ratio_gtfp",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "missed_anomalies_unclassified",
        y = "avg_ratio_gtfp",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "miss_due_to_class_iss",
        y = "avg_ratio_gtfp",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\bar{p_0}^i$"), # y1
    TeX("$\\bar{p_0}^i$"), # y2
    TeX("$\\bar{p_0}^i$"), # y3
    TeX("$\\bar{p_1}^i$"), # y4
    TeX("$\\bar{p_1}^i$"), # y5
    TeX("$\\bar{p_1}^i$"), # y6
    TeX("$\\bar{m_3}^i$"), # x1
    TeX("$\\bar{m_2}^i$"), # x2
    TeX("$\\bar{m_1}^i$"), # x3
    TeX("$\\bar{m_3}^i$"), # x4
    TeX("$\\bar{m_2}^i$"), # x5
    TeX("$\\bar{m_1}^i$"), # x6
    "correlation_missed_anomalies_perf.png",
    TeX("$p_2^i$")
)

# correlation compensation metrics

p1 <- ggplot(
    data = input, aes_string(
        x = "avg_compensation_by_aff_by_savior",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_missed_chances",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "avg_no_second_chance",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "avg_compensation_by_aff_by_savior",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "avg_compensation_by_aff_by_savior",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "avg_missed_chances",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\beta$"), # y1
    TeX("$\\beta$"), # y2
    TeX("$\\beta$"), # y3
    TeX("$\\bar{c_1}^i$"), # y4
    TeX("$\\bar{c_1}^i$"), # y5
    TeX("$\\bar{c_2}^i$"), # y6
    TeX("$\\bar{c_1}^i$"), # x1
    TeX("$\\bar{c_2}^i$"), # x2
    TeX("$\\bar{c_3}^i$"), # x3
    TeX("$\\bar{p_0}^i$"), # x4
    TeX("$\\bar{p_1}^i$"), # x5
    TeX("$\\bar{p_1}^i$"), # x6
    "correlation_compensation_metrics.png",
    TeX("$p_2^i$")
)

# correlation compensation metrics (with alpha=0.2)
filtered_data <- subset(input, anomaly_perc>=20.0)

p1 <- ggplot(
    data = filtered_data, aes_string(
        x = "avg_compensation_by_aff_by_savior",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = filtered_data, aes_string(
        x = "avg_missed_chances",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = filtered_data, aes_string(
        x = "avg_no_second_chance",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = filtered_data, aes_string(
        x = "anomaly_link_perc_scores",
        y = "avg_compensation_by_aff_by_savior",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = filtered_data, aes_string(
        x = "avg_ratio_gtfp",
        y = "avg_compensation_by_aff_by_savior",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = filtered_data, aes_string(
        x = "avg_ratio_gtfp",
        y = "avg_missed_chances",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\beta$"), # y1
    TeX("$\\beta$"), # y2
    TeX("$\\beta$"), # y3
    TeX("$\\bar{c_1}^i$"), # y4
    TeX("$\\bar{c_1}^i$"), # y5
    TeX("$\\bar{c_2}^i$"), # y6
    TeX("$\\bar{c_1}^i$"), # x1
    TeX("$\\bar{c_2}^i$"), # x2
    TeX("$\\bar{c_3}^i$"), # x3
    TeX("$\\bar{p_0}^i$"), # x4
    TeX("$\\bar{p_1}^i$"), # x5
    TeX("$\\bar{p_1}^i$"), # x6
    "correlation_compensation_metrics_alpha20.png",
    TeX("$p_2^i$")
)

# "best of" correlation plots

p1 <- ggplot(
    data = input, aes_string(
        x = "anomaly_link_perc_scores",
        y = "f1_scores",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "avg_ratio_gtfp",
        y = "f1_scores",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "sum_of_max_fault_paths_and_dev",
        y = "`max_runtime (s)`",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "gt_match_perc",
        y = "num_classifications_model_acc_ratio",
        color = "gt_match",
        group = "gt_match"
    )
)

# compensation for a=0.2 -- beta vs. comp by savior
filtered_data <- subset(input, anomaly_perc>=20.0)
p5 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "avg_compensation_by_aff_by_savior",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

# increased potential for misclassifications with greater beta (again, a=0.2)
filtered_data <- subset(input, anomaly_perc>=20.0)
filtered_data <- subset(filtered_data, avg_model_acc<=0.95)
p6 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "avg_misclassifications",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$F1$"), # y1
    TeX("$F1$"), # y2
    TeX("$r^{max}_i$ (s)"), # y3
    TeX("$n_c / \\gamma$"), # y4
    TeX("$\\beta$"), # y5
    TeX("$\\beta$"), # y6
    TeX("$p_0$"), # x1
    TeX("$p_1$"), # x2
    TeX("$f^{max}_i + \\tilde{f^{max}_i}$"), # x3
    TeX("$p_2$"), # x4
    TeX("$\\bar{c_1} (\\alpha=0.2)$"), # x5
    TeX("$\\bar{FP} + \\bar{FN} (\\alpha=0.2, \\gamma \\leq 0.95)$"), # x6
    "best_of_corr.png",
    TeX("$p_2$")
)

# 𝛼 = 0.2 and 𝛾 ∈ [0.95, 0.99] to analyze the isolated impact of increasing 𝛽
filtered_data <- subset(input, anomaly_perc>=20.0)
filtered_data <- subset(filtered_data, avg_model_acc<=0.99)
filtered_data <- subset(filtered_data, avg_model_acc>=0.95)

p1 <- ggplot(
    data = filtered_data, aes_string(
        x = "avg_misclassifications",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = filtered_data, aes_string(
        x = "anomaly_link_perc_scores",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p3 <- ggplot(
    data = filtered_data, aes_string(
        x = "avg_ratio_gtfp",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p4 <- ggplot(
    data = filtered_data, aes_string(
        x = "gt_match_perc",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p5 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "avg_compensation_by_aff_by_savior",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

p6 <- ggplot(
    data = filtered_data,
    aes_string(
        x = "avg_missed_chances",
        y = "affected_by_perc",
        color = "gt_match",
        group = "gt_match"
    )
)

gen_multi_plot_six(
    p1, p2, p3, p4, p5, p6,
    TeX("$\\beta$"), # y1
    TeX("$\\beta$"), # y2
    TeX("$\\beta$"), # y3
    TeX("$\\beta$"), # y4
    TeX("$\\beta$"), # y5
    TeX("$\\beta$"), # y6
    TeX("$\\bar{FP} + \\bar{FN} (\\alpha \\geq 0.2, \\gamma \\in \\[0.95, 0.99\\])$"), # x1
    TeX("$\\bar{p_0}^i (\\alpha \\geq 0.2, \\gamma \\in \\[0.95, 0.99\\])$"), # x2
    TeX("$\\bar{p_1}^i (\\alpha \\geq 0.2, \\gamma \\in \\[0.95, 0.99\\])$"), # x3
    TeX("$p_2^i (\\alpha \\geq 0.2, \\gamma \\in \\[0.95, 0.99\\])$"), # x4
    TeX("$\\bar{c_1}^i (\\alpha \\geq 0.2, \\gamma \\in \\[0.95, 0.99\\])$"), # x5
    TeX("$\\bar{c_2}^i (\\alpha \\geq 0.2, \\gamma \\in \\[0.95, 0.99\\])$"), # x6
    "beta_influence.png",
    TeX("$p_2^i$")
)
