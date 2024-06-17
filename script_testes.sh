#PBS -N main
#PBS -q testes
#PBS -l nodes=1:ppn=4
#PBS -e outputs/erros_testes
#PBS -o outputs/saidas_testes
#PBS -m abe
#PBS -M s209376@dac.unicamp.br

module load anaconda3
module load mpich/4.1.1-gcc-9.4.0
source newmpi/bin/activate

cd $PBS_O_WORKDIR
mpirun -np 4 python -m mpi4py.futures main.py