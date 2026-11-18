/* Change the filename to the absolute path to bi-sample/ExperimentArms.csv. */
filename arms "bi-sample/ExperimentArms.csv";
data checkout;
    infile arms dsd firstobs=2 truncover;
    length variant $12 outcome $10;
    input variant :$12. n successes;
    outcome='Converted'; weight=successes; output;
    outcome='Other'; weight=n-successes; output;
run;
proc freq data=checkout;
    tables variant*outcome / chisq riskdiff;
    weight weight;
run;
