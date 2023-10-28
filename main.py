from utils import (
    running_all_instance_choose_capacity,
    running_all_instance_with_chosen_capacity,
)
from zero_formulation import build_model as classical_formulation_build_model
from first_formulation import build_model as first_reformulation_build_model
from second_formulation import build_model as second_reformulation_build_model
from third_formulation import build_model as third_reformulation_build_model
from fourth_formulation import build_model as fourth_reformulation_build_model

if __name__ == "__main__":
    # running_all_instance_with_chosen_capacity(
    #     classical_formulation_build_model,
    #     path_to_save="otimizados0.xlsx",
    #     env_formulation="0st_ref",
    # )
    running_all_instance_with_chosen_capacity(
        first_reformulation_build_model,
        path_to_save="otimizados1.xlsx",
        env_formulation="1st_ref",
    )
    running_all_instance_with_chosen_capacity(
        second_reformulation_build_model,
        path_to_save="otimizados2.xlsx",
        env_formulation="2nd_ref",
    )
    running_all_instance_with_chosen_capacity(
        third_reformulation_build_model,
        path_to_save="otimizados3.xlsx",
        env_formulation="3nd_ref",
    )
    # running_all_instance_with_chosen_capacity(
    #     fourth_reformulation_build_model,
    #     path_to_save="otimizados4.xlsx",
    #     env_formulation="4nd_ref",
    # )
