{ pkgs ? import <nixpkgs> {
  config = {
    allowUnfree = true;
    cudaSupport = true;
  };
} }:
let 
  lib-path = with pkgs; lib.makeLibraryPath [
    libffi
    openssl
    stdenv.cc.cc
  ];
in 
pkgs.mkShell {
  packages = with pkgs; [
    python3

    python3Packages.huggingface-hub
    
    # openevolve dependencies
    python3Packages.openai
    python3Packages.pyyaml
    python3Packages.numpy
    python3Packages.tqdm
    python3Packages.flask
    python3Packages.nltk
    python3Packages.datasets
    python3Packages.dacite
    python3Packages.evaluate

    # other dependencies
    python3Packages.scipy
    python3Packages.deap

    # venv
    python3Packages.venvShellHook
    python3Packages.pip
  ];

  shellHook = ''
    SOURCE_DATE_EPOCH=$(date +%s)
    export "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${lib-path}"
    VENV=.venv

    if test ! -d $VENV; then
      python -m venv $VENV
    fi
    source ./$VENV/bin/activate
    export PYTHONPATH=`pwd`/$VENV/${pkgs.python3.sitePackages}/:$PYTHONPATH
    pip install -r requirements.txt

    export HF_HOME="$PWD/.cache/huggingface"
    export HF_HUB_CACHE="$PWD/.cache/huggingface/hub"
    export WEBNLG_BASE_PATH="$PWD/../problems/triples_to_text/tests/webnlg/release_v3.0/en"

    export PYTHONPATH=`pwd`/../openevolve/:`pwd`/../problems/triples_to_text/tests/benchmark_reader/:$PYTHONPATH
  '';

  postShellHook = ''
    ln -sf ${pkgs.python3.sitePackages}/* ./.venv/lib/python${pkgs.python3.version}/site-packages
  '';
}