library(ggplot2)
library(nlme)

burns <- read.csv("../data/rangeland-burns-temps.csv")
burns$plot <- factor(burns$plot)

plot(burns[,c(7:10, 12:14, 16)])

ggplot(burns, aes(spcode, ptemp.sur)) +
    geom_boxplot() +
    facet_grid(. ~ plot)

ggsave("../results/ptemp-by-spcode-plot.pdf")

# for visualizing spcoide effect on residuals of plot effect

t.mod <- lm(ptemp.sur ~ plot, data=burns)
burns$ptemp.sur.resid <- residuals(t.mod)

ggplot(burns, aes(spcode, ptemp.sur.resid) ) +
    geom_boxplot()



## significant effect of species on peak temperature
ptemp.sur.mod <- lme(ptemp.sur ~ spcode, random = ~ 1 | plot, data = burns)
summary(ptemp.sur.mod)
anova(ptemp.sur.mod)


## PCAs
library(pcaMethods)

ndata <- burns[ rowSums( is.na(burns[, c(17:20) ]) ) != ncol(burns[, c(17:20)] ),]
ndata <- ndata[ rowSums( is.na(ndata[, c(7:10,12:14) ]) ) != ncol(ndata[, c(7:10,12:14)] ),]

plants <- ndata[, c(17:20)] # plant measurements
fire <- ndata[, c(7:10, 12:14)] # HOBO temperatures

plants.PCA <- pca(plants, nPcs=4, method="ppca", center=TRUE)
fire.PCA <- pca(fire, nPcs=4, method="ppca", center=TRUE)

summary(plants.PCA)
summary(fire.PCA)

slplot(fire.PCA)

slplot(plants.PCA)

allscores <- as.data.frame(cbind(scores(plants.PCA), scores(fire.PCA)))
#names(allscores) <- c(paste(names(plants.PCA), "p", sep="_"), paste(names(fire.PCA), "f", sep="_"))
plot(allscores)
