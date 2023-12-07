#PBS -N main
#PBS -q paralela
#PBS -l nodes=2:ppn=128
#PBS -e outputs/erros_paralela
#PBS -o outputs/saidas_paralela
#PBS -m abe
#PBS -M s209376@dac.unicamp.br

module load python/3.8.11-intel-2021.3.0
module load openmpi/4.1.1-intel-2021.3.0
source py38/bin/activate

cd $PBS_O_WORKDIR
mpirun python -m mpi4py.futures main.py