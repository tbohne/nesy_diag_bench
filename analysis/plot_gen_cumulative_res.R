library(ggplot2)
library(gridExtra)

####################################################################################################
########################################### PLOTS ##################################################
####################################################################################################

gen_plot <- function(plot_points_pre, y_name, x_name, filename) {
    final_plot <- plot_points_pre + geom_bar(stat = "identity", fill = c(rgb(32, 43, 50, maxColorValue = 255)),
        width = 0.75) + coord_flip() + xlab(x_name) + ylab(y_name) + scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
    ggsave(final_plot, file = filename, width = 6, height = 4)
}

gen_multi_plot_four <- function(
        pp1, pp2, pp3, pp4, y, x1, x2, x3, x4, filename
    ) {
    fpp1 <- pp1 + geom_bar(stat = "identity", fill = c(rgb(32, 43, 50, maxColorValue = 255)),
        width = 0.75) + coord_flip() + xlab(y) + ylab(x1) + scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
    fpp2 <- pp2 + geom_bar(stat = "identity", fill = c(rgb(32, 43, 50, maxColorValue = 255)),
        width = 0.75) + coord_flip() + xlab(y) + ylab(x2) + scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
    fpp3 <- pp3 + geom_bar(stat = "identity", fill = c(rgb(32, 43, 50, maxColorValue = 255)),
        width = 0.75) + coord_flip() + xlab(y) + ylab(x3) + scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
    fpp4 <- pp4 + geom_bar(stat = "identity", fill = c(rgb(32, 43, 50, maxColorValue = 255)),
        width = 0.75) + coord_flip() + xlab(y) + ylab(x4) + scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
    combined_plot <- grid.arrange(fpp1, fpp2, fpp3, fpp4, ncol = 2)
    ggsave(combined_plot, file = filename, width = 12, height = 6)
}

gen_multi_plot_two <- function(pp1, pp2, y, x1, x2, filename) {
    fpp1 <- pp1 + geom_bar(stat = "identity", fill = c(rgb(32, 43, 50, maxColorValue = 255)),
        width = 0.75) + coord_flip() + xlab(y) + ylab(x1) + scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
    fpp2 <- pp2 + geom_bar(stat = "identity", fill = c(rgb(32, 43, 50, maxColorValue = 255)),
        width = 0.75) + coord_flip() + xlab(y) + ylab(x2) + scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
    combined_plot <- grid.arrange(fpp1, fpp2, ncol = 1)
    ggsave(combined_plot, file = filename, width = 12, height = 6)
}

input <- read.csv(file = "../cumulative_res.csv", header = TRUE, sep = ",")

# Instead of the percentage value factor(gt_match_perc) for which I'd need 100 colors, I only want to
# color / group them into 4 groups: 100%, [75, 100), [50, 75), [0, 50)

input$gt_match <- cut(
    input$gt_match_perc, breaks = c(0, 50, 75, 100, Inf), labels = c("[0,50)%", "[50,75)%", "[75,100)%", "100%"),
    include.lowest = TRUE, right = FALSE
)

# basic plots
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
gen_multi_plot_four(p1, p2, p3, p4, "instances_set", "avg TP", "avg TN", "avg FP", "avg FN", "confusion_matrix.png")

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
gen_multi_plot_two(p1, p2, "instances_set", "avg fault path dev", "max fault path dev", "fault_path_dev.png")

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
gen_multi_plot_four(p1, p2, p3, p4, "instances_set", "avg accuracy", "avg precision", "avg recall", "avg F1", "eval_metrics.png")

p1 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_ano_link_perc", color = "gt_match", group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "instance_set", y = "avg_model_acc", color = "gt_match", group = "gt_match"
    )
)

# anomaly link perc + model acc
gen_multi_plot_two(p1, p2, "instances_set", "avg anomaly link percentage", "avg model accuracy", "ano_link_model_acc.png")

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
gen_multi_plot_four(p1, p2, p3, p4, "instances_set", "avg num of fault paths", "max num of fault paths", "avg fault path len", "max fault path len", "fault_paths.png")
