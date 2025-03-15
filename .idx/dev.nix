# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, lib, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.11"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python311
    (let ruff = pkgs.callPackage ./ruff-0.10.0.nix {}; in ruff)
    pkgs.poetry
    # for libraries written in C/C++ such as numpy and pandas, installed by poetry
    pkgs.libz
    pkgs.gcc
    pkgs.nix-ld
  ];

  # Sets environment variables in the workspace
  env = {
    # for libraries written in C/C++ such as numpy and pandas, installed by poetry
    NIX_LD_LIBRARY_PATH = lib.makeLibraryPath [
      pkgs.stdenv.cc.cc
      pkgs.libz
      pkgs.gcc
    ];
  };
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "vscodevim.vim"
      "ms-python.debugpy"
      "ms-python.python"
      "charliermarsh.ruff"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        # web = {
        #   # Example: run "npm run dev" with PORT set to IDX's defined port for previews,
        #   # and show it in IDX's web preview panel
        #   command = ["npm" "run" "dev"];
        #   manager = "web";
        #   env = {
        #     # Environment variables to set for your server
        #     PORT = "$PORT";
        #   };
        # };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        poetry-install = "poetry install";
      };
      # Runs when the workspace is (re)started
      onStart = {
      };
    };
  };
}
