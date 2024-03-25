from typing import Dict, List

from docplex.mp.model import Model

from read_file import dataCS
from utils import cs_aux


def create_variables(mdl: Model, data: dataCS) -> Model:
    mdl.z = mdl.binary_var_dict(
        (
            (i, j, t)
            for i in range(data.nitems)
            for j in range(data.r)
            for t in range(data.nperiodos)
        ),
        lb=0,
        ub=1,
        name=f"z",
    )
    mdl.w = mdl.binary_var_dict(
        (
            (i, j, t)
            for i in range(data.nitems)
            for j in range(data.r)
            for t in range(data.nperiodos)
        ),
        lb=0,
        ub=1,
        name=f"w",
    )
    mdl.f = mdl.continuous_var_dict(
        (
            (i, j, t)
            for i in range(data.nitems)
            for j in range(data.r)
            for t in range(data.nperiodos)
        ),
        lb=0,
        name=f"f",
    )
    mdl.l = mdl.continuous_var_dict(
        (
            (i, j, t)
            for i in range(data.nitems)
            for j in range(data.r)
            for t in range(data.nperiodos)
        ),
        lb=0,
        name=f"l",
    )
    mdl.z = mdl.continuous_var(lb=0, name=f"u")
    
    mdl.x = mdl.continuous_var_dict(
        (
            (i, j, t, k)
            for i in range(data.nitems)
            for j in range(data.r)
            for t in range(data.nperiodos)
            for k in range(data.nperiodos)
        ),
        lb=0,
        ub=1,
        name=f"x",
    )
    return mdl

def define_obj_function(mdl: Model, data: dataCS) -> Model:
    # cs_aux = cs_aux(data)
    mtd_func = mdl.sum(
        data.sc[i] * (mdl.z[i, j, t]+ mdl.w[i, j, t])
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
    ) + sum(
        cs_aux(data)[i, j, t, k] * mdl.x[i, j, t, k]
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
        for k in range(t, data.nperiodos)
    )
    mdl.mtd_func = mtd_func
    mdl.minimize(mtd_func)
    return mdl


def constraint_demanda_satisfeita(mdl: Model, data: dataCS) -> Model:
    for i in range(data.nitems):
        for t in range(data.nperiodos):
            if data.d[i, t] > 0:
                mdl.add_constraint(
                    mdl.sum(
                        mdl.x[i, j, k, t] for j in range(data.r) for k in range(t + 1)
                    )
                    == 1
                )
    return mdl


def constraint_capacity(mdl: Model, data: dataCS) -> Model:
    for t in range(data.nperiodos):
        for j in range(data.r):
            mdl.add_constraint(
                mdl.sum(data.st[i] * mdl.z[i, j, t] for i in range(data.nitems))
                + mdl.sum(
                    data.vt[i] * data.d[i, k] * mdl.x[i, j, t, k]
                    for i in range(data.nitems)
                    for k in range(t, data.nperiodos)
                )
                + mdl.sum(mdl.l[i,j,t] for i in range(data.nitems))
                +mdl.sum(mdl.f[i,j,t] for i in range(data.nitems))
                <= data.cap[0],
                ctname="capacity",
            )
    return mdl


def constraint_setup(mdl: Model, data: dataCS) -> Model:
    mdl.add_constraints(
        mdl.x[i, j, t, k] <= mdl.z[i, j, t] + mdl.w[i, j, t]
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
        for k in range(t, data.nperiodos)
    )
    return mdl

def constraint_split_time(mdl: Model, data: dataCS) -> Model:
    mdl.add_constraints(
        mdl.f[i, j, t] + mdl.l[i,j,t-1] == mdl.w[i, j, t] * data.st[i]
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
    )
    return mdl

def constraint_split_max(mdl: Model, data: dataCS) -> Model:
    mdl.add_constraints(
        mdl.sum(mdl.w[i, j, t] for i in range(data.nitems)) <= 1
        for j in range(data.r)
        for t in range(data.nperiodos)
    )
    return mdl
    

def valor_funcao_obj(mdl: Model, data: dataCS) -> Model:
    return sum(
            data.sc[i] * mdl.y[i, j, t]
            for i in range(data.nitems)
            for j in range(data.r)
            for t in range(data.nperiodos)
        ) + sum(
            data.cs[i, t, k] * mdl.x[i, j, t, k]
            for i in range(data.nitems)
            for j in range(data.r)
            for t in range(data.nperiodos)
            for k in range(t, data.nperiodos)
    )

def total_setup_cost(mdl, data):
    return sum(
        data.sc[i] * mdl.y[i, j, t]
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
    )


def total_estoque_cost(mdl, data):
    return sum(
        data.cs[i, t, k] * mdl.x[i, j, t, k]
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
        for k in range(data.nperiodos)
    )


def used_capacity(mdl, data):
    return sum(
        data.st[i] * mdl.y[i, j, t]
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
    ) + sum(
        data.vt[i] * data.d[i, k] * mdl.x[i, j, t, k]
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
        for k in range(t, data.nperiodos)
    )


def total_y(mdl, data):
    return sum(
        mdl.y[i, j, t]
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
    )


def closest_to_75_percent(results_per_instance: List[Dict[str, any]]) -> Dict[str, any]:
    """Dado uma lista de resultados para uma instância, retorne aquele mais próximo de 75% de utilização da capacidade."""
    return min(results_per_instance, key=lambda x: abs(x["utilization_capacity"] - 75))


def build_model(data: dataCS, capacity: float) -> Model:
    data.cap[0] = capacity
    mdl = Model(name="mtd")
    mdl.context.cplex_parameters.threads = 1
    mdl = create_variables(mdl, data)
    mdl = define_obj_function(mdl, data)
    mdl = constraint_demanda_satisfeita(mdl, data)
    mdl = constraint_capacity(mdl, data)
    mdl = constraint_setup(mdl, data)

    mdl.add_kpi(total_setup_cost(mdl, data), "total_setup_cost")
    mdl.add_kpi(total_estoque_cost(mdl, data), "total_estoque_cost")
    mdl.add_kpi(used_capacity(mdl, data), "used_capacity")
    mdl.add_kpi(total_y(mdl, data), "total_y")
    mdl.add_kpi(valor_funcao_obj(mdl, data), "valor_funcao_obj")
    return mdl, data
