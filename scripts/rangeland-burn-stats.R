library(ggplot2)
library(nlme)

burns <- read.csv("../data/rangeland-burns-temps.csv")

plot(burns[,c(7:10, 12:14, 16)])

ggplot(burns, aes(spcode, ptemp.sur)) +
    geom_boxplot() +
    facet_grid(. ~ plot)
ggsave("../results/ptemp-by-spcode-plot.pdf")


## significant effect of species on peak temperature
ptemp.sur.mod <- lme(ptemp.sur ~ spcode, random = ~ 1 | plot, data = burns)
summary(ptemp.sur.mod)
anova(ptemp.sur.mod)

