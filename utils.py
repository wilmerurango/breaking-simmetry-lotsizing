from typing import Dict, List
import numpy as np
import pandas as pd

import re

from pathlib import Path
from read_file import dataCS
from context import ProjectContext
from docplex.mp.relax_linear import LinearRelaxer

try:
    from mpi4py.futures import MPIPoolExecutor
    from mpi4py import MPI

    MPI_BOOL = True
except:
    print("mpi4py not running")
    MPI_BOOL = False

import constants

import gc


def print_info(context: ProjectContext, data: dataCS, status: str) -> None:
    if MPI_BOOL:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()          
        size = comm.Get_size()
        name = MPI.Get_processor_name()
        message = f"Process {rank} / {size} on {name}"        
    else:
        message = str(None)
    print(
        f"Instance = {data.instance} Cap = {data.cap[0]} nmaquinas = {data.r} {status} Experimento {context.experiment_id} " + message
    )


def add_new_kpi(kpis: Dict[str, any], result, data: dataCS, **kwargs) -> dict:
    kpis["Instance"] = data.instance
    kpis["Best Bound"] = result.solve_details.best_bound
    kpis["Gap"] = result.solve_details.gap
    kpis["Nodes Processed"] = result.solve_details.nb_nodes_processed
    kpis["Tempo de Solução"] = result.solve_details.time
    kpis["capacity"] = data.cap[0]
    kpis["utilization_capacity"] = (
        100 * kpis.get("used_capacity", 0) / (data.cap[0] * data.r * data.nperiodos)
    )
    kpis["nmaquinas"] = data.r
    # kpis["real obj function"] = data.valor_funcao_obj
    for key, value in kwargs.items():
        kpis[key] = value
    return kpis

def cs_aux(data: dataCS):
    cs_aux = np.zeros((data.nitems, data.r, data.nperiodos, data.nperiodos))
    for j in range(data.r):
        for i in range(data.nitems):
            for t in range(data.nperiodos):
                for k in range(data.nperiodos):
                    cs_aux[i, j, t, k] = (
                        data.vc[i, t] + 0.00001*j + sum(data.hc[i] for u in range(t, k))
                    ) * data.d[i, k]
    return cs_aux

def closest_to_IDEAL_CAPACITY_percent(
    results_per_instance: List[Dict[str, any]]
) -> Dict[str, any]:
    """Dado uma lista de resultados para uma instância, retorne aquele mais próximo de IDEAL_CAPACITY de utilização da capacidade."""
    return min(
        results_per_instance,
        key=lambda x: abs(x["utilization_capacity"] - constants.IDEAL_CAPACITY),
    )


def choose_capacity(
    context: ProjectContext,
    dataset: str,
    build_model,
    nmaquinas: int = 2,
    get_closest: bool = True,
) -> None:    
    data = dataCS(context, dataset, r=nmaquinas)
    original_capacity = data.cap[0] / data.r
    instance_results = []

    for cap in np.linspace(
        original_capacity,
        original_capacity * 3,
        num=constants.NUM_POINTS,
        endpoint=True,
    ):
        mdl, data = build_model(data, np.ceil(cap))
        mdl.parameters.timelimit = constants.FAST_TIMELIMIT
        result = mdl.solve()

        if result == None:
            print_info(context, data, "infactível")
            continue

        kpis = mdl.kpis_as_dict(result, objective_key="objective_function")
        kpis = add_new_kpi(kpis, result, data)

        assert kpis["utilization_capacity"] <= 100, "Capacidade > 100%"

        instance_results.append(kpis)
        print_info(context, data, "concluído")
    if get_closest:
        if len(instance_results) > 0:
            df_ideal_capacity = pd.DataFrame(
                [closest_to_IDEAL_CAPACITY_percent(instance_results)]
            )
            data.cap[0] = df_ideal_capacity["capacity"]
            df_ideal_capacity.to_excel(
                f"{constants.RESULTADOS_INDIVIDUAIS_PATH}/{str(data)}.xlsx",
                engine="openpyxl",
            )
    else:
        df_ideal_capacity = pd.DataFrame(instance_results)
        df_ideal_capacity.to_excel(
            f"{constants.RESULTADOS_INDIVIDUAIS_PATH}/{str(data)}.xlsx",
            engine="openpyxl",
        )
    gc.collect()


def running_all_instance_choose_capacity(context: ProjectContext, build_model) -> None:
    # Executando e coletando os resultados
    final_results = []

    if not MPI_BOOL:        
        for dataset in constants.INSTANCES:
            for nmaq in constants.MAQUINAS:
                best_result = choose_capacity(context, dataset, build_model, nmaquinas=nmaq)

                if isinstance(best_result, pd.DataFrame):
                    final_results.append(best_result)
    else:
        with MPIPoolExecutor() as executor:            
            futures = executor.starmap(
                choose_capacity,
                (
                    (context, dataset, build_model, nmaq)
                    for dataset in constants.INSTANCES
                    for nmaq in constants.MAQUINAS
                ),
            )
            final_results.append(futures)
            executor.shutdown(wait=True)

    get_and_save_results(
        path_to_read=constants.RESULTADOS_INDIVIDUAIS_PATH,
        path_to_save=constants.CAPACIDADES_PATH,
    )
    print("Processamento de capacidades concluído.")


