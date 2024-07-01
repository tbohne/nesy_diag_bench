library(ggplot2)
library(gridExtra)
library(latex2exp)

BAR_COLOR <- c(rgb(32, 43, 50, maxColorValue = 255))
COLOR_VALS <- scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
BAR_DEF <- geom_bar(stat = "identity", fill = BAR_COLOR, width = 0.75)

gen_plot <- function(plot_points_pre, y_name, x_name, filename) {
    final_plot <- plot_points_pre + BAR_DEF + coord_flip() + xlab(x_name) + ylab(y_name) + COLOR_VALS
    ggsave(final_plot, file = filename, width = 6, height = 12)
}

gen_multi_plot_four <- function(
        pp1, pp2, pp3, pp4, y, x1, x2, x3, x4, filename, group_name
    ) {
    fpp1 <- pp1 + BAR_DEF + coord_flip() + xlab(y) + ylab(x1) + COLOR_VALS + labs(color = group_name)
    fpp2 <- pp2 + BAR_DEF + coord_flip() + xlab(y) + ylab(x2) + COLOR_VALS + labs(color = group_name)
    fpp3 <- pp3 + BAR_DEF + coord_flip() + xlab(y) + ylab(x3) + COLOR_VALS + labs(color = group_name)
    fpp4 <- pp4 + BAR_DEF + coord_flip() + xlab(y) + ylab(x4) + COLOR_VALS + labs(color = group_name)
    combined_plot <- grid.arrange(fpp1, fpp2, fpp3, fpp4, ncol = 4)
    ggsave(combined_plot, file = filename, width = 28, height = 14)
}

gen_fault_path_multi_plot <- function(
        pp1, pp2, pp3, pp4, y1, y2, y3, x1, x2, x3, x4, filename, group_name
    ) {
    fpp1 <- pp1 + BAR_DEF + coord_flip() + xlab(y1) + ylab(x1) + COLOR_VALS + labs(color = group_name)
    fpp2 <- pp2 + BAR_DEF + coord_flip() + xlab(y1) + ylab(x2) + COLOR_VALS + labs(color = group_name)
    fpp3 <- pp3 + geom_point(size=5) + xlab(x3) + ylab(y2) + COLOR_VALS + labs(color = group_name)
    fpp4 <- pp4 + geom_point(size=5) + xlab(x4) + ylab(y3) + COLOR_VALS + labs(color = group_name)
    combined_plot <- grid.arrange(fpp1, fpp2, fpp3, fpp4, ncol = 4)
    ggsave(combined_plot, file = filename, width = 28, height = 14)
}

input <- read.csv(file = "res.csv", header = TRUE, sep = ",", check.name = FALSE)

# fault path plots

p1 <- ggplot(
    data = input, aes_string(
        x = "instance", y = "avg_fp_len", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance", y = "`#fault_paths`", color = "gt_match", group = "gt_match"
    )
)

p3 <- ggplot(
    data = input, aes_string(
        x = "`#fault_paths`", y = "avg_fp_len", color = "gt_match", group = "gt_match",
        ymin = min("avg_fp_len"), ymax=max("avg_fp_len")
    )
)

p4 <- ggplot(
    data = input, aes_string(
        x = "`#fault_paths`", y = "`runtime (s)`", color = "gt_match", group = "gt_match",
        ymin = min("`runtime (s)`"), ymax=max("`runtime (s)`")
    )
)

gen_fault_path_multi_plot(
    p1, p2, p3, p4,
    TeX("instance set ($i \\in I$)"),
    TeX("$l^a_i$"),
    TeX("runtime (s)"),
    TeX("$l^a_i$"),
    "num of fault paths",
    "num of fault paths",
    "num of fault paths",
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
    TeX("$FP$ (regular components treated as anomalies)"),
    "runtime (s)",
    TeX("$FN$ (missed anomalies)"),
    "class_ratio.png",
    TeX("$p_2$")
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
