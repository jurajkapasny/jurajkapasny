# Scrape articles from web
# websites available:
#	www.sme.sk
#	www.dennikn.sk

# !/bin/bash
# COUNTER=0
# while  [ $COUNTER -lt 10 ] ; 
# do
#	echo The counter is $COUNTER
#        let COUNTER=COUNTER+1 
# done

# DennikN
echo "Scraping DennikN"
python scraping_Dennikn.py

# SME
echo "Scraping SME"
python scraping_SME.py

#Pravda
echo "Scraping Pravda"
python scraping_Pravda.py
