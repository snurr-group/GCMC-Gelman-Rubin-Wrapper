###################################################
# Run RASPA and then calculates Gelman-Rubin value#
# Only works for single pressure calculation now  #
###################################################
import pathlib

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

# use a non-interactive backend
import matplotlib
matplotlib.use('Agg')

file_dir = os.getcwd()
Sim_dir = file_dir + '/'

directory2 = 'Output/System_0/'

loadings = []

printevery = 50

fsize = 10

def Get_GR(round):
  for filename in os.listdir(Sim_dir + directory2):
  #here a second for loop for the directory names of the pore sizes
    if filename.endswith(".data"):
      with open(os.path.join(Sim_dir + directory2, filename),'r') as r:
        for ind, line in enumerate(r,1):
          if 'absolute adsorption:' in line:
            molkg = line.split("[mol/uc],")
            # ['\tabsolute adsorption:   0.37500 (avg.   0.29736) ', '   0.3903180149 (avg.   0.3095051343) [mol/kg],  41.4381120499 (avg.  32.8586125877) [mg/g]\n']
            molkg = molkg[1].split()[0] # the first number in the second element
            #print(molkg)
            loadings.append(molkg)

  Cycles = np.linspace(0,printevery * (len(loadings)-1), len(loadings))
  #####################################
  # GENERATE LOADING vs. CYCLE PLOT  ##
  #####################################
  fig1 = plt.figure()
  ax1 = fig1.add_subplot(111)

  ax1.plot(Cycles, loadings, label = 'GCMC Loading vs. Cycles')
  ax1.legend(prop={'size': 6})
  ax1.set_xlabel('Cycles', fontsize = fsize, fontweight='bold')
  ax1.set_ylabel("Loading [mol/kg]", fontsize = fsize, fontweight='bold')
  fig1.savefig(Sim_dir + 'Loading-Cycle-' + str(round) + '.png', dpi=900, bbox_inches = 'tight')

  ######################################
  # CALCULATE GELMAN-RUBIN VALUE    ####
  ######################################
  Dataset = pd.DataFrame()
  Dataset['Cycle'] = [int(a) for a in Cycles]
  Dataset['Loading'] = [float(a) for a in loadings]
  nblock = 5
  L = int(len(loadings)/nblock)
  list_of_blocks = []
  list_averages = []
  list_block_var = []
  for a in range(0,nblock):
    #print(a)
    blocka = Dataset.loc[a*L: (a+1)*L]
    list_averages.append(np.mean(blocka['Loading']))
    list_block_var.append(np.var(blocka['Loading']))
  # then calculate the r score
  B = np.var(list_averages)*L
  W = np.mean(list_block_var)
  R = ((L-1)/L*W + 1/L*B)/W
  print("Round " + str(round) + ", R is: " + str(R))
  return R

def Restart_Simulation(round):
  os.rename('Output', str(round) + '-output')
  if(os.path.isdir('RestartInitial')):
    print("It exists")
    os.rename('RestartInitial', str(round) + '-restartinitial')
  os.rename('Restart', 'RestartInitial')
  # change the line for reading restart file in simulation.input
  with open('simulation.input', 'r') as file :
    filedata = file.read()
  filedata = filedata.replace('RestartFile no', 'RestartFile yes')
  with open('simulation.input', 'w') as file:
        file.write(filedata)
  # finally, run the simulation
  os.system('./bsub.job')

##############################################################################################
# Step 1: start the simulation, provided that all the setup are done in the current folder  ##
##############################################################################################
os.system('./bsub.job')
#################################################################################################
# Before Step 2, setup the parameters for Gelman-Rubin(GR)                                     ##
# Number of GR-rounds, GR threshold (usually 1.5, but this seems too strict, 3 may be better)  ##
#################################################################################################
GR_rounds = 5
GR_goal = 1.5
##################################################################
# Step 3, get GR and check the value                            ##
# If it is greater than the threshold, restart the simulation   ##
##################################################################
current_round = 0
currentGR = Get_GR(current_round)
while((currentGR > GR_goal) and (current_round <= GR_rounds)):
  print("Current Round: " + str(current_round))
  Restart_Simulation(current_round)
  current_round += 1
  currentGR = Get_GR(current_round)
