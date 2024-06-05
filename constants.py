from pathlib import Path


INSTANCES = [f"X{i}{j}{k}{l}{m}{n}.dat" for i in range(1, 4) for j in range(1,3) for k in [1,2,4] 
             for l in range(1,3) for m in range(7,10) for n in ["A", "B", "C", "D", "E"]]

MAQUINAS = [2,4,6]
NUM_POINTS = 15
FAST_TIMELIMIT = 20
TIMELIMIT = 3600

CAPACIDADES_PATH = Path.resolve(Path.cwd() / "resultados" / "capacidades.xlsx")
RESULTADOS_INDIVIDUAIS_PATH = Path.resolve(Path.cwd() / "resultados" / "individuais")
OTIMIZADOS_INDIVIDUAIS_PATH = Path.resolve(Path.cwd() / "resultados" / "otimizados")
DETALHADOS_INDIVIDUAIS_PATH = Path.resolve(Path.cwd() / "resultados" / "detalhados")
FINAL_PATH = Path.resolve(Path.cwd() / "resultados")

IDEAL_CAPACITY = 75
