def check_variable_undefined(var_name) -> None:
    """
        変数が未定義、よって使用されていないことから、関係するロジックがないことを確認します

        Args:
            var_name: 定義済みか確認したい変数名

    """
    if var_name in locals() or var_name in globals():
        raise AssertionError(f"Variable '{var_name}' is already defined.")
    else:
        # print(f"Variable '{var_name}' is not defined.")
        pass
