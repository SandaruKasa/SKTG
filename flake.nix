{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-compat.url = "github:edolstra/flake-compat/v1.0.1";
    pre-commit-hooks-nix = {
      url = "github:cachix/pre-commit-hooks.nix";
      inputs = {
        flake-compat.follows = "flake-compat";
        nixpkgs.follows = "nixpkgs";
        nixpkgs-stable.follows = "nixpkgs";
      };
    };
  };

  outputs = inputs@{ nixpkgs, flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [ inputs.pre-commit-hooks-nix.flakeModule ];

      systems = [ "x86_64-linux" "aarch64-linux" ];

      perSystem = { pkgs, config, self', ... }:
        let
          python = pkgs.python311;

          allOf = selectors: pkgs:
            builtins.concatMap (selector: selector pkgs) selectors;

          distPythonPkgs = pypkgs:
            with pypkgs;
            [
              # TODO
            ];

          devPythonPkgs = pypkgs:
            with pypkgs; [
              black
              isort
              # pleasing PyCharm:
              setuptools
            ];

        in {
          packages = {
            # TODO

            devPython =
              python.withPackages (allOf [ distPythonPkgs devPythonPkgs ]);
          };

          devShells.default = pkgs.mkShellNoCC {
            inherit (config.pre-commit.devShell) shellHook;
            packages = with pkgs; [ self'.packages.devPython nixfmt statix ];
            env = { LOGLEVEL = "DEBUG"; };
          };

          pre-commit.settings = {
            hooks = {
              black.enable = true;
              isort.enable = true;
              nixfmt.enable = true;
              statix.enable = true;
            };

            settings = { isort.profile = "black"; };
          };

          formatter = pkgs.nixfmt;
        };
    };
}
