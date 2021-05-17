GEN_DIR=${PWD}/../proto/ecotaxa-cli/gen
mkdir ../stubs/ecotaxa-cli/gen
docker run --rm --network="host" -u $(id -u ${USER}):$(id -g ${USER}) \
-v $GEN_DIR:/gen \
openapitools/openapi-generator-cli:v5.1.1 generate \
-i https://ecotaxa.obs-vlfr.fr/api/openapi.json -g typescript-axios \
--additional-properties=generateSourceCodeOnly=true -o /gen
# Patch base.ts as the full URL make CORS issues in dev mode
sed -i "s/https:\/\/ecotaxa.obs-vlfr.fr//" $GEN_DIR/base.ts
