set -x

# TODO : take a parameter $1
rm -f AboutProject.js
# Super strict at the beginning, will adapt if necessary...

`tsc AboutProject.ts --outfile AboutProject.js \
--alwaysStrict \
--declaration  \
--forceConsistentCasingInFileNames \
--noImplicitAny \
--noErrorTruncation \
--noFallthroughCasesInSwitch \
--noImplicitAny \
--noImplicitReturns \
--noImplicitThis \
--noUnusedLocals \
--noUnusedParameters \
--pretty \
--strict \
--strictFunctionTypes \
--strictNullChecks \
--strictPropertyInitialization \
`

set +x
