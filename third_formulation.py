from typing import Dict
from docplex.mp.model import Model

from read_file import dataCS

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
    mdl.x = mdl.continuous_var_dict(
        (
            (i, j, t, k)
            for i in range(data.nitems)
            for j in range(data.r)
            for t in range(data.nperiodos)
            for k in range(data.nperiodos)
        ),
        lb=0,
        name=f"x",
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
    return mdl


def define_obj_function(mdl: Model, data: dataCS) -> Model:
    mtd_func = mdl.sum(
        data.sc[i] * (mdl.z[i, j, t]+ mdl.w[i, j, t])
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

def constraint_simmetry_crossover(mdl: Model, data: dataCS) -> Model:
    mdl.add_constraints(
        mdl.sum(mdl.w[k, j, t] for k in range(i-1)) <= mdl.z[i,t,j]
        for i in range(1,data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
    )
    return mdl

def constraint_simmetry_machine(mdl: Model, data: dataCS) -> Model:
    mdl.add_constraints(
        mdl.w[i, j-1, t] + mdl.z[i,j-1,t] <= mdl.w[i, j, t] + mdl.z[i,j,t]
        for i in range(data.nitems)
        for j in range(1,data.r)
        for t in range(data.nperiodos)
    )
    return mdl


def total_setup_cost(mdl, data):
    return sum(
        data.sc[i] * (mdl.z[i, j, t]+mdl.w[i, j, t])
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
        data.st[i] * (mdl.z[i, j, t]+mdl.w[i, j, t])
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
        mdl.z[i, j, t]+mdl.w[i, j, t]
        for i in range(data.nitems)
        for j in range(data.r)
        for t in range(data.nperiodos)
    )


def add_new_kpi(kpis: Dict[str, any], result, data: dataCS) -> dict:
    kpis["Instance"] = data.instance
    kpis["Best Bound"] = result.solve_details.best_bound
    kpis["Gap"] = result.solve_details.gap
    kpis["Nodes Processed"] = result.solve_details.gap
    kpis["Tempo de Solução"] = result.solve_details.time
    kpis["capacity"] = data.cap[0]
    kpis["utilization_capacity"] = (
        100 * kpis.get("used_capacity", 0) / (data.cap[0] * data.r * data.nperiodos)
    )
    kpis["nmaquinas"] = data.r
    return kpis


def build_model(data: dataCS, capacity: float) -> Model:    
    data.cap[0] = capacity
    mdl = Model(name="mtd")
    mdl = create_variables(mdl, data)
    mdl = define_obj_function(mdl, data)
    mdl = constraint_demanda_satisfeita(mdl, data)
    mdl = constraint_capacity(mdl, data)
    mdl = constraint_setup(mdl, data)
    mdl = constraint_split_time(mdl, data)
    mdl = constraint_split_max(mdl, data)
    mdl = constraint_simmetry_crossover(mdl, data)
    mdl = constraint_simmetry_machine(mdl, data)
    mdl.add_kpi(total_setup_cost(mdl, data), "total_setup_cost")
    mdl.add_kpi(total_estoque_cost(mdl, data), "total_estoque_cost")
    mdl.add_kpi(used_capacity(mdl, data), "used_capacity")
    mdl.add_kpi(total_y(mdl, data), "total_y")
    return mdl, data