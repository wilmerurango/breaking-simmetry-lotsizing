import re
from dataclasses import dataclass
from typing import Dict
import os
import numpy as np
import pandas as pd
from pathlib import Path
from context import ProjectContext


@dataclass
class LerDados:
    instance: str
    nitems: int
    nperiodos: int
    cap: int
    vt: np.ndarray
    hc: np.ndarray
    st: np.ndarray
    sc: np.ndarray
    d: np.ndarray

    def __init__(self, context: ProjectContext, instance: str, sort_index: bool = False):
        self.instance = instance
        self._instance = Path.resolve(Path.cwd() / "540data" / instance)
        if not Path.exists(self._instance):
            print(f"{self.instance} NÃO EXISTE")
        sep = self._detect_delimiter()
        column_names = self._generate_cols(sep=sep)
        df = pd.read_csv(
            self._instance,
            sep=sep,
            header=None,
            lineterminator="\n",
            engine="c",
            names=column_names,
        )
        self.nitems = int(df.iloc[0, 0])
        self.nperiodos = int(df.iloc[0, 1])
        inicio = 2
        fim = inicio + 1
        self.cap = np.array(df.iloc[inicio:fim, 0].astype(float), dtype=int)
        inicio, fim = fim, fim + self.nitems
        self.vt = np.array(df.iloc[inicio:fim, 0].astype(float), dtype=int)
        self.hc = context.custo_estoque * np.array(df.iloc[inicio:fim, 1].astype(float), dtype=float)
        self.hc = self.hc * 100
        self.st = np.array(df.iloc[inicio:fim, 2].astype(float), dtype=int)
        self.sc = context.custo_setup * np.array(df.iloc[inicio:fim, 3].astype(float), dtype=int)
        inicio, fim = fim, fim + self.nperiodos
        if self.nitems <= 15:
            self._d_no_sorted = np.array(df.iloc[inicio:fim, :].astype(float), dtype=int).T
        else:
            demanda_sup = np.array(df.iloc[inicio:fim, :].astype(float), dtype=int)
            inicio, fim = fim, fim + self.nperiodos
            demanda_inf = np.array(
                df.iloc[inicio:fim, :]
                .replace("\r", np.nan)
                .dropna(axis=1)
                .astype(float),
                dtype=int,
            )
            self._d_no_sorted = np.append(demanda_sup, demanda_inf, axis=1).T
        if sort_index:
            self._sort_index()
        else:
            self.d = self._d_no_sorted

    def _sort_index(self):
        sorted_indices = sorted(range(len(self.st)), key=lambda i: self.st[i], reverse=True)
        # Ordenar o vetor st em ordem decrescente e os demais vetores de acordo com a ordem dos itens
        self.st = np.array([self.st[i] for i in sorted_indices]) 
        self.vt = np.array([self.vt[i] for i in sorted_indices])
        self.hc = np.array([self.hc[i] for i in sorted_indices])
        self.sc = np.array([self.sc[i] for i in sorted_indices])
        self.d = np.array([self._d_no_sorted[i] for i in sorted_indices])

    def __str__(self) -> str:
        return f"{self.instance}_cap_{self.cap[0]}".replace(".dat", "").replace(".DAT", "")

    def _detect_delimiter(self) -> str:
        with open(self._instance) as f:
            line_splitted = re.split("\t", f.readline())
        if len(line_splitted) > 1:
            return "\t"
        else:
            return r"\s+"

    def _generate_cols(self, sep: str) -> list:
        with open(self._instance, "r", encoding="utf-8") as temp_f:
            col_count = [len(re.split(sep, l.strip())) for l in temp_f.readlines()]
        column_names = [i for i in range(max(col_count))]
        return column_names


@dataclass
class dataCS(LerDados):
    vc: np.array
    cs: Dict
    r: int

    def __init__(self, context: ProjectContext, instance: str, r: int, original_capacity: bool = False, sort_index: bool = False):
        super().__init__(context, instance, sort_index = sort_index)
        self._create_vc_cs()
        self.r = r
        if not original_capacity:
            self.original_cap = self.cap
            self.cap = self._lot_sizing_capacity()

    def __str__(self) -> str:
        return f"{super().__str__()}_nmaq_{self.r}"

    def _create_vc_cs(self):
        self.vc = np.zeros((self.nitems, self.nperiodos))
        self.cs = np.zeros((self.nitems, self.nperiodos, self.nperiodos))
        for i in range(self.nitems):
            for t in range(self.nperiodos):
                for k in range(self.nperiodos):
                    self.cs[i, t, k] = (
                        self.vc[i, t] + sum(self.hc[i] for u in range(t, k))
                    ) * self.d[i, k]

    def _lot_sizing_capacity(self):
        return np.array(
            [
                int(
                    np.ceil(
                        (self.vt[:, np.newaxis] * self.d + self.st[:, np.newaxis])
                        .sum(axis=0)
                        .max()
                    )
                )
            ]
        )


if __name__ == "__main__":
    context = ProjectContext(f"experimentos/experimento1.yml", 1)
    ler = LerDados(context,"X11117A.dat", sort_index = True)
    data = dataCS(context,"X11117A.dat", r=2)
    pass
    
