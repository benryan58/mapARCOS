
# 
# Take the ARCOS data PDFs and scrape out the data, saving into a combined
# CSV file.
# 

setwd("c:/users/ben_ryan/documents/personal/opioids/ARCOS")


getPackages <- function (list.of.packages) {
  new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]

  if(length(new.packages)) install.packages(new.packages)
  lapply(list.of.packages,require,character.only=T)
}


# 
# Pull data from a single ARCOS PDF and parse it into a data.table
# 
pullData <- function(arctxt,reportDT,debug=FALSE) {
	rptPeriodStart = NA
	rptPeriodEnd = NA
	drugCode = character()
	drugName = character()
	state = character()

	for(i in 1:length(arctxt)) {
		if (debug) {
			print(arctxt[i])
			flush.console()
		}
		line <- unlist(strsplit(gsub(',','',trimws(arctxt[i])),'[[:space:]]+'))

		if (suppressWarnings(!is.na(as.numeric(line[1])))) {
			if (length(line) == 1) {
				next
			}
			line <- as.numeric(line)
			line <- c(list(rptPeriodStart,rptPeriodEnd,drugCode,drugName,state),
				as.list(line))
			names(line) <- names(reportDT)
			reportDT <- rbind(reportDT,line)
			next
		}

		if (length(grep("REPORTING PERIOD:", arctxt[i],ignore.case=TRUE)) > 0) {
			if (length(grep("REPORT 2", arctxt[i],ignore.case=TRUE)) > 0) break

			periods <- unlist(regmatches(arctxt[i],
				gregexpr('\\d{2}/\\d{2}/\\d{4} TO \\d{2}/\\d{2}/\\d{4}',
					arctxt[i])))
			if (length(periods) == 0) next
			periods <- as.Date(unlist(strsplit(periods, ' TO ')),format='%m/%d/%Y')

			rptPeriodStart <- periods[1]
			rptPeriodEnd <- periods[2]
			next
		}

		if (length(grep("DRUG CODE:", arctxt[i])) > 0) {
			line <- unlist(strsplit(gsub(',','',trimws(arctxt[i])),'[[:space:]]{2,}'))
			druginfo <- unlist(strsplit(line,'DRUG CODE:|DRUG NAME:|DRUGCODE:|DRUGNAME:'))
			druginfo <- druginfo[druginfo!='']
			drugCode <- trimws(druginfo[1])
			drugName <- trimws(druginfo[2])
			next
		}

		if (length(grep("STATE:", arctxt[i])) > 0) {
			state <- trimws(gsub('STATE:','',arctxt[i]))
			next
		}

		if (length(grep("ARCOS 2 - REPORT 2", gsub('[[:space:]]{2,}',' ',arctxt[i]),ignore.case=TRUE)) > 0) break
	}
	return (reportDT)
}


#
# Actually do the things here.
# 

getPackages(list('data.table','pdftools'))

reportDT <- data.table(
	rptStart=as.Date(character()),
	rptEnd=as.Date(character()),
	drugCode=character(),
	drugName=character(),
	State=character(),
	zipcode=integer(),
	Q1=numeric(),
	Q2=numeric(),
	Q3=numeric(),
	Q4=numeric(),
	Total=numeric())

emptyRpt = copy(reportDT)


fileList <- grep("pdf$",dir(),value=TRUE)

for (fp in fileList) {
	arc <- pdf_text(fp)
	arc <- unlist(strsplit(arc,'\n'),recursive=FALSE)
	reportDT <- rbind(reportDT,pullData(arc,emptyRpt))
	print(paste0(fp," done!"))
	flush.console()
}

reportDT[,Year:=year(rptStart)]
fwrite(reportDT,"ARCOS_2000_2016.csv",row.names=FALSE)

