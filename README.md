# GCMC-Gelman-Rubin-Wrapper
A *python* wrapper that runs GCMC simulation using RASPA, and calculates the Gelman-Rubin convergence factor after the simulation is done and restarts the simulation if needed.<br />
**bsub.job**: shell script for running RASPA<br />
**simulation.input**: RASPA input file<br />
**wrapper.job**: python wrapper<br />
**GCMC-GR.py**: main python script<br />
When running this as a job, submit the **wrapper.job** file.
