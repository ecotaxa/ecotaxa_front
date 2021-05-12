set -x

# TODO : take a parameter $1
# rm `echo "$1" | cut -f 1 -d '.'`.js
rm -f AboutProject.js
# Super strict at the beginning, will adapt if necessary...

`tsc AboutProject.ts \
--alwaysStrict \
--declaration  \
--forceConsistentCasingInFileNames \
--noImplicitAny \
--noErrorTruncation \
--noFallthroughCasesInSwitch \
--noImplicitReturns \
--noImplicitThis \
--noUnusedLocals \
--noUnusedParameters \
--pretty \
--strict \
--strictFunctionTypes \
--strictNullChecks \
--types \
--strictPropertyInitialization \
`

set +x
