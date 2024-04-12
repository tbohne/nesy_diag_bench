library(ggplot2)
library(gridExtra)
library(dplyr)

PT_DEF <- geom_point(size=5)
COLOR_VALS <- c("#d44345", "#ffb641", "#ffff00", "#ccff99", "#00ff00")

gen_multi_plot_six <- function(
        pp1, pp2, pp3, pp4, pp5, pp6,
        y1, y2, y3, y4, y5, y6,
        x1, x2, x3, x4, x5, x6,
        filename
    ) {
    fpp1 <- pp1 + PT_DEF + xlab(x1) + ylab(y1) + scale_color_manual(values = color_mapping)
    fpp2 <- pp2 + PT_DEF + xlab(x2) + ylab(y2) + scale_color_manual(values = color_mapping)
    fpp3 <- pp3 + PT_DEF + xlab(x3) + ylab(y3) + scale_color_manual(values = color_mapping)
    fpp4 <- pp4 + PT_DEF + xlab(x4) + ylab(y4) + scale_color_manual(values = color_mapping)
    fpp5 <- pp5 + PT_DEF + xlab(x5) + ylab(y5) + scale_color_manual(values = color_mapping)
    fpp6 <- pp6 + PT_DEF + xlab(x6) + ylab(y6) + scale_color_manual(values = color_mapping)
    combined_plot <- grid.arrange(fpp1, fpp2, fpp3, fpp4, fpp5, fpp6, ncol = 3)
    ggsave(combined_plot, file = filename, width = 12, height = 6)
}

gen_multi_plot_two <- function(
        pp1, pp2, y1, y2, x1, x2, filename
    ) {
    fpp1 <- pp1 + PT_DEF + xlab(x1) + ylab(y1) + scale_color_manual(values = color_mapping)
    fpp2 <- pp2 + PT_DEF + xlab(x2) + ylab(y2) + scale_color_manual(values = color_mapping)
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
        x = "compensation_ano_link",
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
        x = "compensation_gtfp",
        y = "compensation_ano_link",
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
    "avg_ratio_gtfp",
    "anomaly_perc_aff_by_ratio",
    "anomaly_perc_aff_by_ratio",
    "anomaly_perc_aff_by_ratio",
    "compensation_ano_link",
    "anomaly_perc_aff_by_ratio",
    "compensation_ano_link",
    "compensation_ano_link",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "compensation_gtfp",
    "compensation_gtfp",
    "compensation_analysis.png"
)

# same with prod #############################

p1 <- ggplot(
    data = input, aes_string(
        x = "compensation_ano_link",
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
        x = "compensation_gtfp",
        y = "compensation_ano_link",
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
    "avg_ratio_gtfp",
    "anomaly_perc_aff_by_prod",
    "anomaly_perc_aff_by_prod",
    "anomaly_perc_aff_by_prod",
    "compensation_ano_link",
    "anomaly_perc_aff_by_prod",
    "compensation_ano_link",
    "compensation_ano_link",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "compensation_gtfp",
    "compensation_gtfp",
    "compensation_analysis_prod.png"
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

gen_multi_plot_two(
    p1, p2,
    "anomaly link perc",
    "avg ratio gtfp",
    "F1",
    "F1",
    "f1_end_res_corr.png"
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

gen_multi_plot_two(
    p1, p2,
    "model_acc_connectivity_ratio",
    "model_acc_connectivity_ratio",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "modelacc_connectivity_performance.png"
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

gen_multi_plot_two(
    p1, p2,
    "num_classifications_model_acc_ratio",
    "num_classifications_model_acc_ratio",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "num_classifications_model_acc.png"
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

gen_multi_plot_two(
    p1, p2,
    "affected_by_perc",
    "affected_by_perc",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "aff_by_perf.png"
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

gen_multi_plot_two(
    p1, p2,
    "avg_model_acc",
    "avg_model_acc",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "model_acc_perf.png"
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

gen_multi_plot_two(
    p1, p2,
    "anomaly_perc",
    "anomaly_perc",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "anomaly_perc_perf.png"
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

gen_multi_plot_two(
    p1, p2,
    "anomaly_perc_model_acc_ratio",
    "anomaly_perc_model_acc_ratio",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "anomaly_perc_model_acc_ratio_perf.png"
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

gen_multi_plot_two(
    p1, p2,
    "num_classifications",
    "num_classifications",
    "anomaly_link_perc_scores",
    "avg_ratio_gtfp",
    "num_classifications_perf.png"
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
    "avg_model_acc", #y1
    "avg_model_acc", #y2
    "avg_model_acc", #y3
    "avg_model_acc", #y4
    "avg_model_acc", #y5
    "avg_model_acc", #y6
    "classifications", #x1
    "classifications (filt. based on avg_ratio_gtfp 70%)", #x2
    "classifications (filt. based on avg_ratio_gtfp 75%)", #x3
    "classifications (filt. based on avg_ratio_gtfp 80%)", #x4
    "classifications (filt. based on avg_ratio_gtfp 90%)", #x5
    "classifications (filt. based on max avg_ratio_gtfp)", #x6
    "model_acc_classifications.png"
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
    "avg_model_acc", #y1
    "avg_model_acc", #y2
    "avg_model_acc", #y3
    "avg_model_acc", #y4
    "avg_model_acc", #y5
    "avg_model_acc", #y6
    "classifications", #x1
    "classifications (filt. based on ano_link_perc 70%)", #x2
    "classifications (filt. based on ano_link_perc 75%)", #x3
    "classifications (filt. based on ano_link_perc 80%)", #x4
    "classifications (filt. based on ano_link_perc 90%)", #x5
    "classifications (filt. based on max ano_link_perc)", #x6
    "model_acc_classifications_ano_link.png"
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
    "avg_model_acc", #y1
    "avg_model_acc", #y2
    "avg_model_acc", #y3
    "avg_model_acc", #y4
    "avg_model_acc", #y5
    "avg_model_acc", #y6
    "classifications", #x1
    "classifications (filt. based on gt_match_perc 70%)", #x2
    "classifications (filt. based on gt_match_perc 75%)", #x3
    "classifications (filt. based on gt_match_perc 80%)", #x4
    "classifications (filt. based on gt_match_perc 90%)", #x5
    "classifications (filt. based on max gt_match_perc)", #x6
    "model_acc_classifications_gt_match_perc.png"
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
        y = "affected_by_perc",
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
    "affected_by_perc", # y1
    "affected_by_perc", # y2
    "anomaly_perc", # y3
    "anomaly_perc", # y4
    "anomaly_perc_aff_by_prod", # y5
    "anomaly_perc_aff_by_prod", # y6
    "avg_num_fault_paths", # x1
    "avg_fault_path_len", # x2
    "avg_num_fault_paths", # x3
    "avg_fault_path_len", # x4
    "avg_num_fault_paths", # x5
    "avg_fault_path_len", # x6
    "correlation_anomaly_perc_aff_by_prod_fault_paths.png"
)