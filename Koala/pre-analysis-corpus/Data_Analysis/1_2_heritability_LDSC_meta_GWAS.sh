#------------------------------------------------------------
# 2024-09-13 last modified
#
# LDSC
# * use the munge_sumstats to reformat GWAS summary statistics
#   and keep SNPs in the HapMap3 list
# • calculate h2 using the GWAS meta-analysis
#------------------------------------------------------------


#----- (1) heritability -----
# sample size:
# Neff=4/(1/3635+1/13703) + 4/(1/6397 + 1/9270)= 26631.77 

## Munge Data
$dir_LDSC/munge_sumstats.py \
--sumstats GWAS_meta_GEL_DDD_HRC_sex_ALT_MAF0.01_HM3_rsid.txt.gz \
--a1 A1 --a2 A2 \
--N 26631.77 --p P \
--out LDSC_meta_analysis_GWAS_GEL_DDD_HRC_sex_Neff \
--merge-alleles ${dir_LDscore}/w_hm3.snplist

## Calculate h2 on the liability scale
$dir_LDSC/ldsc.py \
--h2 LDSC_meta_analysis_GWAS_GEL_DDD_HRC_sex_Neff.sumstats.gz \
--ref-ld-chr ${dir_LDscore}/ \
--w-ld-chr ${dir_LDscore}/ \
--samp-prev 0.5 \
--pop-prev 0.01 \
--out LDSC_meta_analysis_GWAS_GEL_DDD_HRC_sex_h2_liability_Neff_P0.5



#----- (2) rgen -----
#LDSC_${externalGWAS}.sumstats.gz: the file that contains the processed data of the external GWAS 
$dir_LDSC/ldsc.py \
--rg ../LDSC_meta_analysis_Scottish/LDSC_meta_analysis_GWAS_GEL_DDD_HRC_sex_Neff.sumstats.gz,\
../clean_GWAS/LDSC_input/LDSC_${externalGWAS}.sumstats.gz \
--ref-ld-chr ${dir_LDscore}/ \
--w-ld-chr ${dir_LDscore}/ \
--out LDSC_rgen_meta_GWAS_GEL_DDD_HRC_${externalGWAS}


