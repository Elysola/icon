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
            pkgs.ruff
            pkgs.black
            pkgs.cairo
            pkgs.librsvg
            pkgs.fontconfig
            pkgs.dejavu_fonts
            pkgs.potrace
            pkgs.imagemagick
          ];

          shellHook = ''
            export LD_LIBRARY_PATH="${pkgs.cairo}/lib:$LD_LIBRARY_PATH"
            export ELY_FONTCONFIG_FILE="$PWD/.fontconfig-elysola.conf"
            cat > "$ELY_FONTCONFIG_FILE" <<'FONTCONFIG'
            <?xml version="1.0"?>
            <!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
            <fontconfig>
              <dir>${pkgs.dejavu_fonts}/share/fonts/truetype</dir>
              <cachedir prefix="xdg">fontconfig</cachedir>
              <selectfont><rejectfont><glob>*/MapleMono-*</glob></rejectfont></selectfont>
              <match target="pattern">
                <test name="family" qual="any"><string>DejaVu Sans</string></test>
                <edit name="family" mode="assign" binding="strong"><string>DejaVu Sans</string></edit>
              </match>
            </fontconfig>
            FONTCONFIG
            export FONTCONFIG_FILE="$ELY_FONTCONFIG_FILE"
            uv sync
          '';
        };
      });
}
