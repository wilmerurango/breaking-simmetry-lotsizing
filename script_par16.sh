#PBS -N main
#PBS -q par16
#PBS -l nodes=1:ppn=16
#PBS -e outputs/erros_par16
#PBS -o outputs/saidas_par16
#PBS -m abe
#PBS -M s209376@dac.unicamp.br

module load anaconda3
module load mpich/4.1.1-gcc-9.4.0
source newmpi/bin/activate

cd $PBS_O_WORKDIR
mpirun python -m mpi4py.futures main.py
