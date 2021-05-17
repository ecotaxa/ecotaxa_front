Code generation & dev tools used in EcoTaxa front.

###### To check the tools versions:

$ node --version

v12.19.0


$ npm --version

6.14.8


$ docker --version

Docker version 20.10.2, build 20.10.2-0ubuntu1~18.04.2

###### Generating the API entry point in TS:

The generated files are committed in `git`, but in case/when the API changes, there will be a need for refreshing the generated code:

$ pushd ../tools

$ ./generate.sh

$ popd

This will generate the Typescript API entry points in proto/gen.

###### Setting up the environment:

$ cd ecotaxa-cli

$ npm install

###### Launch Visual Studio Code IDE:

$ code .

If you launch "serve" npm task then, after a while, you should be able to connect to local dev server at http://localhost:8080/