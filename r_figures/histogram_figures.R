library(ggplot2)
options(scipen = 999) # Turn off scientific notation

dta <- read.csv("nobigquery_annotations.csv", sep = "\t")

x_vals <- seq(0, length(dta$stargazers_count)-1)

p <- ggplot(data=dta, aes(x=x_vals, y=sort(stargazers_count+1)))
p <- p + geom_point()
p <- p + theme_bw()
p <- p + scale_y_log10(limits = c(1, 1e6), expand = c(0.2, 0))
p


p <- ggplot(data=dta, aes(stargazers_count+1))
p <- p + theme_bw()
p <- p + geom_histogram(bins=11)
p <- p + scale_x_log10()
p <- p + geom_vline(xintercept=6+1, col="red")
#p <- p + annotate("text", x=1000, y=2000, label= "We assert repositories are more \n likely to have a community if they \n have more than six stars (red line).")
p <- p + xlab("Number of Stars") + ylab("Number of Repositories") + ggtitle("Log Histogram of Stars per Repository")
p1 <- p
p

p <- ggplot(data=dta, aes(forks_count+1))
p <- p + theme_bw()
p <- p + geom_histogram(bins=11)
p <- p + scale_x_log10()
p <- p + geom_vline(xintercept=6+1, col="red")
#p <- p + annotate("text", x=1000, y=2000, label= "We assert repositories are more \n likely to have a community if they \n have more than six forks (red line).")
p <- p + xlab("Number of Forks") + ylab("Number of Repositories") + ggtitle("Log Histogram of Forks per Repository")
p2 <- p
p



p <- ggplot(data=dta, aes(forks_count+1, stargazers_count+1))
p <- p + theme_bw()
p <- p + geom_point()
p <- p + scale_x_log10() + scale_y_log10() + coord_fixed()
p <- p + scale_fill_viridis_c("Number of\nRepositories", trans="log10") + xlab("Number of Forks") + ylab("Number of Stars")
#p <- p + geom_abline(slope=1, intercept=0)
p <- p + geom_rect(aes(NULL,NULL,xmin=0+1,xmax=6+1, ymin=0+1,ymax=6+1), colour="red", size=0.5, alpha=0.0005, fill="white")
p

p <- ggplot(data=dta, aes(forks_count+1, stargazers_count+1))
p <- p + theme_bw()
p <- p + geom_bin2d(bins=22)
p <- p + scale_x_log10() + scale_y_log10() + coord_fixed()
p <- p + scale_fill_viridis_c("Number of\nRepositories", trans = "log2") + xlab("Number of Forks") + ylab("Number of Stars")
#p <- p + geom_abline(slope=1, intercept=0)
p <- p + geom_rect(aes(NULL,NULL,xmin=0+1,xmax=6+1, ymin=0+1,ymax=6+1), colour="red", size=0.5, alpha=0.0005, fill="white")
p3<-p
p

library(gridExtra)
grid.arrange(p1, p2, p3, ncol=3)

cor(dta$stargazers_count, dta$forks_count, method = 'pearson')

# Date for repositories with community

dta_with_community <- dta[dta$forks_count >= 6 | dta$stargazers_count >= 6,]

cor(dta_with_community$stargazers_count, dta_with_community$forks_count, method = 'pearson')

p <- ggplot(data=dta_with_community, aes(time_since_last_push / (86400*365))) # 86400 seconds in a day
p <- p + theme_bw()
p <- p + geom_histogram(bins=40)
p <- p + geom_vline(xintercept=0.5, col="red") # Six months
#p <- p + annotate("text", x=1000, y=2000, label= "We assert repositories are more \n likely to have a community if they \n have more than six forks (red line).")
p <- p + xlab("Years Since Last Push") + ylab("Number of Repositories") + ggtitle("Histogram of Time Since Last Push")
p <- p + xlim(c(0, 5))
p <- p + ylim(c(0, 300))
#p <- p + xlim(c(0.5, 5))
p


p <- ggplot(data=dta_with_community, aes((time_since_last_push + 1) / (86400*365), forks_count+1))
p <- p + theme_bw()
p <- p + geom_bin2d(bins=22)
p <- p + scale_y_log10()
p <- p + scale_fill_viridis_c("Number of\nRepositories", trans = "log2") + xlab("Time Since Last Push (Years)") + ylab("Number of Forks")
p <- p + xlim(c(0, 5))
#p <- p + geom_abline(slope=1, intercept=0)
p

cor(dta_with_community$time_since_last_push, dta_with_community$stargazers_count, method = 'pearson')

cor(dta$time_since_last_push, dta$stargazers_count, method = 'pearson')

# Cumulative distribution function
plot((quantile(dta_with_community$time_since_last_push / (86400*365), probs = seq(0, 1, by= 0.01))), type="l")


# Data of repos using sustainability supports, between six months and two years
dta_sus_supports <- dta_with_community[dta_with_community$time_since_last_push / (86400*365) >= 0.5 & dta_with_community$time_since_last_push / (86400*365) <= 2.0,]

View(dta_sus_supports)

write.csv(dta[,c(1, 6, 7, 12)], file = "sup2-annotated-data.csv", row.names = F)
write.csv(dta_sus_supports[,c(1)], file = "sup3-sustainabilty-support-needed.csv", row.names = F)

set.seed(42)
dss_rand_sample <- dta_sus_supports[sample(nrow(dta_sus_supports), 30), ]
