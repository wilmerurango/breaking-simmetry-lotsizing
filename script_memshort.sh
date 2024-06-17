#PBS -N main
#PBS -q memshort
#PBS -l nodes=1:ppn=128
#PBS -e outputs/erros_memshort
#PBS -o outputs/saidas_memshort
#PBS -m abe
#PBS -M s209376@dac.unicamp.br

module load anaconda3
module load mpich/4.1.1-gcc-9.4.0
source newmpi/bin/activate

cd $PBS_O_WORKDIR
mpirun python -m mpi4py.futures main.py
