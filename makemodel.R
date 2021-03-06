library(MASS)
library(plsdepot)

INPUT_FILE_PREFIX <- './data/processed/user_data'
X <- read.csv(paste(INPUT_FILE_PREFIX,'1.csv',sep='_'))
for(i in 2:5)
{
	X <- rbind(X,read.csv(paste(paste(INPUT_FILE_PREFIX,i,sep='_'),'csv',sep='.')))
}
X$USER_AGE <- as.numeric(Sys.time() - as.POSIXct(X$CREATED_AT,'%a %b %d %H:%M:%S +0000 %Y',tz='GMT')) 

for(i in c('HAS_LOCATION','HAS_URL','HAS_BEEN_VERIFIED'))
{
	X[,i] <- ifelse(X[,i]=='True',1,0)
}

X <- X[,c(-1,-2)]


X <- X[X$USER_AGE > 30 & X$FRIENDS_COUNT > 15 & X$STATUSES_COUNT > 10 & X$STATUSES_COUNT < 100000 & X$FOLLOWERS_COUNT < 100000 & X$FOLLOWERS_COUNT > 100,]

X$HAS_BEEN_VERIFIED <- NULL

cols <- dim(X)[2]

X <- X[,c(1:4,6:cols,5)]

write.table(X,file='./model/metrics/data/data.csv',sep=',',row.names=FALSE)
sink('./model/metrics/data/data_summary.txt')
summary(X)
sink('./model/metrics/correlation/table.txt')
cor(X)
sink()


pdf(file='./model/metrics/correlation/FOLLOWERS_COUNT_vs_everything_else.pdf')
	for(i in 1:cols)
	{
	  		plot(X[,i],X$FOLLOWERS_COUNT,xlab=colnames(X)[i],ylab='FOLLOWERS_COUNT',log='xy')
	    	abline(rlm(X$FOLLOWERS_COUNT ~ X[,i]),col='blue',untf=TRUE)
	}
dev.off()

X <- log(X + 1)

model <- plsreg1(X[, 1:(cols-1)], X[, cols, drop = FALSE], comps = 4)

sink('./model/result/tables/std_coefs.txt')
	model$std.coefs
sink('./model/result/tables/reg_coefs.txt')
	model$reg.coefs
sink()

X$PREDICTED <- model$y.pred
X <- exp(X) - 1

pdf(file='./model/result/plots/ACTUAL_vs_PREDICTED.pdf')
	plot(X$FOLLOWERS_COUNT, X$PREDICTED,log='xy',xlab='FOLLOWERS_COUNT',ylab='PREDICTED_FOLLOWERS_COUNT')
	abline(rlm(X$FOLLOWERS_COUNT ~ X$PREDICTED),col='blue',untf=TRUE)
dev.off()


diff_from_pred <- abs(X$FOLLOWERS_COUNT - X$PREDICTED)

perc_diff_from_pred <- (diff_from_pred/X$FOLLOWERS_COUNT)*100

X$ABS_DIFF_PRED <- diff_from_pred

X$PERC_DIFF_PRED <- perc_diff_from_pred

pdf(file='./model/result/plots/error_graphs.pdf')
	plot(X$FOLLOWERS_COUNT,X$ABS_DIFF_PRED,log='xy',xlab='FOLLOWERS_COUNT',ylab='ABSOLUTE_DIFFERENCE_IN_PREDICTION')
	abline(rlm(X$FOLLOWERS_COUNT ~ X$ABS_DIFF_PRED),col='blue',untf=TRUE)
	plot(X$FOLLOWERS_COUNT,X$PERC_DIFF_PRED,log='xy',xlab='FOLLOWERS_COUNT',ylab='PERCENTAGE_DIFFERENCE_IN_PREDICTION')
	abline(rlm(X$FOLLOWERS_COUNT ~ X$PERC_DIFF_PRED),col='blue',untf=TRUE)
dev.off()

write.table(X[,c('FOLLOWERS_COUNT','PREDICTED','ABS_DIFF_PRED','PERC_DIFF_PRED')],file='./model/result/tables/errors.csv',sep=',',row.names=FALSE)

sink()

avg_pred_perc_difference <- mean(perc_diff_from_pred)

cat('\nAvg perc difference for Predicted=', toString(avg_pred_perc_difference),file='./model/result/tables/eval.txt')


