library(ggplot2)
library(gridExtra)

BAR_COLOR <- c(rgb(32, 43, 50, maxColorValue = 255))
COLOR_VALS <- scale_color_manual(values = c("#d44345", "#0bc986", "#ffb641", "#33364d"))
BAR_DEF <- geom_bar(stat = "identity", fill = BAR_COLOR, width = 0.75)

gen_plot <- function(plot_points_pre, y_name, x_name, filename) {
    final_plot <- plot_points_pre + BAR_DEF + coord_flip() + xlab(x_name) + ylab(y_name) + COLOR_VALS
    ggsave(final_plot, file = filename, width = 6, height = 12)
}

gen_fault_path_multi_plot <- function(
        pp1, pp2, pp3, pp4, y1, y2, y3, x1, x2, x3, x4, filename
    ) {
    fpp1 <- pp1 + BAR_DEF + coord_flip() + xlab(y1) + ylab(x1) + COLOR_VALS
    fpp2 <- pp2 + BAR_DEF + coord_flip() + xlab(y1) + ylab(x2) + COLOR_VALS
    fpp3 <- pp3 + geom_point(size=5) + xlab(x3) + ylab(y2) + COLOR_VALS
    fpp4 <- pp4 + geom_point(size=5) + xlab(x4) + ylab(y3) + COLOR_VALS
    combined_plot <- grid.arrange(fpp1, fpp2, fpp3, fpp4, ncol = 4)
    ggsave(combined_plot, file = filename, width = 28, height = 14)
}

input <- read.csv(file = "res.csv", header = TRUE, sep = ",", check.name = FALSE)

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
    p1, p2, p3, p4, "instance", "avg fault path len", "runtime (s)", "avg fault path len", "num of fault paths",
    "num of fault paths", "num of fault paths", "fault_paths.png"
)
