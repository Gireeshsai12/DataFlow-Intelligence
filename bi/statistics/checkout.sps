* Set the working directory to this project's root before running.
GET DATA /TYPE=TXT /FILE='bi-sample/ExperimentArms.csv'
 /DELCASE=LINE /DELIMITERS="," /ARRANGEMENT=DELIMITED /FIRSTCASE=2
 /VARIABLES=variant A12 n F10.0 successes F10.0.
COMPUTE failures=n-successes.
VARSTOCASES /MAKE frequency FROM successes failures /INDEX=outcome /KEEP=variant.
WEIGHT BY frequency.
CROSSTABS /TABLES=variant BY outcome /STATISTICS=CHISQ /CELLS=COUNT ROW.
WEIGHT OFF.
