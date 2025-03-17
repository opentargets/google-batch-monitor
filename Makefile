# Usefull commands to prepare the test data and scripts for profiling runs.
send-carma-finemapping-script:
	gcloud storage cp profiling/carma/carma_finemapping.sh  gs://ot_orchestration/test/ukb_ppp_eur_data/carma_finemapping.sh