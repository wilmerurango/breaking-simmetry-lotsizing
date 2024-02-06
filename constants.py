from pathlib import Path

#INSTANCES = [f"F{i}.DAT" for i in range(2, 24)] + [f"F{i}.DAT" for i in range(26, 70)] + [f"G{i}.DAT" for i in range(1, 58)] + [f"G{i}.DAT" for i in range(59, 75)]
INSTANCES = ["F1.DAT",
              "F25.DAT", 
              "G59.DAT", 
              "G64.DAT"
             ]
MAQUINAS = [2,4]
NUM_POINTS = 10
FAST_TIMELIMIT = 20
TIMELIMIT = 360

CAPACIDADES_PATH = Path.resolve(Path.cwd() / "resultados" / "capacidades.xlsx")
RESULTADOS_INDIVIDUAIS_PATH = Path.resolve(Path.cwd() / "resultados" / "individuais")
OTIMIZADOS_INDIVIDUAIS_PATH = Path.resolve(Path.cwd() / "resultados" / "otimizados")
DETALHADOS_INDIVIDUAIS_PATH = Path.resolve(Path.cwd() / "resultados" / "detalhados")
FINAL_PATH = Path.resolve(Path.cwd() / "resultados")

IDEAL_CAPACITY = 75
