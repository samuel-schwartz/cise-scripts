library(ggplot2)
library(RColorBrewer)
library(forcats)

# Top level
top_level <- data.frame("Domain" = c("Non-US", "US, Non-Lab", "US Lab"), "Commits" = c(291511, 279520, 423064), "Percent of Commits"=c(29.3, 28.1, 42.6))

my_colors <- c(brewer.pal(name="Dark2", n = 3))

p <- ggplot(top_level, aes(x="", y=Percent.of.Commits, fill=Domain))
p <- p + theme_void()
p <- p + geom_bar(stat="identity", width=1)
p <- p + coord_polar("y", start=0) 
p <- p + geom_text(aes(label = paste0(Commits,"\n(", Percent.of.Commits, "%)")), position = position_stack(vjust=0.5))
p <- p + ylab("Percent of Commits") + xlab("")
p <- p + scale_fill_manual(values=my_colors)
p

# Non-US
non_us <- read.table(text="Domain	Number of Commits	 Percent of all Commits	 Percent of Category
gov.uk	223128	22.4	76.5
gov.au	31033	3.1	10.6
gov.br	24196	2.4	8.3
gov.pl	4039	0.4	1.4
gov.ar	2290	0.2	0.8
govt.nz	2105	0.2	0.7
All others	4720	0.5	0.2", header=T, sep="\t")

p <- ggplot(non_us, aes(x=fct_reorder(Domain, Number.of.Commits), y=Number.of.Commits))
p <- p + theme_bw()
p <- p + geom_col(fill=my_colors[1])
p <- p + xlab("Domain")
p

# US Non Lab

non_lab <- read.table(text="Domain	Number of Commits	 Percent of all Commits	 Percent of Category
nasa.gov	61187	6.2	21.9
nih.gov	57859	5.8	20.7
usgs.gov	28786	2.9	10.3
cfpb.gov	27579	2.8	9.9
noaa.gov	16782	1.7	6
All others	87327	8.8	31.2", header=T, sep="\t")

p <- ggplot(non_lab, aes(x=fct_reorder(Domain, Number.of.Commits), y=Number.of.Commits))
p <- p + theme_bw()
p <- p + geom_col(fill=my_colors[3])
p <- p + xlab("Domain")
p


# US Lab

non_lab <- read.table(text="Domain	Number of Commits	 Percent of all Commits	 Percent of Category
ornl.gov	80166	8.1	18.9
lbl.gov	64521	6.5	15.3
llnl.gov	59338	6	14
inl.gov	41001	4.1	9.7
anl.gov	38608	3.9	9.1
bnl.gov	33224	3.3	7.9
lanl.gov	29243	2.9	6.9
fnal.gov	23080	2.3	5.5
sandia.gov	18023	1.8	4.3
nrel.gov	17521	1.8	4.1
pnnl.gov	15860	1.6	3.7
pnl.gov	1440	0.1	0.3
pppl.gov	826	0.1	0.2
ameslab.gov	169	0	0
doe.gov	44	0	0", header=T, sep="\t")

p <- ggplot(non_lab, aes(x=fct_reorder(Domain, Number.of.Commits), y=Number.of.Commits))
p <- p + theme_bw()
p <- p + geom_col(fill=my_colors[2])
p <- p + xlab("Domain")
p <- p + theme(axis.text.x = element_text(angle = 90*3, vjust = 0, hjust=0.5))
p


# Web Scraping

scrape <- read.table(text="Domain	Repos
ameslab.gov	10
anl.gov	482
bnl.gov	82
energy.gov	60
fnal.gov	9
inl.gov	34
jlab.org	35
lanl.gov	84
lbl.gov	184
llnl.gov	400
netl.doe.gov	11
nrel.gov	4
ornl.gov	212
pnnl.gov	52
pppl.gov	2
sandia.gov	29
slac.stanford.edu	8
srnl.doe.gov	0", header=T, sep="\t")

p <- ggplot(scrape, aes(x=fct_reorder(Domain, Repos), y=Repos))
p <- p + theme_bw()
p <- p + geom_col(fill="#9c254d")
p <- p + xlab("Domain") + ylab("Repos Found")
p <- p + theme(axis.text.x = element_text(angle = 90*3, vjust = 0, hjust=0.5))
p
