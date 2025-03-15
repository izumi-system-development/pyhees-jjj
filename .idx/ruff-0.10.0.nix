{
  lib,
  fetchzip,
  stdenv,
  installShellFiles,
  versionCheckHook,
}:

stdenv.mkDerivation (finalAttrs: 
let
  version = "0.10.0";
in
{
  pname = "ruff";
  version = version;

  src = fetchzip {
    url = "https://github.com/astral-sh/ruff/releases/download/${version}/ruff-x86_64-unknown-linux-gnu.tar.gz";
    hash = "sha256-Xu2xjYexroAGyzMCDp1OFMLD4MZyLDudAOQG4QB73bw=";
  };

  nativeBuildInputs = [ installShellFiles ];

  installPhase = ''
    mkdir -p $out/bin
    cp $src/ruff $out/bin # 実行ファイルを適切な場所にコピー
  '';

  postInstall =
    lib.optionalString (stdenv.buildPlatform.canExecute stdenv.hostPlatform) ''
      installShellCompletion --cmd ruff \
        --bash <($bin/bin/ruff generate-shell-completion bash) \
        --fish <($bin/bin/ruff generate-shell-completion fish) \
        --zsh <($bin/bin/ruff generate-shell-completion zsh)
    '';

  nativeCheckInputs = [
    versionCheckHook
  ];

  versionCheckProgramArg = [ "--version" ];

  meta = {
    description = "Extremely fast Python linter";
    homepage = "https://github.com/astral-sh/ruff";
    changelog = "https://github.com/astral-sh/ruff/releases/tag/${version}";
    license = lib.licenses.mit;
    mainProgram = "ruff";
    maintainers = ["Yusuke Arai"];
  };
})