library(ggplot2)
library(gridExtra)

PT_DEF <- geom_point(size=5)
COLOR_VALS <- c("#d44345", "#ffb641", "#ffff00", "#ccff99", "#00ff00")

gen_multi_plot_four <- function(
        pp1, pp2, pp3, pp4, y1, y2, y3, y4, x1, x2, x3, x4, filename
    ) {
    fpp1 <- pp1 + PT_DEF + xlab(x1) + ylab(y1) + scale_color_manual(values = color_mapping)
    fpp2 <- pp2 + PT_DEF + xlab(x2) + ylab(y2) + scale_color_manual(values = color_mapping)
    fpp3 <- pp3 + PT_DEF + xlab(x3) + ylab(y3) + scale_color_manual(values = color_mapping)
    fpp4 <- pp4 + PT_DEF + xlab(x4) + ylab(y4) + scale_color_manual(values = color_mapping)
    combined_plot <- grid.arrange(fpp1, fpp2, fpp3, fpp4, ncol = 2)
    ggsave(combined_plot, file = filename, width = 12, height = 6)
}


# actual compensation insights

input <- read.csv(
    file = "compensation.csv", header = TRUE, sep = ",", check.name = FALSE
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
        x = "compensation",
        y = "avg_ratio_gtfp",
        color = "gt_match",
        group = "gt_match"
    )
)

p2 <- ggplot(
    data = input, aes_string(
        x = "compensation",
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

gen_multi_plot_four(
    p1, p2, p3, p4,
    "avg_ratio_gtfp",
    "anomaly_perc_aff_by_ratio",
    "anomaly_perc_aff_by_ratio",
    "anomaly_perc_aff_by_ratio",
    "compensation",
    "compensation",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "compensation_analysis.png"
)