def get_values_from_name(file_name: str, regex: str, index: int) -> int:
    target = re.compile(regex).search(file_name)
    if target:
        return int(target[0][index])
    else:
        return -1        
    
def get_and_save_results(path_to_read: str, path_to_save: Path) -> None:
    list_files = []
    target_formulation = get_values_from_name(path_to_save.name, "otimizados_[0-9]", -1)
    target_experiment = get_values_from_name(path_to_save.name, "experiment_[0-9]", -1)
    for file in Path(path_to_read).glob("*"):        
        current_formulation_file = get_values_from_name(file.name, "[0-9]_ref", 0)                
        current_experiment = get_values_from_name(file.name, "experiment_[0-9]", -1)            
        if  target_formulation == current_formulation_file and target_experiment == current_experiment:
            list_files.append(pd.read_excel(file))
    df_results_optimized = pd.concat(list_files)
    df_results_optimized.to_excel(path_to_save, index=False)


def solve_optimized_model(
    context: ProjectContext, dataset: str, build_model, capacity: Dict, env_formulation: int, nmaquinas: int = 8
) -> None:
    if capacity == None:
        return None
    elif not isinstance(capacity, dict):
        print_info(context, data, "capacidade está com tipo errado")
        raise TypeError("Capacidade está com tipo errado.")
    data = dataCS(context, dataset, r=nmaquinas)
    mdl, data = build_model(data, context.multiplicador_capacidade * capacity.get("capacity", 0))
    mdl.parameters.timelimit = constants.TIMELIMIT
    mdl.set_time_limit(constants.TIMELIMIT)
    result = mdl.solve()

    if result == None:
        print_info(context, data, "infactível")
        return None

    kpis = mdl.kpis_as_dict(result, objective_key="objective_function")
    kpis = add_new_kpi(kpis, result, data, formulation=env_formulation, experimento=context.experiment_id)

    # Cálculo da relaxação linear
    relaxed_model = LinearRelaxer.make_relaxed_model(mdl.clone())
    status = relaxed_model.solve(url=None, key=None, log_output=False)

    relaxed_objective_value = relaxed_model.objective_value
    kpis["Relaxed Objective Value"] = relaxed_objective_value

    suffix_path = str(data) + "_" + env_formulation + f"_experiment_{context.experiment_id}"
    complete_path_to_save = Path.resolve(
        constants.OTIMIZADOS_INDIVIDUAIS_PATH / suffix_path
    )

    df_results_optimized = pd.DataFrame([kpis])
    df_results_optimized.to_excel(f"{complete_path_to_save}.xlsx", index=False)

    print_info(context, data, "concluído")
    gc.collect()


def running_all_instance_with_chosen_capacity(
    context: ProjectContext, build_model, path_to_save: str, env_formulation: int
):
    final_results = []

    pdf_capacidades = pd.read_excel(constants.CAPACIDADES_PATH, engine="openpyxl")
    caps = pd.pivot_table(
        pdf_capacidades, index=["Instance", "nmaquinas"], aggfunc={"capacity": "mean"}
    ).T.to_dict()

    # Atualizar a coluna "capacity" na tabela caps
    for key in caps:
        caps[key]['capacity'] = caps[key]['capacity'] * 0.95
    print(caps)

    if not MPI_BOOL:        
        for dataset in constants.INSTANCES:
            for nmaq in constants.MAQUINAS:
                if caps.get((dataset, nmaq), None) == None:
                    print(f"Instance = {dataset} nmaquinas = {nmaq} not found")
                    continue
                else:
                    cap = caps.get((dataset, nmaq), None)

                best_result = solve_optimized_model(
                    context,
                    dataset,
                    build_model,
                    capacity=cap,
                    nmaquinas=nmaq,
                    env_formulation=env_formulation,
                )

                if best_result:
                    final_results.append(best_result)
    else:
        with MPIPoolExecutor() as executor:            
            futures = executor.starmap(
                solve_optimized_model,
                (
                    (
                        context,
                        dataset,
                        build_model,
                        caps.get((dataset, nmaq), None),
                        env_formulation,
                        nmaq,
                    )
                    for dataset in constants.INSTANCES
                    for nmaq in constants.MAQUINAS
                ),
            )
            final_results.append(futures)
            executor.shutdown(wait=True)

    get_and_save_results(
        path_to_read=constants.OTIMIZADOS_INDIVIDUAIS_PATH,
        path_to_save=Path.resolve(constants.FINAL_PATH / path_to_save),
    )
    print(f"Concluído {env_formulation}")