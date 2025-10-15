{ pkgs ? import <nixpkgs> {} }:
let
  packageOverrides = pkgs.callPackage ./python-packages.nix { };
  pythonCustom = pkgs.python3.override { inherit packageOverrides; };
in 
pkgs.mkShell {
  packages = with pkgs; [
    python3

    (pythonCustom.withPackages(p: [ p.openevolve ]))
  ];
}