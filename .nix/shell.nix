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
  ];

  shellHook = ''
    export HF_HOME="$PWD/.cache/huggingface"
    export HF_HUB_CACHE="$PWD/.cache/huggingface/hub"
  '';
}