#PBS -N main
#PBS -q parexp
#PBS -l nodes=3:ppn=48
#PBS -e outputs/erros_parexp
#PBS -o outputs/saidas_parexp
#PBS -m abe
#PBS -M s209376@dac.unicamp.br

module load anaconda3
module load mpich/4.1.1-gcc-9.4.0
source newmpi/bin/activate

cd $PBS_O_WORKDIR
mpirun python -m mpi4py.futures main.py