shrink = 3
mex = shrink/1.255
linesx = 2.0


mypar <- function(mfrow) {
par(
    mfrow=mfrow,
    cex=(1/shrink),
    cex.axis=mex,
    cex.lab=mex,
    cex.main=mex,
    cex.sub=mex,
    mex=mex,
    lwd=(1/shrink),
    oma=c(0,0,0,0),
    xpd=NA,
    tcl=0.5,
    xaxs="i",
    yaxs="i",
    bty="n"
    )
}

col_width=3.25

height=col_width

packages = read.csv("packages.csv")
revpackages <- packages[rev(rownames(packages)),]
options(scipen=5)
npackages = length(packages$Count)
packagemax = max(packages$Count)

svg(filename="packages.svg", width=col_width, height=height, 
    family="Latin Modern Roman", pointsize=10)
mypar(c(1,1))
par(mar=c(1.75,2.0,1,1)+0.0)
plot(seq(1, npackages), revpackages$Count, 
  type="h",
  main="", ylab="", xlab="", 
  axes=FALSE, log="xy",
  xlim=c(0.8, npackages+1),
  ylim=c(1, packagemax))
axis(2, mgp=c(1.25, 0.25, 0), lwd=(1/shrink), at=c(1,2,5,10,20,50,100,200,500,1000,packagemax)) 
axis(1, mgp=c(1.5, 0.5, 0), lwd=(1/shrink), at=c(1,2,5,10,20,50,100,200,500,1000,npackages))
title(ylab="Crashes Seen", line=1.0)
title(xlab="Package", line=1.25)

dev.off()

buckets = read.csv("buckets_dist.csv")
revbuckets <- buckets[rev(rownames(buckets)),]
nbuckets = length(buckets$Count)
bucketmax = max(buckets$Count)

svg(filename="buckets.svg", width=col_width, height=height, 
    family="Latin Modern Roman", pointsize=10)
mypar(c(1,1))
par(mar=c(1.75,2.0,1,1)+0.0)
plot(seq(1, nbuckets), revbuckets$Count, 
  type="h",
  main="", ylab="", xlab="", 
  axes=FALSE, log="xy",
  xlim=c(0.8, nbuckets+1),
  ylim=c(1, bucketmax))
axis(2, mgp=c(1.25, 0.25, 0), lwd=(1/shrink), at=c(1,2,5,10,20,50,bucketmax)) 
axis(1, mgp=c(1.5, 0.5, 0), lwd=(1/shrink), at=c(1,2,5,10,20,50,100,200,500,1000,nbuckets))
title(ylab="Crashes", line=1.0)
title(xlab="Bucket", line=1.25)

dev.off()

date_ranges = read.csv("date_ranges.csv")
revdate_ranges <- date_ranges[rev(rownames(date_ranges)),]
ndate_ranges = length(date_ranges$Count)
date_rangemax = max(date_ranges$Delta)
x=revdate_ranges[revdate_ranges$Count>2,][[3]]/(24*60*60)
# d = dbeta(seq(0, 1, length= length(x)+1), 0.01907475, 2.35506635)
# d2 = dbeta(seq(0, 1, length= length(x)+1), 0.01907475, 2.14096941)
d = dbeta(seq(0, 1, length= length(x)+1), 0.292113, 2.857459)
d2 = dbeta(seq(0, 1, length= length(x)+1), 0.3342342, 3.0989057)
d = d[-1]
d2 = d2[-1]
middle_index = 100
d = d * (x[middle_index]/d[middle_index])
d2 = d2 * (x[middle_index]/d2[middle_index])

linecolor=rgb(1,0,0)
svg(filename="date_ranges.svg", width=col_width, height=height, 
    family="Latin Modern Roman", pointsize=10)
mypar(c(1,1))
par(mar=c(1.75,2.0,1,1)+0.0)
plot(seq(1, length(x)), x, 
  type="h",
  main="", ylab="", xlab="", 
  axes=FALSE, log="y",
  xlim=c(0.8, length(x)+1),
  ylim=c(1/24, 365.25*4),
  col=rgb(0.5, 0.5, 0.5))
lines(seq(1,  length(x)), d, col=linecolor, cex=linesx)
# lines(seq(1,  length(x)), d2, col=rgb(1,0,1))
legend("topright", legend=c("Beta Distribution"), col=c(linecolor),
        lty=c(1),
        cex=mex*0.9, pt.cex=linesx, bty="n")
axis(2, mgp=c(1.25, 0.25, 0), lwd=(1/shrink), 
  at=c(1/24,1,7,30,365.25,365.25*4),
  labels=c("Hour", "Day", "Week", "Month", "Year", "4Y")
  )
