#PBS -N meuteste
#PBS -q testes
#PBS -l nodes=1:ppn=2
#PBS -e erros
#PBS -o saida

module load anaconda3
module load mpich/4.1.1-gcc-9.4.0
source newmpi/bin/activate

cd $PBS_O_WORKDIR

mpirun -np 2 python teste.py