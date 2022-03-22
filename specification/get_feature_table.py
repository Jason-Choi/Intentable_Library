from pandas import DataFrame
from typing import Dict, List


def get_feature_table(table: DataFrame, is_column : int, axis_type: str) -> DataFrame:
    aggregate_functions: List[str] = [
                                    'idxmax',
                                    'idxmin',
                                    'max',
                                    'min',
                                    # 'mean',
                                    # 'median',
                                    'sum'
                                    ]
    aggregated_table: List[DataFrame] = []

    for aggregate_function in aggregate_functions:
        aggregated_table.append(
            eval(f"table.{aggregate_function}(axis={is_column}).tolist()")
        )
    if is_column == 0 and axis_type == "DATE":

        aggregate_functions.insert(0, "NAMEMOSTPAST")
        aggregated_table.insert(0, table.index.tolist()[0])
        
        aggregate_functions.insert(0, "ENTITYMOSTPAST")
        aggregated_table.insert(0,table.iloc[0].tolist())

        aggregate_functions.insert(0, "NAMEMOSTRECENT")
        aggregated_table.insert(0, table.index.tolist()[-1])

        aggregate_functions.insert(0, "ENTITYMOSTRECENT")
        aggregated_table.insert(0,table.iloc[-1].tolist())
    
    elif is_column == 1 and axis_type == "DATE":
        aggregate_functions.insert(0, "NAMEMOSTPAST")
        aggregated_table.insert(0, table.columns.tolist()[0])

        aggregate_functions.insert(0, "ENTITYMOSTPAST")
        aggregated_table.insert(0, table.iloc[:, 0].tolist())

        aggregate_functions.insert(0, "NAMEMOSTRECENT")
        aggregated_table.insert(0, table.columns.tolist()[-1])

        aggregate_functions.insert(0, "ENTITYMOSTRECENT")
        aggregated_table.insert(0, table.iloc[:, -1].tolist())


    output = {aggregate_functions[i].lower().replace("idx", "name"): aggregated_table[i] for i in range(len(aggregate_functions))}
    output_list = {}
    for function_name, entity_table in output.items():
        
        if type(entity_table) != type([]):
            output_list[f"<{function_name}>"] = entity_table
        else:
            for i in range(len(entity_table)):
                output_list[f"<{function_name}> <{i}>"] = entity_table[i]
    return output_list

