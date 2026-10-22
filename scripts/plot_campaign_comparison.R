# Optional base-R export, after node scripts/render_campaign_comparison.mjs.
args <- commandArgs(trailingOnly=TRUE)
folder <- if(length(args)) args[1] else "reports/campaign-history-2026-10-22"
d <- read.csv(file.path(folder,"scores.csv"), stringsAsFactors=FALSE)
variants <- unique(d$variant)
models <- c("recency_7","ridge_10","forest_3_5","xgb_2_50","dynamic_01","ensemble_equal")
colors <- c("#3067c5","#8b51ad","#b56a16","#177c70")
png(file.path(folder,"comparison.png"),width=2000,height=1400,res=150)
par(mfrow=c(2,2),mar=c(6,4.5,2.5,1),oma=c(2,0,5,0),las=1)
for(election in c("knesset_24_2021","knesset_25_2022")) {
  for(stage in c("shrunk_projected","integer")) {
    rows <- d[d$election==election & d$stage==stage & d$method %in% models,]
    values <- rows$absolute_seat_error
    yr <- range(c(values,if(grepl("2021",election))20 else 12))+c(-0.7,0.7)
    plot(NA,xlim=c(0.5,length(models)+0.5),ylim=yr,xaxt="n",xlab="",ylab="Total absolute seat error",
         main=paste(sub(".*_","",election),if(stage=="integer")"Rounded" else "Before rounding, 25% correction"),bty="l")
    abline(h=axTicks(2),col="#e1e6ec",lwd=0.6)
    text(seq_along(models),par("usr")[3]-diff(par("usr")[3:4])*0.06,models,srt=35,adj=1,xpd=NA,cex=0.85)
    for(i in seq_along(variants)) {
      r <- rows[rows$variant==variants[i],]
      vals <- r$absolute_seat_error[match(models,r$method)]
      points(seq_along(models)+(i-2.5)*0.12,vals,col=colors[i],pch=c(1,2,5,16)[i],cex=1.1)
    }
    reference <- d[d$election==election & d$stage==stage & d$method=="rounded_mean_reference",]$absolute_seat_error[1]
    abline(h=reference,col="#637186",lty=2)
  }
}
mtext("Same models and poll benchmarks, different historical inputs",outer=TRUE,side=3,line=3.5,cex=1.25,font=2)
mtext("Dashed line: matching-stage poll mean. Separate markers are data variants, not additional election outcomes.",outer=TRUE,side=1,line=0.5,cex=0.8)
par(fig=c(0,1,0,1),mar=c(0,0,0,0),oma=c(0,0,0,0),new=TRUE)
plot.new()
legend("top",inset=c(0,0.04),legend=c("Original history","Publication age only","Added repeated releases","Added releases + publication age"),col=colors,pch=c(1,2,5,16),ncol=2,bty="n",cex=0.85)
invisible(dev.off())
cat("Wrote comparison.png; no models fitted.\n")
