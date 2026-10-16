{
  description = "Elysola 图标构建环境";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.uv
            pkgs.cairo
            pkgs.librsvg
            pkgs.potrace
            pkgs.imagemagick
          ];

          shellHook = ''
            export LD_LIBRARY_PATH="${pkgs.cairo}/lib:$LD_LIBRARY_PATH"
            uv sync
          '';
        };
      });
}
