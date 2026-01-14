{ pkgs ? import <nixpkgs> {} }:
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
  ];

  shellHook = ''
    export HF_HOME="$PWD/.cache/huggingface"
    export HF_HUB_CACHE="$PWD/.cache/huggingface/hub"
    export WEBNLG_BASE_PATH="$PWD/../problems/triples_to_text/tests/webnlg/release_v3.0/en"

    export PYTHONPATH=`pwd`/../openevolve/:$PYTHONPATH
  '';
}