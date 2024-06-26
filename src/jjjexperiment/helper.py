def check_variable_undefined(var_name):
    """変数が未定義であることを確認します"""
    if var_name in locals() or var_name in globals():
        raise AssertionError(f"Variable '{var_name}' is already defined.")
    else:
        print(f"Variable '{var_name}' is not defined.")
