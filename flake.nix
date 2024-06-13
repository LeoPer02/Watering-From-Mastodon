{
    description = "Arduino";

    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
	};

    outputs = { self, ... } @ inputs: 
    let
        pkgs = import inputs.nixpkgs { inherit system; };
        ROOT = let p = builtins.getEnv "PWD"; in if p == "" then self else p;
        name = "Arduino";
        system = "x86_64-linux";
        mqtt-explorer= pkgs.symlinkJoin {
            name = "mqtt-explorer";
            paths = [ pkgs.appimage-run ];
            buildInputs = [ pkgs.makeWrapper ];
            postBuild = ''
                mv $out/bin/appimage-run $out/bin/mqtt-explorer
                wrapProgram $out/bin/mqtt-explorer --add-flags "./mqtt-explorer.AppImage"
            '';
        };
    in {
        devShells."${system}".default = pkgs.mkShell {
            inherit name ROOT;

            buildInputs = with pkgs; [
                arduino-ide python3
                docker
                mqtt-explorer
            ];

            shellHook = '''';

        };
    };
}