axis(1, mgp=c(1.5, 0.5, 0), lwd=(1/shrink))
title(ylab="Lifetime", line=1.0)
title(xlab="Bucket #", line=1.25)

dev.off()


library(fitdistrplus)
library(logspline)
# 
# descdist(revdate_ranges$Delta, discrete=FALSE, boot=100)
# 
# hist(revdate_ranges$Delta, freq=FALSE)
# lines(density(revdate_ranges$Delta))
# 
est = fitdist(x/max(x), "beta", method="mme")
est
fitdist(x/max(x), probs=list(shape1=0.5, shape2=0.5), "beta", method="qme", start=est[[1]])
# fitdist(x/max(x), "beta", method="mle", start=est[[1]])
# 


y=revdate_ranges[revdate_ranges$Count>2,][[3]]/(24*60*60)
x=revdate_ranges[revdate_ranges$Count>2,][[2]]

linecolor=rgb(1,0,0)
svg(filename="date_v_size.svg", width=col_width, height=height, 
    family="Latin Modern Roman", pointsize=10)
mypar(c(1,1))
par(mar=c(1.75,2.0,1,1)+0.0)
plot(x, y, 
  type="p",
  main="", ylab="", xlab="", 
  axes=FALSE, log="xy",
#   xlim=c(0.8, length(x)+1),
  ylim=c(1/24, 365.25*4),
  col=rgb(0, 0, 0, 0.5))
# lines(seq(1,  length(x)), d2, col=rgb(1,0,1))
axis(2, mgp=c(1.25, 0.25, 0), lwd=(1/shrink), 
  at=c(1/24,1,7,30,365.25,365.25*4),
  labels=c("Hour", "Day", "Week", "Month", "Year", "4Y")
  )
axis(1, mgp=c(1.5, 0.5, 0), lwd=(1/shrink))
title(ylab="Lifetime", line=1.0)
title(xlab="Bucket Size", line=1.25)

dev.off()

cor.test(x,y, method="pearson")
cor.test(x,y, method="spearman")

signals = read.csv("signals-filtered.csv")

svg(filename="signals.svg", width=col_width, height=height, 
    family="Latin Modern Roman", pointsize=10)
mypar(c(1,1))
par(mar=c(1.75,2.0,1,1)+0.0)
xx <- barplot(signals$Count,
# legend=signals$Signal, 
#   type="p",
  main="", ylab="", xlab="", 
  axes=FALSE, log="",
#   xlim=c(0.8, length(x)+1),
#   ylim=c(1/24, 365.25*4),
#   col=rgb(0, 0, 0, 0.5)
)
# lines(seq(1,  length(x)), d2, col=rgb(1,0,1))
text(x=xx, y=signals$Count, label=signals$Count, pos=3, cex=mex*0.7)
axis(2, mgp=c(1.25, 0.25, 0), lwd=(1/shrink))
axis(1, mgp=c(1.5, 0.5, -0.2), lwd=(1/shrink),
    at=seq(1,length(signals$Count))*1.2-0.6,
   labels=c("SYS", "XFSZ", "XCPU", "ILL", "FPE", "BUS", "TRAP", "ABRT", "SEGV"),
   cex.axis=mex*0.7,
   lty=0
)
title(ylab="Crashes", line=1.0)
title(xlab="Signal", line=1.25)

40592-sum(signals$Count)

dev.off()

architectures = read.csv("architectures-filtered.csv")

svg(filename="architectures.svg", width=col_width, height=height, 
    family="Latin Modern Roman", pointsize=10)
mypar(c(1,1))
par(mar=c(1.75,2.0,1,1)+0.0)
xx <- barplot(architectures$Count,
# legend=architectures$Signal, 
#   type="p",
  main="", ylab="", xlab="", 
  axes=FALSE, log="",
#   xlim=c(0.8, length(x)+1),
#   ylim=c(1/24, 365.25*4),
#   col=rgb(0, 0, 0, 0.5)
)
# lines(seq(1,  length(x)), d2, col=rgb(1,0,1))
text(x=xx, y=architectures$Count, label=architectures$Count, pos=3, cex=mex*0.7)
axis(2, mgp=c(1.25, 0.25, 0), lwd=(1/shrink))
axis(1, mgp=c(1.5, 0.5, -0.2), lwd=(1/shrink),
    at=seq(1,length(architectures$Count))*1.2-0.6,
   labels=architectures$Architecture,
   cex.axis=mex*0.7,
   lty=0
)
title(ylab="Crashes", line=1.0)
title(xlab="Architecture", line=1.25)

40592-sum(architectures$Count)

dev.off()