library(ggplot2)
library(gridExtra)

BAR_COLOR <- c(rgb(32, 43, 50, maxColorValue = 255))
BAR_DEF <- geom_bar(stat = "identity", fill = BAR_COLOR, width = 0.75)
COLOR_VALS <- c("#d44345", "#ffb641", "#ffff00", "#0bc986", "#0bc986")

gen_multi_plot_four <- function(
        pp1, pp2, pp3, pp4, y, x1, x2, x3, x4, filename
    ) {
    fpp1 <- pp1 + BAR_DEF + coord_flip() + xlab(y) + ylab(x1) + scale_color_manual(values = color_mapping)
    fpp2 <- pp2 + BAR_DEF + coord_flip() + xlab(y) + ylab(x2) + scale_color_manual(values = color_mapping)
    fpp3 <- pp3 + BAR_DEF + coord_flip() + xlab(y) + ylab(x3) + scale_color_manual(values = color_mapping)
    fpp4 <- pp4 + BAR_DEF + coord_flip() + xlab(y) + ylab(x4) + scale_color_manual(values = color_mapping)
    combined_plot <- grid.arrange(fpp1, fpp2, fpp3, fpp4, ncol = 2)
    ggsave(combined_plot, file = filename, width = 12, height = 6)
}

gen_multi_plot_two <- function(pp1, pp2, y, x1, x2, filename) {
    fpp1 <- pp1 + BAR_DEF + coord_flip() + xlab(y) + ylab(x1) + scale_color_manual(values = color_mapping)
    fpp2 <- pp2 + BAR_DEF + coord_flip() + xlab(y) + ylab(x2) + scale_color_manual(values = color_mapping)
    combined_plot <- grid.arrange(fpp1, fpp2, ncol = 1)
    ggsave(combined_plot, file = filename, width = 12, height = 6)
}

input <- read.csv(file = "cumulative_res.csv", header = TRUE, sep = ",", check.name = FALSE)

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
gen_multi_plot_four(p1, p2, p3, p4, "instance_set", "avg TP", "avg TN", "avg FP", "avg FN", "confusion_matrix.png")

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "fp_dev_mean", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "fp_dev_max", color = "gt_match", group = "gt_match"
    )
)

# fault path dev multiplot
gen_multi_plot_two(p1, p2, "instance_set", "avg fault path dev", "max fault path dev", "fault_path_dev.png")

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
gen_multi_plot_four(p1, p2, p3, p4, "instance_set", "avg accuracy", "avg precision", "avg recall", "avg F1", "eval_metrics.png")

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
    "instance_set",
    "avg anomaly link percentage",
    "avg false positives (regular components treated as anomalies)",
    "avg ratio of found ground truth fault paths",
    "avg false negatives (missed anomalies)",
    "gt_analysis.png"
)

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_num_fault_paths", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "max_num_fault_paths", color = "gt_match", group = "gt_match"
    )
)

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
gen_multi_plot_four(p1, p2, p3, p4, "instance_set", "avg num of fault paths", "max num of fault paths", "avg fault path len", "max fault path len", "fault_paths.png")


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
    "instance_set",
    "avg classification ratio",
    "avg false positives (regular components treated as anomalies)",
    "avg runtime (s)",
    "avg false negatives (missed anomalies)",
    "classification_ratio.png"
)
